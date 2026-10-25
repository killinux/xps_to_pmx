"""The only module that imports mmd_tools (design doc §3.4).  Written against mmd_tools 1.0.2.

Every call follows the behaviour measured in research note 08:

* ``Model.create(..., armature=arm)`` adopts the armature (keyword ``armature``);
* bone order = vertex-group order of the mesh carrying the
  ``mmd_bone_order_override`` modifier (a zero-vertex helper mesh); ``bone_id``
  is written too, *before* the 付与 targets;
* 付与 is exported from ``mmd_bone`` only; the target setter silently stores −1
  for unknown names, so every target is read back;
* the IK representation copies the PMX importer (constraint on the target's
  parent, iterations = loop, unit angle on the constraint bone, knee limits via
  ``PMXImporter.convertIKLimitAngles`` + ``mmd_ik_limit_override``);
* material fields are written as ID properties so the HD node tree is not
  rewired to ``mmd_shader``;
* export is the plain ``exporter.export`` function with ``scale`` passed
  explicitly and the armature switched to REST around it.
"""
from __future__ import annotations

import importlib
import math
import os
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import addon_utils
import bpy
import numpy as np
from mathutils import Vector

from ..core.pose import EXPORT_SCALE
from ..core.rig.skeleton import PlannedBone, SkeletonPlan

MODULE = "mmd_tools"
SUPPORTED = ((1, 0, 2),)
BONE_ORDER_MESH = "000_mmd_bone_order"
BONE_ORDER_MODIFIER = "mmd_bone_order_override"
#: Display frames in panel order (design doc §8.3); English names as written to the PMX.
FRAMES: Tuple[Tuple[str, str], ...] = (
    ("センター", "center"), ("ＩＫ", "IK"), ("体(上)", "upper body"), ("腕", "arms"), ("指", "fingers"),
    ("体(下)", "lower body"), ("足", "legs"), ("髪", "hair"), ("物理", "physics"), ("その他", "others"),
)
ROOT_FRAME = "Root"


class MMDToolsError(RuntimeError):
    pass


def ensure_mmd_tools():
    """Enable (if needed) and return the mmd_tools module; raises :class:`MMDToolsError` when unusable."""
    try:
        loaded_default, loaded_state = addon_utils.check(MODULE)
    except Exception:  # pragma: no cover - addon_utils internals
        loaded_state = False
    if not loaded_state:
        try:
            addon_utils.enable(MODULE, default_set=False, persistent=False)
        except Exception as exc:  # noqa: BLE001 - report any failure to the user
            raise MMDToolsError(f"无法启用 mmd_tools：{exc}") from exc
    try:
        mod = importlib.import_module(MODULE)
    except ImportError as exc:
        raise MMDToolsError("没有安装 mmd_tools（需要 Blender 3.6 自带的 1.0.2）") from exc
    if not hasattr(bpy.types.Object, "mmd_type"):
        raise MMDToolsError("mmd_tools 已导入但没有注册（Object.mmd_type 不存在）")
    return mod


def version() -> Tuple[int, ...]:
    mod = ensure_mmd_tools()
    return tuple(mod.bl_info.get("version", (0, 0, 0)))


def is_supported() -> bool:
    return version() in SUPPORTED


def _pmx(v: Sequence[float]) -> Tuple[float, float, float]:
    """Blender direction → PMX axes convention used by mmd_bone axis properties (.xzy)."""
    return float(v[0]), float(v[2]), float(v[1])


class ContextGuard:
    """Restore mode, active object and selection after mmd_tools calls that change them (note 08 Q13)."""

    def __init__(self, context: bpy.types.Context):
        self.context = context

    def __enter__(self):
        vl = self.context.view_layer
        self.active = vl.objects.active
        self.mode = self.active.mode if self.active is not None else 'OBJECT'
        self.selected = [o for o in vl.objects if o.select_get()]
        if self.active is not None and self.active.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        return self

    def __exit__(self, *exc):
        vl = self.context.view_layer
        if vl.objects.active is not None and vl.objects.active.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        for o in vl.objects:
            o.select_set(False)
        for o in self.selected:
            if o.name in vl.objects:
                o.select_set(True)
        if self.active is not None and self.active.name in vl.objects:
            vl.objects.active = self.active
        return False


# ---------------------------------------------------------------------------
# model

def find_root(obj: bpy.types.Object) -> Optional[bpy.types.Object]:
    ensure_mmd_tools()
    from mmd_tools.core.model import Model  # noqa: WPS433 (bridge-only import)
    return Model.findRoot(obj)


def create_model(context: bpy.types.Context, arm: bpy.types.Object, name_j: str, name_e: str,
                 collection: Optional[bpy.types.Collection]) -> bpy.types.Object:
    ensure_mmd_tools()
    from mmd_tools.core.model import Model
    with ContextGuard(context):
        rig = Model.create(name_j, name_e, scale=1.0 / EXPORT_SCALE, obj_name=f"{name_j}", armature=arm,
                           add_root_bone=False)
        root = rig.rootObject()
    if collection is not None:
        for coll in list(root.users_collection):
            if coll != collection:
                coll.objects.unlink(root)
        if root.name not in collection.objects:
            collection.objects.link(root)
    return root


def setup_bones(arm: bpy.types.Object, plan: SkeletonPlan) -> List[str]:
    """MMD bone properties, flags, bone_id and 付与 (read back).  Returns problems found."""
    ensure_mmd_tools()
    problems: List[str] = []
    arm.data.bones.active = None
    pbs = arm.pose.bones
    for i, b in enumerate(plan.bones):
        pb = pbs[b.name]
        mb = pb.mmd_bone
        mb.name_j = b.name
        mb.name_e = b.name_e
        mb.transform_order = int(b.transform_order)
        mb.is_controllable = bool(b.controllable)
        mb.bone_id = i
        pb.lock_location = [not b.movable] * 3
        pb.lock_rotation = [False] * 3
        pb.bone.hide = not b.visible
        if b.fixed_axis is not None:
            mb.enabled_fixed_axis = True
            mb.fixed_axis = _pmx(b.fixed_axis)
        else:
            mb.enabled_fixed_axis = False
        if b.local_x is not None and b.local_z is not None:
            mb.enabled_local_axes = True
            mb.local_axis_x = _pmx(b.local_x)
            mb.local_axis_z = _pmx(b.local_z)
        else:
            mb.enabled_local_axes = False
    for b in plan.bones:
        mb = pbs[b.name].mmd_bone
        if b.grant_parent:
            mb.has_additional_rotation = True
            mb.has_additional_location = False
            mb.additional_transform_influence = float(b.grant_rate)
            mb.additional_transform_bone = b.grant_parent
            if mb.additional_transform_bone != b.grant_parent:
                problems.append(f"{b.name}: 付与源 {b.grant_parent} 写入失败（读回 {mb.additional_transform_bone!r}）")
        else:
            mb.has_additional_rotation = False
            mb.has_additional_location = False
    return problems


def build_bone_order(arm: bpy.types.Object, plan: SkeletonPlan, collection: Optional[bpy.types.Collection]) \
        -> bpy.types.Object:
    """(Re)create the zero-vertex mesh whose vertex groups define the PMX bone order (note 08 Q3)."""
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH' and obj.parent == arm and BONE_ORDER_MODIFIER in obj.modifiers:
            me = obj.data
            bpy.data.objects.remove(obj)
            if me.users == 0:
                bpy.data.meshes.remove(me)
    for obj in arm.children:
        if obj.type == 'MESH':
            for mod in obj.modifiers:
                if mod.name == BONE_ORDER_MODIFIER:
                    mod.name = "Armature"
    me = bpy.data.meshes.new(BONE_ORDER_MESH)
    obj = bpy.data.objects.new(BONE_ORDER_MESH, me)
    (collection or bpy.context.scene.collection).objects.link(obj)
    obj.parent = arm
    for b in plan.bones:
        obj.vertex_groups.new(name=b.name)
    mod = obj.modifiers.new(BONE_ORDER_MODIFIER, 'ARMATURE')
    mod.object = arm
    obj.hide_render = True
    return obj


def setup_ik(arm: bpy.types.Object, plan: SkeletonPlan) -> List[str]:
    ensure_mmd_tools()
    from mmd_tools.core.pmx.importer import PMXImporter
    problems: List[str] = []
    pbs = arm.pose.bones
    for b in plan.bones:
        if b.ik is None:
            continue
        target = pbs[b.ik.target]
        chain0 = pbs[b.ik.links[0].bone]
        if target.parent != chain0:
            problems.append(f"{b.name}: IK 目标 {target.name} 的父骨不是链首 {chain0.name}")
            continue
        for c in list(chain0.constraints):
            if c.type == 'IK' and c.subtarget == b.name:
                chain0.constraints.remove(c)
        c = chain0.constraints.new('IK')
        c.name = "IK"
        c.target = arm
        c.subtarget = b.name
        c.chain_count = len(b.ik.links)
        c.iterations = int(b.ik.loop)
        c.use_tail = True
        chain0.mmd_bone.ik_rotation_constraint = float(b.ik.unit_angle)
        old = target.constraints.get("mmd_ik_target_override")
        if old is not None:
            target.constraints.remove(old)
        t = target.constraints.new('DAMPED_TRACK')
        t.name = "mmd_ik_target_override"
        t.mute = True
        t.influence = 0.0
        t.target = arm
        t.subtarget = chain0.name
        for link in b.ik.links:
            if link.limit_min is None:
                continue
            pb = pbs[link.bone]
            minimum, maximum = PMXImporter.convertIKLimitAngles(link.limit_min, link.limit_max, pb.bone.matrix_local)
            pb.use_ik_limit_x = pb.use_ik_limit_y = pb.use_ik_limit_z = True
            pb.ik_max_x, pb.ik_max_y, pb.ik_max_z = maximum
            pb.ik_min_x, pb.ik_min_y, pb.ik_min_z = minimum
            old = pb.constraints.get("mmd_ik_limit_override")
            if old is not None:
                pb.constraints.remove(old)
            lim = pb.constraints.new('LIMIT_ROTATION')
            lim.name = "mmd_ik_limit_override"
            lim.owner_space = 'POSE'
            lim.max_x, lim.max_y, lim.max_z = maximum
            lim.min_x, lim.min_y, lim.min_z = minimum
            lim.use_limit_x = pb.ik_max_x != lim.max_x or pb.ik_min_x != lim.min_x
            lim.use_limit_y = pb.ik_max_y != lim.max_y or pb.ik_min_y != lim.min_y
            lim.use_limit_z = pb.ik_max_z != lim.max_z or pb.ik_min_z != lim.min_z
    return problems


def apply_axes_and_grants(context: bpy.types.Context, arm: bpy.types.Object) -> None:
    """Sync rolls with the local axes, then build the 付与 preview constraints / shadow bones."""
    ensure_mmd_tools()
    from mmd_tools.core.bone import FnBone
    with ContextGuard(context):
        FnBone.apply_bone_local_axes(arm)
        FnBone.apply_additional_transformation(arm)


def setup_display_frames(root: bpy.types.Object, arm: bpy.types.Object, plan: SkeletonPlan) -> Dict[str, int]:
    ensure_mmd_tools()
    from mmd_tools.core.model import Model
    rig = Model(root)
    rig.initialDisplayFrames(reset=True)
    frames = root.mmd_root.display_item_frames
    root_frame = frames[ROOT_FRAME]
    root_frame.data.clear()
    by_frame: Dict[str, List[str]] = {}
    root_bone = next((b.name for b in plan.bones if b.display_frame == ROOT_FRAME), plan.bones[0].name)
    item = root_frame.data.add()
    item.type, item.name = 'BONE', root_bone
    for b in plan.bones:
        if not b.visible or not b.controllable or b.name == root_bone:
            continue
        frame = b.display_frame if b.display_frame in dict(FRAMES) else "その他"
        by_frame.setdefault(frame, []).append(b.name)
    counts = {}
    for name, name_e in FRAMES:
        names = by_frame.get(name)
        if not names:
            continue
        frame = frames.add()
        frame.name, frame.name_e = name, name_e
        for n in names:
            item = frame.data.add()
            item.type, item.name = 'BONE', n
        counts[name] = len(names)
    return counts


def set_model_info(root: bpy.types.Object, name_j: str, name_e: str, comment: str) -> None:
    mmd_root = root.mmd_root
    mmd_root.name, mmd_root.name_e = name_j, name_e
    text = bpy.data.texts.get(f"{root.name}_comment") or bpy.data.texts.new(f"{root.name}_comment")
    text.from_string(comment)
    mmd_root.comment_text = text.name


# ---------------------------------------------------------------------------
# materials (ID properties only: the XPS / HD node tree stays connected)

MATERIAL_DEFAULTS = {  # 18-series values (note 11 §9.1)
    "diffuse_color": (1.0, 1.0, 1.0),
    "alpha": 1.0,
    "specular_color": (0.5, 0.5, 0.5),
    "shininess": 10.0,
    "ambient_color": (0.5, 0.5, 0.5),
    "is_double_sided": True,
    "enabled_drop_shadow": True,
    "enabled_self_shadow_map": True,
    "enabled_self_shadow": True,
    "enabled_toon_edge": False,
    "edge_weight": 1.0,
    "is_shared_toon_texture": True,
    "shared_toon_texture": 0,
    "sphere_texture_type": 1,   # ID-prop value 1 = '0' (off)
}


def setup_material(mat: bpy.types.Material, name_j: str, comment: str, base_node: str, sphere_node: str) -> List[str]:
    """Write the MMD material parameters as ID properties and name the texture nodes for the exporter."""
    ensure_mmd_tools()
    notes = []
    mm = mat.mmd_material
    for key, value in MATERIAL_DEFAULTS.items():
        mm[key] = value
    mm["name_j"] = name_j
    mm["name_e"] = name_j
    mm["comment"] = comment
    if mat.use_nodes and mat.node_tree is not None:
        nodes = mat.node_tree.nodes
        for wanted, current in (("mmd_base_tex", base_node), ("mmd_sphere_tex", sphere_node)):
            if nodes.get(wanted) is not None:
                continue
            node = nodes.get(current)
            if node is not None and node.type == 'TEX_IMAGE' and node.image is not None:
                node.name = wanted
            elif wanted == "mmd_base_tex":
                notes.append(f"{mat.name}: 没有漫反射贴图节点")
    return notes


def material_output_is_mmd_shader(mat: bpy.types.Material) -> bool:
    if not mat.use_nodes or mat.node_tree is None:
        return False
    for node in mat.node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL' and node.is_active_output:
            links = node.inputs["Surface"].links
            return bool(links) and links[0].from_node.name == "mmd_shader"
    return False


# ---------------------------------------------------------------------------
# export / read back

def model_parts(root: bpy.types.Object):
    ensure_mmd_tools()
    from mmd_tools.core.model import Model
    rig = Model(root)
    return rig.armature(), list(rig.meshes()), list(rig.rigidBodies()), list(rig.joints())


def export_pmx(context: bpy.types.Context, root: bpy.types.Object, filepath: str, scale: float = EXPORT_SCALE,
               copy_textures: bool = True) -> None:
    ensure_mmd_tools()
    from mmd_tools.core.pmx import exporter
    arm, meshes, rigids, joints = model_parts(root)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with ContextGuard(context):
        old = arm.data.pose_position
        arm.data.pose_position = 'REST'
        arm.update_tag()
        context.scene.frame_set(context.scene.frame_current)
        try:
            exporter.export(filepath, root=root, armature=arm, meshes=meshes, rigid_bodies=rigids, joints=joints,
                            scale=scale, copy_textures=copy_textures, sort_materials=False, sort_vertices='NONE',
                            disable_specular=False, overwrite_bone_morphs_from_pose_library=False,
                            translate_in_presets=False)
        finally:
            arm.data.pose_position = old
            arm.update_tag()


def read_pmx(filepath: str) -> Dict:
    """Plain-data summary of a PMX file (for the post-export checks in core)."""
    ensure_mmd_tools()
    from mmd_tools.core import pmx
    m = pmx.load(filepath)
    bones = []
    for b in m.bones:
        bones.append({
            "name": b.name, "name_e": b.name_e, "parent": -1 if b.parent is None else int(b.parent),
            "location": [float(x) for x in b.location], "transform_order": int(b.transform_order),
            "rotatable": bool(b.isRotatable), "movable": bool(b.isMovable), "visible": bool(b.visible),
            "controllable": bool(b.isControllable), "is_ik": bool(b.isIK),
            "grant": None if b.additionalTransform is None else
            [int(b.additionalTransform[0]), float(b.additionalTransform[1])],
            "grant_rotate": bool(b.hasAdditionalRotate), "grant_move": bool(b.hasAdditionalLocation),
            "axis": None if b.axis is None else [float(x) for x in b.axis],
            "local": None if b.localCoordinate is None else
            [[float(x) for x in b.localCoordinate.x_axis], [float(x) for x in b.localCoordinate.z_axis]],
            "ik": None if not b.isIK else {
                "target": int(b.target), "loop": int(b.loopCount), "unit": float(b.rotationConstraint),
                "links": [{"bone": int(l.target),
                           "min": None if l.minimumAngle is None else [float(x) for x in l.minimumAngle],
                           "max": None if l.maximumAngle is None else [float(x) for x in l.maximumAngle]}
                          for l in b.ik_links]},
        })
    n_bones = len(m.bones)
    weight_counts = np.zeros(n_bones, dtype=np.int64)
    bad_refs = 0
    sums_off = 0
    max_influences = 0
    unweighted = 0
    for v in m.vertices:
        w = v.weight
        idx = [int(i) for i in w.bones]
        if w.type == 0:            # BDEF1
            pairs = [(idx[0], 1.0)]
        elif w.type == 1:          # BDEF2
            pairs = [(idx[0], float(w.weights[0])), (idx[1], 1.0 - float(w.weights[0]))]
        elif w.type == 3:          # SDEF
            pairs = [(idx[0], float(w.weights.weight)), (idx[1], 1.0 - float(w.weights.weight))]
        else:                      # BDEF4
            pairs = list(zip(idx, (float(x) for x in w.weights)))
        pairs = [(i, x) for i, x in pairs if i >= 0 and x > 0]
        if not pairs:
            unweighted += 1
        max_influences = max(max_influences, len(pairs))
        if pairs and abs(sum(x for _, x in pairs) - 1.0) > 1e-3:
            sums_off += 1
        for i, _ in pairs:
            if i >= n_bones:
                bad_refs += 1
            else:
                weight_counts[i] += 1
    ys = [float(v.co[1]) for v in m.vertices]
    textures = [t.path for t in m.textures]
    materials = [{"name": mt.name, "texture": int(mt.texture), "sphere": int(mt.sphere_texture),
                  "sphere_mode": int(mt.sphere_texture_mode), "toon_shared": bool(mt.is_shared_toon_texture),
                  "toon": int(mt.toon_texture), "comment": mt.comment, "faces": int(mt.vertex_count) // 3,
                  "double_sided": bool(getattr(mt, "is_double_sided", False))} for mt in m.materials]
    frames = [{"name": d.name, "name_e": d.name_e, "special": bool(d.isSpecial),
               "items": [[int(t), int(i)] for t, i in d.data]} for d in m.display]
    return {"name": m.name, "name_e": m.name_e, "bones": bones, "vertices": len(m.vertices),
            "faces": len(m.faces), "weight_counts": weight_counts.tolist(), "bad_weight_refs": bad_refs,
            "weight_sums_off": sums_off, "max_influences": max_influences, "unweighted_vertices": unweighted,
            "min_y": min(ys) if ys else 0.0, "max_y": max(ys) if ys else 0.0,
            "textures": textures, "materials": materials, "frames": frames, "morphs": len(m.morphs),
            "rigids": len(m.rigids), "joints": len(m.joints)}
