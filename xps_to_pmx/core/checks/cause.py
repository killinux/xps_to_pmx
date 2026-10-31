"""Cause checks on the source skeleton, run in stage ② (design doc §15.5).

They name the source bone that causes a problem and suggest the fix:

* ``mapping.merge_segment``: a bone merged into one limb segment while its weights
  clearly lie in another segment (the knee / elbow breaks when that joint bends).
  Automatic unless the user decided that bone.
* ``mapping.duplicate_name``: two source bones share a name, one carries weights
  on both sides and the other none (the file's vertices all point at the first
  copy).  The fix splits the weights by side; it edits source weights, so it is
  never automatic.

The analysis behind them is stored with the job so the checkup can trace
symptoms on the MMD model back to source bones.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Set

from ..fixes import Fix
from ..rig.classify import Disposition
from ..rig.limbs import LIMB_SEGMENTS, SegmentMass, limb_segments, segment_mass
from ..rig.rigdata import RigData
from ..spec import BoneSpec
from .mapping import INFO, WARNING, CheckItem

#: Share of a bone's weight on the twin's side, and vertices there, that make a duplicate name a finding.
DUPLICATE_SHARE = 0.10
DUPLICATE_VERTICES = 10
#: Width of the centre band (fraction of model height) ignored when deciding sides.
SIDE_MARGIN = 0.02
#: The centre band where a split blends linearly (fraction of model height).
SPLIT_BLEND = 0.01

SEGMENT_SLOTS = frozenset(f"{side}_{a}" for side in ("left", "right") for a, _ in LIMB_SEGMENTS)
#: Only body helpers are judged by limb segments: a skirt piece merged into a leg is a different problem
#: (on the corpus, skirt hems below the knee would otherwise be "fixed" into the shin, 2026-10-31).
NOT_BODY = frozenset(("hair", "cloth", "breast", "butt", "prop", "genital", "face"))


@dataclass
class MergeAnalysis:
    bone: int
    slot: str                 # current merge target
    mass: SegmentMass

    def as_dict(self, rig: RigData) -> Dict:
        b = rig.bones[self.bone]
        return {"bone": b.name, "src": b.src_name or b.name, "slot": self.slot, **self.mass.as_dict()}


@dataclass
class DuplicatePair:
    bone: int                 # the copy that carries the weights
    twin: int                 # the same-named copy on the other side, without weights
    twin_side: float          # +1 / -1: the twin's side of the centre line (x sign)
    share: float              # share of ``bone``'s weight on the twin's side
    vertices: int             # vertices of ``bone`` on the twin's side

    def as_dict(self, rig: RigData) -> Dict:
        return {"bone": rig.bones[self.bone].name, "twin": rig.bones[self.twin].name,
                "src": rig.bones[self.bone].src_name or rig.bones[self.bone].name,
                "twin_side": self.twin_side, "share": round(self.share, 4), "vertices": self.vertices}


def merge_analysis(rig: RigData, slot_bones: Dict[str, int], dispositions: Dict[int, Disposition]
                   ) -> List[MergeAnalysis]:
    """Segment masses of every bone merged into a limb segment slot."""
    segments = {side: limb_segments(rig, slot_bones, side) for side in ("left", "right")}
    out = []
    for b, d in dispositions.items():
        if d.action != "merge" or d.slot_id not in SEGMENT_SLOTS or d.category in NOT_BODY:
            continue
        side = d.slot_id.split("_", 1)[0]
        ancestors = set(rig.ancestors(b))
        allowed = [s for s in segments[side] if s.end_bone not in ancestors]
        mass = segment_mass(rig, b, allowed)
        if mass is not None:
            out.append(MergeAnalysis(b, d.slot_id, mass))
    return out


def check_merge_segments(rig: RigData, spec: BoneSpec, analysis: Iterable[MergeAnalysis],
                         user_decided: Set[str]) -> List[CheckItem]:
    items = []
    for a in analysis:
        owner = a.mass.clear_owner()
        if owner is None or owner == a.slot:
            continue
        name = rig.bones[a.bone].name
        share = a.mass.fractions[owner]
        decided = f"bone:{name}" in user_decided
        fix = Fix("bone", bone=name, src=rig.bones[a.bone].src_name or name, action="merge", slot_id=owner,
                  finding=f"mapping.merge_segment:{name}", origin="checkup", auto=not decided,
                  note=f"{share:.0%} 的明确权重在 {spec[owner].name_j} 段")
        text = (f"{name} 并入了 {spec[a.slot].name_j}，但它 {share:.0%} 的明确权重在 {spec[owner].name_j} 段；"
                f"弯曲关节时这部分会被扯着走")
        if decided:
            text += "（你手动指定过这根骨，没有自动改）"
        detail = (f"关节两侧各 10% 以外的权重占 {a.mass.decisive:.0%}，其中 {share:.0%} 在 {spec[owner].name_j} 段；"
                  f"共 {a.mass.vertices} 个顶点")
        items.append(CheckItem(WARNING, "mapping.merge_segment", text, owner, name, detail, fix))
    return items


def find_duplicates(rig: RigData) -> List[DuplicatePair]:
    """Same-named bones where one copy carries weights on both sides and the other copy none."""
    if rig.skin is None:
        return []
    groups: Dict[str, List[int]] = {}
    for b in rig.bones:
        groups.setdefault(b.src_name or b.name, []).append(b.index)
    eps = SIDE_MARGIN * rig.height
    x = rig.skin.positions[:, 0].astype(float)
    out = []
    for members in groups.values():
        if len(members) < 2:
            continue
        weighted = [m for m in members if rig.bones[m].weighted]
        empty = [m for m in members if not rig.bones[m].weighted]
        for twin in empty:
            tx = float(rig.bones[twin].head[0])
            if abs(tx) <= eps:
                continue
            twin_side = 1.0 if tx > 0 else -1.0
            for bone in weighted:
                bx = float(rig.bones[bone].head[0])
                if bx * twin_side > eps:
                    continue  # both copies on the same side: not a mirrored pair
                w = rig.skin.bone_weight_column(bone)
                total = float(w.sum())
                if total <= 0:
                    continue
                there = (x * twin_side > eps) & (w > 0)
                share = float(w[there].sum()) / total
                if share >= DUPLICATE_SHARE and int(there.sum()) >= DUPLICATE_VERTICES:
                    out.append(DuplicatePair(bone, twin, twin_side, share, int(there.sum())))
                    break
    return out


def check_duplicates(rig: RigData, pairs: Iterable[DuplicatePair]) -> List[CheckItem]:
    items = []
    for p in pairs:
        name, twin = rig.bones[p.bone].name, rig.bones[p.twin].name
        side = "左" if p.twin_side > 0 else "右"
        fix = Fix("split_side", bone=name, src=rig.bones[p.bone].src_name or name, twin=twin,
                  finding=f"mapping.duplicate_name:{name}", origin="checkup", auto=False,
                  note=f"把{side}侧的权重拆给 {twin}")
        text = (f"源文件里有两根骨都叫“{rig.bones[p.bone].src_name or name}”：权重全在 {name} 上，"
                f"{side}侧那根（{twin}）没有权重；动一侧时另一侧也会跟着动")
        detail = f"{name} 有 {p.share:.0%} 的权重、{p.vertices} 个顶点在{side}侧"
        items.append(CheckItem(WARNING, "mapping.duplicate_name", text, "", name, detail, fix))
    return items


def auto_fixed_item(fix: Fix, spec: BoneSpec) -> CheckItem:
    """The info line left in the ② checks after a fix was applied automatically."""
    slot = spec.get(fix.slot_id)
    target = slot.name_j if slot is not None else fix.slot_id
    return CheckItem(INFO, "mapping.auto_fixed", f"已自动修正：{fix.bone} 改并入 {target}（{fix.note}）",
                     fix.slot_id, fix.bone, fix.note, fix)
