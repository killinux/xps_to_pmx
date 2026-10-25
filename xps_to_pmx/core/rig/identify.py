"""Stage ② engine: fill mapping slots and decide what happens to every source bone.

Order (design doc §5.3): user-fixed slots → alias table (best-scoring
convention first, other columns as fallback) → spine by position → topology
for whatever is still empty (and as a cross-check of the alias results) →
下半身 diagnosis → classification of the remaining bones.  Every slot match
records its origin, confidence and reason; one source bone fills at most one
slot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..spec import BoneSpec, norm_name
from .classify import Disposition, classify_bones
from .lower_body import LowerBodyDiagnosis, diagnose_lower_body
from .rigdata import RigData
from .topology import TopologyResult, assign_spine, identify_topology

ORIGIN_USER = "user"
ORIGIN_CSV = "csv"
ORIGIN_SPINE = "spine"
ORIGIN_TOPOLOGY = "topology"
ORIGIN_DIAG = "diagnosis"

SPINE_SLOTS = ("upper_body1_bone", "upper_body2_bone", "upper_body3_bone", "upper_body4_bone")


@dataclass
class SlotMatch:
    slot_id: str
    bone: int = -1
    origin: str = ""
    confidence: float = 0.0
    reason: str = ""
    merges: List[int] = field(default_factory=list)

    @property
    def mapped(self) -> bool:
        return self.bone >= 0


@dataclass
class Identification:
    convention: str
    convention_scores: List[Tuple[str, int]]
    slots: Dict[str, SlotMatch]
    bones: Dict[int, Disposition]
    lower_body: LowerBodyDiagnosis
    topology: TopologyResult
    disagreements: List[Tuple[str, int, int]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    #: "-Y" (MMD/Blender convention, character's left at +X) or "+Y" (model faces backwards)
    facing: str = "-Y"

    def bone_of(self, slot_id: str) -> int:
        m = self.slots.get(slot_id)
        return m.bone if m else -1

    def slot_bones(self) -> Dict[str, int]:
        return {s: m.bone for s, m in self.slots.items() if m.bone >= 0}


def score_conventions(rig: RigData, spec: BoneSpec) -> List[Tuple[str, int]]:
    present = {norm_name(b.name) for b in rig.bones}
    scores = []
    for conv in spec.conventions:
        hits = sum(1 for slot in spec if any(a.norm in present for a in slot.primary_aliases(conv)))
        scores.append((conv, hits))
    scores.sort(key=lambda t: -t[1])
    return scores


def identify(rig: RigData, spec: BoneSpec, convention: Optional[str] = None,
             fixed: Optional[Dict[str, int]] = None) -> Identification:
    fixed = fixed or {}
    scores = score_conventions(rig, spec)
    conv = convention or (scores[0][0] if scores and scores[0][1] > 0 else "")
    by_norm: Dict[str, List[int]] = {}
    for b in rig.bones:
        by_norm.setdefault(norm_name(b.name), []).append(b.index)

    slots: Dict[str, SlotMatch] = {s.slot_id: SlotMatch(s.slot_id) for s in spec}
    taken: Dict[int, str] = {}
    merged: Dict[int, str] = {}
    notes: List[str] = []

    blocked = {s for s, b in fixed.items() if b < 0 and s in slots}

    def assign(slot_id: str, bone: int, origin: str, conf: float, reason: str) -> bool:
        if bone < 0 or bone in taken or bone in merged or slot_id in blocked:
            return False
        m = slots[slot_id]
        m.bone, m.origin, m.confidence, m.reason = bone, origin, conf, reason
        taken[bone] = slot_id
        return True

    def add_merge(slot_id: str, bone: int) -> None:
        if bone >= 0 and bone not in taken and bone not in merged:
            slots[slot_id].merges.append(bone)
            merged[bone] = slot_id

    # 1. user-fixed slots win (bone -1 = the user wants this slot empty, i.e. generated)
    for slot_id, bone in fixed.items():
        if slot_id in slots and 0 <= bone < len(rig):
            assign(slot_id, bone, ORIGIN_USER, 1.0, "用户指定")
    for slot_id in blocked:
        slots[slot_id].origin, slots[slot_id].reason = ORIGIN_USER, "用户指定留空（由补骨生成）"

    # 2. alias table: chosen convention first, then the others as fallback
    order = ([conv] if conv else []) + [c for c in spec.conventions if c != conv]
    for rank, column in enumerate(order):
        conf = 1.0 if rank == 0 else 0.85
        for slot in spec.ordered():
            m = slots[slot.slot_id]
            if not m.mapped:
                for alias in slot.primary_aliases(column):
                    hit = next((b for b in by_norm.get(alias.norm, ()) if b not in taken and b not in merged), -1)
                    if assign(slot.slot_id, hit, ORIGIN_CSV, conf, f"名称表 {column}: {alias.name}"):
                        break
            if slots[slot.slot_id].mapped:
                for alias in slot.merge_aliases(column):
                    for b in by_norm.get(alias.norm, ()):
                        add_merge(slot.slot_id, b)

    # 3. topology (needed for the spine rule, the fallback and the cross-check)
    topo = identify_topology(rig)

    # 4. spine chain by position between 上半身 and 首
    ub = slots["upper_body_bone"].bone
    neck = slots["neck_bone"].bone if slots["neck_bone"].mapped else slots["head_bone"].bone
    if ub >= 0 and neck >= 0 and rig.is_ancestor(ub, neck):
        chain = [ub] + rig.path_down(ub, rig.bones[neck].parent) if rig.bones[neck].parent != ub else [ub]
        chain = [b for b in chain if b == ub or (b not in taken and b not in merged) or taken.get(b) in SPINE_SLOTS]
        for slot_id, bone in assign_spine(rig, chain, neck).items():
            if slot_id != "upper_body_bone" and not slots[slot_id].mapped:
                assign(slot_id, bone, ORIGIN_SPINE, 0.9, "脊柱按位置分配（上半身2 取最接近 上半身→首 0.35 处的一节）")

    # 5. topology fills the gaps; disagreements are recorded for the checker
    disagreements = []
    for slot_id, bone in topo.slots.items():
        if slot_id not in slots:
            continue
        m = slots[slot_id]
        if not m.mapped:
            if assign(slot_id, bone, ORIGIN_TOPOLOGY, 0.7, f"拓扑: {topo.reasons.get(slot_id, '')}"):
                for extra in topo.merges.get(slot_id, ()):
                    add_merge(slot_id, extra)
        elif m.bone != bone and m.origin in (ORIGIN_CSV, ORIGIN_SPINE) and bone not in m.merges:
            disagreements.append((slot_id, m.bone, bone))
    for slot_id, extras in topo.merges.items():
        if slots.get(slot_id) and slots[slot_id].mapped:
            for extra in extras:
                add_merge(slot_id, extra)

    # 6. 下半身 diagnosis
    thighs = [slots[s].bone for s in ("left_thigh_bone", "right_thigh_bone") if slots[s].mapped]
    excluded = {b for b, s in taken.items() if s != "lower_body_bone" and spec[s].deform}
    diag = diagnose_lower_body(rig, slots["upper_body_bone"].bone, thighs, topo.leg_fork,
                               slots["lower_body_bone"].bone, excluded)
    lb = slots["lower_body_bone"]
    if diag.case in ("A", "B") and diag.primary >= 0:
        if lb.mapped and lb.bone != diag.primary:
            if not rig.bones[lb.bone].weighted and lb.origin != ORIGIN_USER:
                old = lb.bone
                del taken[old]
                lb.bone = -1
                assign("lower_body_bone", diag.primary, ORIGIN_DIAG, 0.9, diag.text)
                notes.append(f"下半身 改用 {rig.bones[diag.primary].name}（{rig.bones[old].name} 无权重）")
            else:
                add_merge("lower_body_bone", diag.primary)
        elif not lb.mapped:
            if diag.primary in taken:  # e.g. topology put it on a control slot
                other = taken.pop(diag.primary)
                slots[other].bone = -1
            assign("lower_body_bone", diag.primary, ORIGIN_DIAG, 0.9, diag.text)
        for extra in diag.merges:
            if extra in taken and slots[taken[extra]].origin != ORIGIN_USER and not spec[taken[extra]].deform:
                slots[taken.pop(extra)].bone = -1
            add_merge("lower_body_bone", extra)

    facing = detect_facing(rig, spec, slots)
    if facing == "+Y":
        notes.append("模型背朝前方（左侧骨在 -X），③ 预处理会先旋转 180°")
    for left_id, right_id in swap_mirrored_pairs(rig, spec, slots, facing):
        notes.append(f"{spec[left_id].name_j}/{spec[right_id].name_j} 的源骨名字左右标反了，已按位置交换")

    # 7. classification of everything else
    head = slots["head_bone"].bone
    dispositions = classify_bones(rig, {s: m.bone for s, m in slots.items()}, merged, head)
    for bone, disp in dispositions.items():
        if disp.action == "merge" and bone not in merged:
            merged[bone] = disp.slot_id
            slots[disp.slot_id].merges.append(bone)
    return Identification(conv, scores, slots, dispositions, diag, topo, disagreements, notes + topo.notes,
                          facing)


def swap_mirrored_pairs(rig: RigData, spec: BoneSpec, slots: Dict[str, SlotMatch], facing: str) -> List[Tuple[str, str]]:
    """Swap L/R slot pairs whose two bones both sit clearly on the opposite side (names lie, positions don't).

    User-fixed slots are never touched.  Bones near the centre line are left
    alone, so a collapsed / broken skeleton is reported by the checker instead.
    """
    eps = rig.centre_eps()
    sign = -1.0 if facing == "+Y" else 1.0
    swapped = []
    for s in spec:
        if s.side != "L" or not s.mirror:
            continue
        lm, rm = slots.get(s.slot_id), slots.get(s.mirror)
        if lm is None or rm is None or not lm.mapped or not rm.mapped:
            continue
        if ORIGIN_USER in (lm.origin, rm.origin):
            continue
        lx = sign * float((rig.bones[lm.bone].head[0] + rig.bones[lm.bone].tail[0]) / 2)
        rx = sign * float((rig.bones[rm.bone].head[0] + rig.bones[rm.bone].tail[0]) / 2)
        if lx < -eps and rx > eps:
            lm.bone, rm.bone = rm.bone, lm.bone
            lm.merges, rm.merges = rm.merges, lm.merges
            lm.reason = rm.reason = "源骨名左右标反，已按位置交换"
            swapped.append((s.slot_id, s.mirror))
    return swapped


def detect_facing(rig: RigData, spec: BoneSpec, slots: Dict[str, SlotMatch]) -> str:
    """Majority vote of mapped limb bones: are "left" bones on +X (facing -Y) or on -X (facing +Y)?"""
    eps = rig.centre_eps()
    agree = disagree = 0
    for s in spec:
        m = slots.get(s.slot_id)
        if s.side not in ("L", "R") or s.group not in ("arm", "leg") or m is None or not m.mapped:
            continue
        b = rig.bones[m.bone]
        x = float((b.head[0] + b.tail[0]) / 2)
        if abs(x) < eps:
            continue
        if (x > 0) == (s.side == "L"):
            agree += 1
        else:
            disagree += 1
    return "+Y" if disagree > agree else "-Y"
