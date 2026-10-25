"""下半身 diagnosis (design doc §6): where do the lower-torso weights live?

Cases (L = 上半身 head height − 足 head height):

* **A** a clean hip bone (its w>0.5 vertices have a median height in
  [足 − 1.0L, 上半身 + 0.3L]) → rename / merge it into 下半身 (what the 18
  series does: 下半身 = source pelvis + hip weights, vertex for vertex);
* **B** the same, but the weights sit on a helper / ``unused`` bone (lezisell
  ``unused bip001 pelvis``, Eve ``pelvis alt``) → merge it into 下半身;
* **C** the hip bone also covers the belly (median above 上半身 + 0.3L) →
  split it by height with ``S(t)`` (S(0.5)=1, S(1.75)=0, t = (z − 足)/L);
* **D** no hip weights at all (legs hang off the spine) → split the lowest
  spine bone the same way.

Read-only: the weight surgery happens in stage ④.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from .rigdata import RigData

T_FULL = 0.5      # S(t) = 1 at and below
T_ZERO = 1.75     # S(t) = 0 at and above
#: Candidates are already centred hip-region bones, so only the upper bound (belly
#: coverage → case C) matters; the lower bound just rejects bones living in the legs.
#: UE-style pelvises reach down over the buttocks (median t ≈ -1.1 on Gantz Reika).
MEDIAN_LOW = -3.0
MEDIAN_HIGH = 1.3
_EXCLUDE_RE = re.compile(r"skirt|cloth|coat|cape|hair|breast|boob|weapon|prop|genital|gens\b|pussy|vagina|penis"
                         r"|dick|ball_?s?\b|testic|anus|butt|glute|tail", re.IGNORECASE)


def split_factor(t: np.ndarray) -> np.ndarray:
    """Share of a vertex weight that goes to 下半身 at normalised height ``t``."""
    x = np.clip((np.asarray(t, dtype=np.float64) - T_FULL) / (T_ZERO - T_FULL), 0.0, 1.0)
    return 1.0 - x * x * (3.0 - 2.0 * x)


@dataclass
class Candidate:
    bone: int
    name: str
    vertices: int
    strong_vertices: int
    median_t: Optional[float]

    def as_dict(self) -> Dict:
        return {"bone": self.name, "vertices": self.vertices, "strong_vertices": self.strong_vertices,
                "median_t": None if self.median_t is None else round(self.median_t, 3)}


@dataclass
class LowerBodyDiagnosis:
    case: str = ""
    primary: int = -1
    merges: List[int] = field(default_factory=list)
    split_bone: int = -1
    waist_z: float = 0.0
    thigh_z: float = 0.0
    seg_l: float = 0.0
    candidates: List[Candidate] = field(default_factory=list)
    text: str = ""

    @property
    def needs_split(self) -> bool:
        return self.case in ("C", "D")


def diagnose_lower_body(rig: RigData, upper_body: int, thighs: List[int], leg_fork: int,
                        mapped_lower: int, excluded: set) -> LowerBodyDiagnosis:
    diag = LowerBodyDiagnosis()
    if upper_body < 0 or len(thighs) < 2:
        diag.text = "缺少 上半身 或左右 足 的映射，无法诊断下半身"
        return diag
    diag.waist_z = float(rig.bones[upper_body].head[2])
    diag.thigh_z = float(np.mean([rig.bones[t].head[2] for t in thighs]))
    seg = diag.waist_z - diag.thigh_z
    diag.seg_l = seg if seg > 0.01 * rig.height else 0.03 * rig.height
    if rig.skin is None or not rig.skin.count:
        diag.text = "没有蒙皮数据，无法诊断下半身"
        return diag

    eps = rig.centre_eps()
    lo = diag.thigh_z - 1.5 * diag.seg_l
    hi = diag.waist_z + 1.5 * diag.seg_l
    cand_ids = []
    for b in rig.bones:
        if b.index in excluded or not b.weighted or (b.index != mapped_lower and _EXCLUDE_RE.search(b.name)):
            continue
        if abs(float(b.head[0])) > eps or not (lo <= float(b.head[2]) <= hi):
            continue
        related = b.index in (mapped_lower, leg_fork) or any(rig.is_ancestor(b.index, t) for t in thighs) \
            or (leg_fork >= 0 and rig.is_ancestor(leg_fork, b.index) and not
                any(rig.is_ancestor(b.index, t) or b.index == t for t in thighs))
        if related:
            cand_ids.append(b.index)
    if mapped_lower >= 0 and mapped_lower not in cand_ids and rig.bones[mapped_lower].weighted:
        cand_ids.append(mapped_lower)

    for idx in cand_ids:
        col = rig.skin.bone_weight_column(idx)
        strong = col > 0.5
        t = (rig.skin.positions[strong, 2] - diag.thigh_z) / diag.seg_l
        diag.candidates.append(Candidate(idx, rig.bones[idx].name, int((col > 0).sum()), int(strong.sum()),
                                         float(np.median(t)) if strong.any() else None))
    diag.candidates.sort(key=lambda c: -c.vertices)

    in_range = [c for c in diag.candidates if c.median_t is not None and MEDIAN_LOW <= c.median_t <= MEDIAN_HIGH]
    if in_range:
        best = in_range[0]
        if mapped_lower >= 0 and any(c.bone == mapped_lower for c in in_range):
            best = next(c for c in in_range if c.bone == mapped_lower)
        diag.primary = best.bone
        diag.merges = [c.bone for c in in_range if c.bone != best.bone]
        named_hip = mapped_lower == best.bone and not rig.bones[best.bone].name.lower().startswith("unused")
        diag.case = "A" if named_hip else "B"
        diag.text = (f"情形{diag.case}：髋部权重在 {best.name}（中位高度 t={best.median_t:.2f}），"
                     f"改名/合并为 下半身" + (f"，另并入 {len(diag.merges)} 根" if diag.merges else ""))
        if mapped_lower >= 0 and mapped_lower != best.bone and not rig.bones[mapped_lower].weighted:
            diag.text += f"；名称表映射的 {rig.bones[mapped_lower].name} 没有权重"
        return diag

    above = [c for c in diag.candidates if c.median_t is not None and c.median_t > MEDIAN_HIGH]
    if above:
        best = above[0]
        diag.case = "C"
        diag.primary = -1
        diag.split_bone = best.bone
        diag.text = (f"情形C：{best.name} 同时覆盖下腹（中位高度 t={best.median_t:.2f}），"
                     f"按高度平滑切分出 下半身")
        return diag

    diag.case = "D"
    diag.split_bone = upper_body
    diag.text = (f"情形D：没有髋骨权重，从最低脊柱节 {rig.bones[upper_body].name} 按高度切分出 下半身，"
                 f"腿侧保留源权重")
    return diag
