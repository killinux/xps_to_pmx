"""bpy helpers for stage ③: merge vertex groups, delete bones, apply rigid rest-pose edits.

``transform_rig`` changes the *rest* state directly: edit bones get the bone
transforms and every mesh vertex (basis and all shape keys) gets the linear
blend of them, so no pose has to be applied and no modifier is applied
(shape keys stay intact).  Custom split normals are rotated the same way.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Set

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

from ..core.pose import blend_directions, blend_matrices, blend_points


# ---------------------------------------------------------------------------
# array access

def get_coords(collection, n: int) -> np.ndarray:
    arr = np.empty(n * 3, dtype=np.float32)
    collection.foreach_get("co", arr)
    return arr.reshape(-1, 3).astype(np.float64)


def set_coords(collection, coords: np.ndarray) -> None:
    collection.foreach_set("co", np.asarray(coords, dtype=np.float32).reshape(-1))


def loop_normals(me: bpy.types.Mesh) -> np.ndarray:
    me.calc_normals_split()
    arr = np.empty(len(me.loops) * 3, dtype=np.float32)
    me.loops.foreach_get("normal", arr)
    return arr.reshape(-1, 3).astype(np.float64)


def set_loop_normals(me: bpy.types.Mesh, normals: np.ndarray) -> None:
    if not len(me.loops):
        return
    me.use_auto_smooth = True
    me.normals_split_custom_set([tuple(n) for n in normals])


def loop_vertices(me: bpy.types.Mesh) -> np.ndarray:
    arr = np.empty(len(me.loops), dtype=np.int32)
    me.loops.foreach_get("vertex_index", arr)
    return arr


def mesh_skin(obj: bpy.types.Object, bone_index: Dict[str, int]):
    """Top-4 (bone index, weight) arrays of one mesh; bone indices refer to ``bone_index``."""
    me = obj.data
    n = len(me.vertices)
    group_bone = {vg.index: bone_index.get(vg.name, -1) for vg in obj.vertex_groups}
    bones = np.full((n, 4), -1, dtype=np.int32)
    weights = np.zeros((n, 4), dtype=np.float32)
    for i, v in enumerate(me.vertices):
        pairs = [(group_bone.get(g.group, -1), g.weight) for g in v.groups if g.weight > 0]
        pairs = [p for p in pairs if p[0] >= 0]
        if len(pairs) > 4:
            pairs.sort(key=lambda p: -p[1])
            pairs = pairs[:4]
        for k, (b, w) in enumerate(pairs):
            bones[i, k] = b
            weights[i, k] = w
    return bones, weights


# ---------------------------------------------------------------------------
# weights and bones

def merge_vertex_groups(obj: bpy.types.Object, merges: Dict[str, str]) -> int:
    """Add each source group's weights into its target group, then remove the source group."""
    vg_index = {vg.name: vg.index for vg in obj.vertex_groups}
    pairs = {s: t for s, t in merges.items() if s in vg_index and s != t}
    if not pairs:
        return 0
    for target in set(pairs.values()):
        if target not in vg_index:
            vg_index[target] = obj.vertex_groups.new(name=target).index
    src_to_tgt = {vg_index[s]: vg_index[t] for s, t in pairs.items()}
    me = obj.data
    normals = loop_normals(me) if len(me.loops) else None
    bm = bmesh.new()
    try:
        bm.from_mesh(me)
        layer = bm.verts.layers.deform.verify()
        for v in bm.verts:
            dv = v[layer]
            for s, t in src_to_tgt.items():
                if s in dv:
                    w = dv[s]
                    del dv[s]
                    dv[t] = dv.get(t, 0.0) + w
        bm.to_mesh(me)
    finally:
        bm.free()
    if normals is not None:
        set_loop_normals(me, normals)
    for name in pairs:
        vg = obj.vertex_groups.get(name)
        if vg is not None:
            obj.vertex_groups.remove(vg)
    me.update()
    return len(pairs)


def delete_bones(context: bpy.types.Context, arm_obj: bpy.types.Object, names: Iterable[str],
                 meshes: Sequence[bpy.types.Object]) -> List[str]:
    """Delete bones; children are re-parented to the nearest surviving ancestor. Returns deleted names."""
    doomed: Set[str] = {n for n in names if n in arm_obj.data.bones}
    if not doomed:
        return []
    with edit_mode(context, arm_obj):
        ebs = arm_obj.data.edit_bones

        def survivor(eb):
            p = eb.parent
            while p is not None and p.name in doomed:
                p = p.parent
            return p

        for eb in list(ebs):
            if eb.name not in doomed and eb.parent is not None and eb.parent.name in doomed:
                eb.use_connect = False
                eb.parent = survivor(eb)
        for name in doomed:
            eb = ebs.get(name)
            if eb is not None:
                ebs.remove(eb)
    for obj in meshes:
        for name in doomed:
            vg = obj.vertex_groups.get(name)
            if vg is not None:
                obj.vertex_groups.remove(vg)
    return sorted(doomed)


class edit_mode:
    """Enter edit mode on ``arm_obj`` and restore object mode afterwards."""

    def __init__(self, context: bpy.types.Context, arm_obj: bpy.types.Object):
        self.context = context
        self.arm = arm_obj

    def __enter__(self):
        ctx = self.context
        if ctx.view_layer.objects.active is not None and ctx.view_layer.objects.active.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        for obj in ctx.view_layer.objects:
            obj.select_set(False)
        self.arm.hide_set(False)
        self.arm.select_set(True)
        ctx.view_layer.objects.active = self.arm
        bpy.ops.object.mode_set(mode='EDIT')
        return self

    def __exit__(self, *exc):
        bpy.ops.object.mode_set(mode='OBJECT')
        return False


# ---------------------------------------------------------------------------
# rigid rest edits

def _decompose(m: np.ndarray):
    lin = m[:3, :3]
    scale = float(np.cbrt(np.linalg.det(lin)))
    rot = lin / scale if abs(scale) > 1e-12 else np.eye(3)
    return scale, rot


def transform_rig(context: bpy.types.Context, arm_obj: bpy.types.Object, meshes: Sequence[bpy.types.Object],
                  bone_transforms: Optional[Dict[str, np.ndarray]] = None,
                  global_matrix: Optional[np.ndarray] = None) -> None:
    """Apply per-bone rigid transforms (blended on the skin) and/or one global similarity transform.

    Both are given in armature space.  The rest pose itself changes; meshes are
    assumed to be parented to the armature without an offset.
    """
    bone_transforms = bone_transforms or {}
    names = [b.name for b in arm_obj.data.bones]
    index = {n: i for i, n in enumerate(names)}
    per_bone = {index[n]: m for n, m in bone_transforms.items() if n in index}
    g = global_matrix if global_matrix is not None else np.eye(4)

    for obj in meshes:
        me = obj.data
        n = len(me.vertices)
        if not n:
            continue
        if per_bone:
            bones, weights = mesh_skin(obj, index)
            mats = blend_matrices(bones, weights, per_bone)
        else:
            mats = np.repeat(np.eye(4)[None], n, axis=0)
        mats = np.einsum("ij,njk->nik", g, mats)
        normals = loop_normals(me) if len(me.loops) else None
        if me.shape_keys is not None:
            for kb in me.shape_keys.key_blocks:
                set_coords(kb.data, blend_points(get_coords(kb.data, n), mats))
        set_coords(me.vertices, blend_points(get_coords(me.vertices, n), mats))
        # custom normals are encoded relative to the face normals: refresh those first
        me.update()
        if normals is not None:
            set_loop_normals(me, blend_directions(normals, mats[loop_vertices(me)]))
        me.update()

    with edit_mode(context, arm_obj):
        ebs = arm_obj.data.edit_bones
        originals = {eb.name: (eb.matrix.copy(), eb.length) for eb in ebs}
        for eb in ebs:
            m = g @ per_bone.get(index.get(eb.name, -1), np.eye(4))
            if np.allclose(m, np.eye(4), atol=1e-12):
                continue
            mat, length = originals[eb.name]
            scale, rot = _decompose(m)
            head = np.array(mat.translation)
            new_head = m[:3, :3] @ head + m[:3, 3]
            new = Matrix(rot) @ mat.to_3x3()
            full = new.to_4x4()
            full.translation = Vector(new_head)
            eb.matrix = full
            eb.length = length * abs(scale)


def edit_bone_head(context, arm_obj, name: str, head: Sequence[float]) -> None:
    """Move one bone head (tail kept) -- used for bone-only normalisation such as levelling 肩."""
    with edit_mode(context, arm_obj):
        eb = arm_obj.data.edit_bones.get(name)
        if eb is not None:
            eb.use_connect = False
            eb.head = Vector(head)
