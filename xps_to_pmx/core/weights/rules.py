"""Weight-split rules of stage ④ as pure functions of vertex positions (design doc §6, §8.2).

Each rule returns per-vertex *shares* (0..1) of one source bone's weight that
go to the generated bones; :class:`~xps_to_pmx.core.weights.skin.SkinEditor`
applies them.  Coordinates are Blender armature space (Z up, front = -Y).
"""
from __future__ import annotations

from typing import Tuple

import numpy as np

from ..rig.lower_body import split_factor
from .skin import ramp, segment_param

#: 18-series stepped twist bands (note 11 §6.2, Inase18/Reika18 profiles): the
#: weight of 腕 (or ひじ) steps through 捩1 → 捩2 → 捩3 → 捩 at these positions
#: along the segment, each step a linear ramp of ±``TWIST_STEP_HALF``.
TWIST_STEPS = (0.25, 0.43, 0.60, 0.76)
TWIST_STEP_HALF = 0.06
#: Smooth variant = semi-standard-bone plugin (plugin_ssb ``addTwistBone``):
#: linear between twist levels 0 / ¼ / ½ / ¾ / 1 at these positions.
TWIST_SMOOTH = (0.12, 0.32, 0.52, 0.72, 0.92)
TWIST_MODES = ("STEPPED", "SMOOTH")

#: plugin_ssb 上半身2: ±0.35 band around the new joint, backs count 50% higher.
UPPER2_BAND = 0.35
UPPER2_BACK_LIFT = 0.5

#: plugin_ssb 足先EX: share = clamp((c − 0.75) × 2) with c the forward progress ankle → 足先EX.
TOE_EX_START = 0.75
TOE_EX_GAIN = 2.0


def twist_shares(s: np.ndarray, mode: str = "STEPPED") -> np.ndarray:
    """(N, 5) shares of [segment bone, 捩1, 捩2, 捩3, 捩] at segment parameter ``s``; rows sum to 1."""
    s = np.asarray(s, dtype=np.float64)
    if mode == "STEPPED":
        cum = [ramp(s, c - TWIST_STEP_HALF, c + TWIST_STEP_HALF) for c in TWIST_STEPS]
    elif mode == "SMOOTH":
        p = TWIST_SMOOTH
        cum = [ramp(s, p[k], p[k + 1]) for k in range(4)]
    else:
        raise ValueError(f"unknown twist mode {mode!r}")
    cum = [np.ones_like(s)] + cum + [np.zeros_like(s)]
    return np.stack([cum[k] - cum[k + 1] for k in range(5)], axis=1)


def twist_segment_shares(points: np.ndarray, start: np.ndarray, end: np.ndarray, mode: str) -> np.ndarray:
    return twist_shares(segment_param(points, start, end), mode)


def upper_body2_share(points: np.ndarray, origin: np.ndarray, neck: np.ndarray) -> np.ndarray:
    """Share of 上半身 weight that moves to a generated 上半身2 placed at ``origin`` (below ``neck``)."""
    span = float(neck[2] - origin[2])
    if span <= 1e-9:
        return np.zeros(len(points))
    d = np.asarray(points, float) - origin
    lifted = d[:, 2] + UPPER2_BACK_LIFT * np.maximum(d[:, 1], 0.0)
    v = lifted / span
    return np.clip((v + UPPER2_BAND) / (2 * UPPER2_BAND), 0.0, 1.0)


def lower_body_share(points: np.ndarray, thigh_z: float, seg_l: float) -> np.ndarray:
    """Share of the split bone's weight that becomes 下半身 (S(t), t = (z − 足) / L; design doc §6 case C/D)."""
    if seg_l <= 1e-9:
        return np.zeros(len(points))
    t = (np.asarray(points, float)[:, 2] - thigh_z) / seg_l
    return split_factor(t)


def toe_ex_share(points: np.ndarray, ankle: np.ndarray, toe_ex: np.ndarray) -> np.ndarray:
    """Share of 足首(D) weight that goes to 足先EX (forward progress along -Y towards the 足先EX head)."""
    span = float(toe_ex[1] - ankle[1])
    if abs(span) <= 1e-9:
        return np.zeros(len(points))
    c = (np.asarray(points, float)[:, 1] - ankle[1]) / span
    return np.clip((c - TOE_EX_START) * TOE_EX_GAIN, 0.0, 1.0)


def band_summary(s: np.ndarray, shares: np.ndarray, edges: Tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0)):
    """Mean shares per s-band (for reports / tests)."""
    out = []
    for lo, hi in zip(edges, edges[1:]):
        m = (s >= lo) & (s < hi)
        out.append(shares[m].mean(axis=0) if m.any() else np.zeros(shares.shape[1]))
    return np.array(out)
