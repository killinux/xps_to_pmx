"""Mapping checks (design doc §5.4).  Expectations come only from the spec table.

Levels: ``error`` blocks the next stage, ``warning`` needs a look, ``info``
explains a decision.  Every rule has a counter-example test in
``tests/test_checks.py`` (hard constraint 6).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from ..fixes import Fix
from ..rig.identify import Identification
from ..rig.rigdata import RigData
from ..spec import BoneSpec

ERROR = "error"
WARNING = "warning"
INFO = "info"

SYMMETRY_TOL = 0.02        # fraction of model height
LIMB_RATIO = (0.55, 1.8)   # upper/lower segment length ratio range
JOINT_FRACTION = (0.3, 0.7)


@dataclass
class CheckItem:
    level: str
    code: str
    text: str
    slot_id: str = ""
    bone: str = ""
    detail: str = ""                      # evidence (numbers) shown under the text
    fix: Optional[Fix] = None             # suggested fix (design doc §15.3)


def _name(rig: RigData, bone: int) -> str:
    return rig.bones[bone].name if bone >= 0 else ""


def mapped_spec_parent(spec: BoneSpec, slot_bones: Dict[str, int], slot_id: str) -> Optional[str]:
    """Nearest slot up the spec parent chain that is mapped (parent fallbacks followed recursively)."""
    seen = set()
    frontier = list(spec[slot_id].parents)
    while frontier:
        nxt = []
        for p in frontier:
            if p in seen:
                continue
            seen.add(p)
            if slot_bones.get(p, -1) >= 0:
                return p
        for p in frontier:
            nxt.extend(spec[p].parents[:1])  # climb through the primary parent of unmapped slots
        frontier = [p for p in nxt if p not in seen]
    return None


_LIMB_GROUPS = ("arm", "finger", "leg")


def _same_chain(spec: BoneSpec, slot_id: str, parent_slot: str) -> bool:
    a, b = spec[slot_id], spec[parent_slot]
    if a.group == "finger":
        return b.group in ("finger", "arm")
    if a.group == "eye":
        return parent_slot == "head_bone"
    return a.group == b.group and a.group in ("arm", "leg", "trunk")


def _conflicting_chain(spec: BoneSpec, slot_id: str, owner: str) -> bool:
    """The bone sits under another limb (other side, or arm vs leg): strong sign of a wrong mapping."""
    a, o = spec[slot_id], spec[owner]
    if a.group not in _LIMB_GROUPS or o.group not in _LIMB_GROUPS:
        return False
    if a.side in ("L", "R") and o.side in ("L", "R") and a.side != o.side:
        return True
    return (a.group == "leg") != (o.group == "leg")


def check_mapping(rig: RigData, spec: BoneSpec, ident: Identification) -> List[CheckItem]:
    items: List[CheckItem] = []
    slots = ident.slots
    slot_bones = {s: m.bone for s, m in slots.items() if m.bone >= 0}
    eps = rig.centre_eps()

    # completeness and uniqueness
    for s in spec.ordered():
        if s.required and s.slot_id not in slot_bones:
            items.append(CheckItem(ERROR, "mapping.required_missing", f"必需骨 {s.name_j} 没有映射", s.slot_id))
    used: Dict[int, List[str]] = {}
    for slot_id, bone in slot_bones.items():
        used.setdefault(bone, []).append(slot_id)
    for bone, owners in used.items():
        if len(owners) > 1:
            names = "、".join(spec[o].name_j for o in owners)
            items.append(CheckItem(ERROR, "mapping.duplicate", f"源骨 {_name(rig, bone)} 同时映射到 {names}",
                                   owners[0], _name(rig, bone)))
    for bone in list(used):
        disp = ident.bones.get(bone)
        if disp is not None and disp.action == "delete":
            items.append(CheckItem(ERROR, "mapping.mapped_bone_deleted",
                                   f"{_name(rig, bone)} 已映射但处置为删除", used[bone][0], _name(rig, bone)))

    # facing, side, hierarchy
    flip = getattr(ident, "facing", "-Y") == "+Y"
    if flip:
        items.append(CheckItem(WARNING, "mapping.facing_back",
                               "模型背朝前方（左侧骨在 -X），③ 预处理会先绕 Z 轴旋转 180°"))
    primary_slot = {b: s for s, b in slot_bones.items()}
    for slot_id, bone in slot_bones.items():
        s = spec[slot_id]
        # side from the bone's midpoint: clavicles start on the centre line but point outwards
        x = float((rig.bones[bone].head[0] + rig.bones[bone].tail[0]) / 2)
        if flip:
            x = -x
        if s.side == "L" and x < eps or s.side == "R" and x > -eps:
            items.append(CheckItem(ERROR, "mapping.wrong_side",
                                   f"{s.name_j} 映射的 {_name(rig, bone)} 在另一侧或中线上（x={x:+.3f}）",
                                   slot_id, _name(rig, bone)))
        parent_slot = mapped_spec_parent(spec, slot_bones, slot_id)
        if parent_slot is None or spec[slot_id].tier != 0 or not _same_chain(spec, slot_id, parent_slot):
            continue  # trunk ↔ limb relations are rebuilt by ④ from the spec, the source may differ
        pb = slot_bones[parent_slot]
        if rig.is_ancestor(pb, bone):
            continue
        owner = next((primary_slot[a] for a in rig.ancestors(bone) if a in primary_slot), None)
        if owner is not None and _conflicting_chain(spec, slot_id, owner):
            items.append(CheckItem(ERROR, "mapping.hierarchy",
                                   f"{s.name_j}（{_name(rig, bone)}）挂在 {spec[owner].name_j} 下，"
                                   f"而不是 {spec[parent_slot].name_j}（{_name(rig, pb)}）下，映射可疑",
                                   slot_id, _name(rig, bone)))
        else:
            items.append(CheckItem(WARNING, "mapping.hierarchy_flat",
                                   f"{s.name_j}（{_name(rig, bone)}）不在 {spec[parent_slot].name_j}"
                                   f"（{_name(rig, pb)}）下（源骨架层级被打乱），④ 会按规格重挂",
                                   slot_id, _name(rig, bone)))

    # symmetry
    tol = SYMMETRY_TOL * rig.height
    for s in spec:
        if s.side != "L" or s.slot_id not in slot_bones or s.mirror not in slot_bones:
            continue
        lh = rig.bones[slot_bones[s.slot_id]].head
        rh = rig.bones[slot_bones[s.mirror]].head
        diff = float(np.linalg.norm(lh - rh * np.array([-1.0, 1.0, 1.0])))
        if diff > tol:
            items.append(CheckItem(WARNING, "mapping.asymmetric",
                                   f"{s.name_j} 与 {spec[s.mirror].name_j} 不对称（镜像差 {diff:.3f}）", s.slot_id))

    # limb proportions and joint placement
    for side in ("left", "right"):
        for upper, mid, end, label in (("upper_arm_bone", "lower_arm_bone", "hand_bone", "腕"),
                                       ("thigh_bone", "knee_bone", "ankle_bone", "足")):
            a, b, c = (slot_bones.get(f"{side}_{k}", -1) for k in (upper, mid, end))
            if min(a, b, c) < 0:
                continue
            pa, pb, pc = rig.bones[a].head, rig.bones[b].head, rig.bones[c].head
            l1, l2 = float(np.linalg.norm(pb - pa)), float(np.linalg.norm(pc - pb))
            if l1 < 1e-6 or l2 < 1e-6:
                items.append(CheckItem(ERROR, "mapping.zero_length", f"{side} {label} 链有零长度骨段",
                                       f"{side}_{mid}"))
                continue
            ratio = l1 / l2
            if not LIMB_RATIO[0] <= ratio <= LIMB_RATIO[1]:
                items.append(CheckItem(WARNING, "mapping.limb_ratio",
                                       f"{side} {label} 链上下段长度比 {ratio:.2f} 异常，关节可能映射错了",
                                       f"{side}_{mid}", _name(rig, b)))
            frac = l1 / (l1 + l2)
            if not JOINT_FRACTION[0] <= frac <= JOINT_FRACTION[1]:
                items.append(CheckItem(WARNING, "mapping.joint_position",
                                       f"{side} {label} 的中间关节位于整链 {frac:.0%} 处", f"{side}_{mid}"))

    # weights
    for slot_id, bone in slot_bones.items():
        s = spec[slot_id]
        weighted = rig.bones[bone].weighted or any(rig.bones[m].weighted for m in slots[slot_id].merges)
        if s.deform and not weighted and s.group not in ("eye",):
            items.append(CheckItem(WARNING, "mapping.no_weights",
                                   f"{s.name_j} 映射的 {_name(rig, bone)} 及其并入骨都没有权重", slot_id,
                                   _name(rig, bone)))
        if not s.deform and rig.bones[bone].weighted:
            items.append(CheckItem(INFO, "mapping.control_weighted",
                                   f"控制骨 {s.name_j}（{_name(rig, bone)}）带权重，④ 阶段会把权重移到 下半身",
                                   slot_id, _name(rig, bone)))

    # decisions worth explaining
    for slot_id, a, b in ident.disagreements:
        if not spec[slot_id].deform or slot_id == "lower_body_bone":
            continue  # control bones are rebuilt anyway; 下半身 is explained by its diagnosis
        items.append(CheckItem(INFO, "mapping.disagreement",
                               f"{spec[slot_id].name_j}：名称表选 {_name(rig, a)}，拓扑认为是 {_name(rig, b)}",
                               slot_id, _name(rig, a)))
    diag = ident.lower_body
    if diag.case:
        level = INFO if diag.case in ("A", "B") else WARNING
        items.append(CheckItem(level, f"mapping.lower_body_{diag.case}", diag.text, "lower_body_bone",
                               _name(rig, diag.primary)))
    elif diag.text:
        items.append(CheckItem(WARNING, "mapping.lower_body_unknown", diag.text, "lower_body_bone"))
    if "left_eye_bone" not in slot_bones and "right_eye_bone" not in slot_bones:
        items.append(CheckItem(INFO, "mapping.no_eyes", "没有眼骨：両目/左目/右目 不生成，表情里的眼球动作不可用"))
    return items


def has_errors(items: List[CheckItem]) -> bool:
    return any(i.level == ERROR for i in items)
