"""Blender → :class:`RigData` (bones in armature space, skin weights as top-4 arrays)."""
from __future__ import annotations

from typing import List, Optional

import bpy
import numpy as np

from ..core.rig.rigdata import RigBone, RigData, SkinData
from .importer import PROP_SRC


def skinned_meshes(arm_obj: bpy.types.Object) -> List[bpy.types.Object]:
    out = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or not len(obj.data.vertices):  # e.g. the zero-vertex bone-order mesh
            continue
        if any(m.type == 'ARMATURE' and m.object == arm_obj for m in obj.modifiers):
            out.append(obj)
    return sorted(out, key=lambda o: o.name)


def rig_from_blender(arm_obj: bpy.types.Object, with_skin: bool = True,
                     meshes: Optional[List[bpy.types.Object]] = None) -> RigData:
    arm = arm_obj.data
    index = {b.name: i for i, b in enumerate(arm.bones)}
    bones = []
    for i, b in enumerate(arm.bones):
        parent = index[b.parent.name] if b.parent else -1
        bones.append(RigBone(i, b.name, parent, np.array(b.head_local, float), np.array(b.tail_local, float),
                             b.get(PROP_SRC, b.name)))
    skin = None
    if with_skin:
        skin = _skin(arm_obj, meshes if meshes is not None else skinned_meshes(arm_obj), index)
    return RigData(bones, skin, arm_obj.name)


def _skin(arm_obj, meshes, index) -> Optional[SkinData]:
    all_pos, all_bones, all_weights, slices = [], [], [], []
    to_arm = np.array(arm_obj.matrix_world.inverted())
    start = 0
    for obj in meshes:
        me = obj.data
        n = len(me.vertices)
        if not n:
            continue
        slices.append((obj.name, start, start + n))
        start += n
        co = np.empty(n * 3, dtype=np.float32)
        me.vertices.foreach_get("co", co)
        m = to_arm @ np.array(obj.matrix_world)
        co = co.reshape(-1, 3) @ m[:3, :3].T + m[:3, 3]
        group_bone = {vg.index: index.get(vg.name, -1) for vg in obj.vertex_groups}
        bones = np.full((n, 4), -1, dtype=np.int32)
        weights = np.zeros((n, 4), dtype=np.float32)
        for i, v in enumerate(me.vertices):
            pairs = [(group_bone.get(g.group, -1), g.weight) for g in v.groups if g.weight > 0]
            pairs = [p for p in pairs if p[0] >= 0]
            if not pairs:
                continue
            if len(pairs) > 4:
                pairs.sort(key=lambda p: -p[1])
                pairs = pairs[:4]
            for k, (b, w) in enumerate(pairs):
                bones[i, k] = b
                weights[i, k] = w
        all_pos.append(co.astype(np.float32))
        all_bones.append(bones)
        all_weights.append(weights)
    if not all_pos:
        return None
    return SkinData(np.concatenate(all_pos), np.concatenate(all_bones), np.concatenate(all_weights), slices)
