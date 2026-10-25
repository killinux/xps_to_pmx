"""Execute a :class:`~xps_to_pmx.core.rig.skeleton.SkeletonPlan` on the armature (stage ④, no decisions here).

* bones: rename (via temporary names, so swaps cannot collide), create, delete
  the bones that were merged, then set parent / head / tail / roll exactly as planned;
* weights: rewrite every vertex whose influences differ from the plan (bmesh
  deform layer; custom split normals are restored afterwards, shape keys are
  untouched) and drop vertex groups of bones that no longer exist.
"""
from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from ..core.rig.skeleton import SkeletonPlan
from . import rigedit
from .importer import PROP_SRC

PROP_SLOT = "xps2pmx_slot"
TEMP_PREFIX = "__x2p_tmp_"


def apply_bones(context: bpy.types.Context, arm_obj: bpy.types.Object, plan: SkeletonPlan) -> Dict[str, int]:
    keep_sources = {b.source for b in plan.bones if b.source}
    with rigedit.edit_mode(context, arm_obj):
        ebs = arm_obj.data.edit_bones
        doomed = [eb.name for eb in ebs if eb.name not in keep_sources]
        # children of doomed bones are re-parented below anyway; remove the doomed bones first
        for name in doomed:
            eb = ebs.get(name)
            if eb is not None:
                for child in eb.children:
                    child.use_connect = False
                ebs.remove(eb)
        renames = [(b.source, b.name) for b in plan.bones if b.source and b.source != b.name]
        for k, (src, _) in enumerate(renames):
            ebs[src].name = f"{TEMP_PREFIX}{k:04d}"
        for k, (_, dst) in enumerate(renames):
            ebs[f"{TEMP_PREFIX}{k:04d}"].name = dst
        created = 0
        for b in plan.bones:
            if b.created:
                eb = ebs.new(b.name)
                eb.head, eb.tail = Vector(b.head), Vector(b.tail)
                eb.roll = 0.0
                created += 1
        for b in plan.bones:
            eb = ebs[b.name]
            eb.use_connect = False
            eb.parent = ebs[b.parent] if b.parent else None
            if (np.abs(np.array(eb.head) - b.head).max() > 1e-7 or np.abs(np.array(eb.tail) - b.tail).max() > 1e-7):
                eb.head, eb.tail = Vector(b.head), Vector(b.tail)
        for b in plan.bones:
            if b.roll_like:
                ebs[b.name].roll = ebs[b.roll_like].roll
    bones = arm_obj.data.bones
    for b in plan.bones:
        bone = bones[b.name]
        if b.slot_id:
            bone[PROP_SLOT] = b.slot_id
        elif PROP_SLOT in bone:
            del bone[PROP_SLOT]
        if b.created and PROP_SRC in bone:
            del bone[PROP_SRC]
        bone.use_deform = b.deform
    return {"renamed": len(renames), "created": created, "deleted": len(doomed)}


def _mesh_slices(plan_rows: int, slices: Sequence[Tuple[str, int, int]]) -> List[Tuple[bpy.types.Object, int, int]]:
    out = []
    for name, start, end in slices:
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH' or len(obj.data.vertices) != end - start:
            raise RuntimeError(f"mesh {name} changed since the snapshot (stage ④ must run on the snapshot it planned)")
        out.append((obj, start, end))
    if slices and slices[-1][2] != plan_rows:
        raise RuntimeError("snapshot rows and plan rows differ")
    return out


def apply_weights(plan: SkeletonPlan, slices: Sequence[Tuple[str, int, int]], tol: float = 1e-5) -> Dict[str, int]:
    """Write the planned weights; returns counts of rewritten vertices / removed groups."""
    if plan.skin_bones is None:
        return {"vertices": 0, "groups_removed": 0}
    names = [b.name for b in plan.bones]
    bone_names = set(names)
    rewritten = removed = 0
    for obj, start, end in _mesh_slices(plan.skin_bones.shape[0], slices):
        nb = plan.skin_bones[start:end]
        nw = plan.skin_weights[start:end]
        me = obj.data
        used = sorted({int(i) for i in np.unique(nb) if i >= 0})
        for i in used:
            if names[i] not in obj.vertex_groups:
                obj.vertex_groups.new(name=names[i])
        group_of = {vg.name: vg.index for vg in obj.vertex_groups}
        bone_group = {vg.index for vg in obj.vertex_groups if vg.name in bone_names}
        stale_groups = {vg.index for vg in obj.vertex_groups if vg.name not in bone_names and _is_bone_group(vg.name)}
        target_index = [group_of.get(n, -1) for n in names]
        normals = None
        changed = 0
        bm = bmesh.new()
        try:
            bm.from_mesh(me)
            layer = bm.verts.layers.deform.verify()
            bm.verts.ensure_lookup_table()
            nb_list, nw_list = nb.tolist(), nw.tolist()
            for v, row_b, row_w in zip(bm.verts, nb_list, nw_list):
                dv = v[layer]
                want = {target_index[b]: w for b, w in zip(row_b, row_w) if b >= 0 and w > 0}
                have = {g: w for g, w in dv.items() if g in bone_group or g in stale_groups}
                if have.keys() == want.keys() and all(abs(have[g] - want[g]) <= tol for g in want):
                    continue
                for g in have:
                    del dv[g]
                for g, w in want.items():
                    dv[g] = w
                changed += 1
            if changed:
                if len(me.loops):
                    normals = rigedit.loop_normals(me)
                bm.to_mesh(me)
        finally:
            bm.free()
        if normals is not None:
            rigedit.set_loop_normals(me, normals)
            me.update()
        for vg in list(obj.vertex_groups):
            if vg.index in stale_groups:
                obj.vertex_groups.remove(vg)
                removed += 1
        rewritten += changed
    return {"vertices": rewritten, "groups_removed": removed}


def _is_bone_group(name: str) -> bool:
    """Vertex groups we own (bone groups); mmd_tools' helper groups are left alone."""
    return not name.startswith("mmd_")
