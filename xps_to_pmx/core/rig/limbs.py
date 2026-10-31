"""Limb segments and where a bone's weights lie along them (design doc §15.5, §15.7).

A segment runs from one limb slot's head to the next one's (thigh → knee …).
:func:`segment_mass` assigns every vertex a bone influences to the nearest
segment of that side and sums the bone's weight per segment.  Vertices whose
closest point lies within ``JOINT_ZONE`` of either end of their segment are
left out: they sit on a joint and belong to both sides of it.  Measured on
rouffe and the regression models (2026-10-31): helpers that really belong to
the next segment have ≥ 70 % of their weight outside joint zones and ≈ 100 %
of that in one segment; helpers that straddle a joint have most of their
weight inside the joint zone.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from .rigdata import RigData

#: (start slot, end slot) without the side prefix.  The order is the classifier's
#: tie-break order for helpers whose head is equally close to two segments.
LIMB_SEGMENTS: Tuple[Tuple[str, str], ...] = (
    ("upper_arm_bone", "lower_arm_bone"),
    ("lower_arm_bone", "hand_bone"),
    ("shoulder_bone", "upper_arm_bone"),
    ("thigh_bone", "knee_bone"),
    ("knee_bone", "ankle_bone"),
    ("ankle_bone", "toe_bone"),
)
JOINT_ZONE = 0.10      # fraction of a segment at each end that counts as "on the joint"
DECISIVE_MIN = 0.5     # share of a bone's weight that must lie clearly inside segments
DOMINANT_MIN = 0.8     # share of that decisive weight that must lie in one segment


@dataclass
class Segment:
    slot: str            # start slot with side, e.g. "left_thigh_bone"; helpers merge into this slot
    end_slot: str        # e.g. "left_knee_bone"
    side: str            # "left" | "right"
    start_bone: int
    end_bone: int
    a: np.ndarray        # start head
    c: np.ndarray        # end head

    @property
    def length(self) -> float:
        return float(np.linalg.norm(self.c - self.a))


@dataclass
class SegmentMass:
    """Weight of one bone per segment, counted only outside joint zones."""

    fractions: Dict[str, float] = field(default_factory=dict)   # segment slot → share of the decisive weight
    decisive: float = 0.0       # decisive weight / total weight of the bone
    total: float = 0.0          # total weight of the bone (sum over vertices)
    vertices: int = 0

    def dominant(self) -> Tuple[str, float]:
        if not self.fractions:
            return "", 0.0
        slot = max(self.fractions, key=self.fractions.get)
        return slot, self.fractions[slot]

    def clear_owner(self) -> Optional[str]:
        """The segment that clearly holds this bone's weight, or None when the evidence is weak."""
        slot, frac = self.dominant()
        if slot and self.decisive >= DECISIVE_MIN and frac >= DOMINANT_MIN:
            return slot
        return None

    def as_dict(self) -> Dict:
        return {"fractions": {k: round(v, 4) for k, v in self.fractions.items()},
                "decisive": round(self.decisive, 4), "total": round(self.total, 4), "vertices": self.vertices}

    @classmethod
    def from_dict(cls, data: Dict) -> "SegmentMass":
        return cls(dict(data.get("fractions", {})), float(data.get("decisive", 0.0)),
                   float(data.get("total", 0.0)), int(data.get("vertices", 0)))


def limb_segments(rig: RigData, slot_bones: Dict[str, int], side: str) -> List[Segment]:
    """The mapped segments of one side, in :data:`LIMB_SEGMENTS` order."""
    out = []
    for a_key, c_key in LIMB_SEGMENTS:
        a, c = slot_bones.get(f"{side}_{a_key}", -1), slot_bones.get(f"{side}_{c_key}", -1)
        if a >= 0 and c >= 0:
            out.append(Segment(f"{side}_{a_key}", f"{side}_{c_key}", side, a, c,
                               np.asarray(rig.bones[a].head, float), np.asarray(rig.bones[c].head, float)))
    return out


def project(points: np.ndarray, a: np.ndarray, c: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Parameter ``t`` along a→c (unclipped) and distance to the clipped segment, per point."""
    ab = c - a
    denom = max(float(ab @ ab), 1e-12)
    t = ((points - a) @ ab) / denom
    closest = a + np.clip(t, 0.0, 1.0)[:, None] * ab
    return t, np.linalg.norm(points - closest, axis=1)


def segment_mass(rig: RigData, bone: int, segments: Sequence[Segment]) -> Optional[SegmentMass]:
    """Where ``bone``'s weights lie along ``segments``; None without skin data, weights or segments."""
    if rig.skin is None or not segments:
        return None
    w = rig.skin.bone_weight_column(bone)
    mask = w > 0
    if not mask.any():
        return None
    pts = rig.skin.positions[mask].astype(float)
    ww = w[mask].astype(float)
    ts, ds = zip(*(project(pts, s.a, s.c) for s in segments))
    t = np.stack(ts, axis=1)
    owner = np.stack(ds, axis=1).argmin(axis=1)
    t_own = t[np.arange(len(owner)), owner]
    decisive = (t_own > JOINT_ZONE) & (t_own < 1.0 - JOINT_ZONE)
    mass = np.bincount(owner[decisive], weights=ww[decisive], minlength=len(segments))
    total = float(ww.sum())
    dec = float(mass.sum())
    fractions = {s.slot: float(m / dec) for s, m in zip(segments, mass)} if dec > 0 else {}
    return SegmentMass(fractions, dec / total if total > 0 else 0.0, total, int(mask.sum()))
