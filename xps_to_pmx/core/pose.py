"""Rigid rest-pose edits computed in pure numpy (stage ③): T→A arms, facing flip, scale and ground.

Every edit is a rigid transform of a bone subtree.  ``plan_arm_pose`` turns
target angles into per-bone 4×4 transforms (descendants inherit their
ancestors'); ``blend_points`` applies them to vertices with linear blend
skinning, which is exactly what Blender's armature modifier would do, so the
same per-vertex matrix can be applied to the basis and to every shape key.

Coordinates: Blender armature space (Z up, model facing -Y, left at +X), metres.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

#: MMD export scale used everywhere (Blender metres → PMX units), as in the owner's pipeline.
EXPORT_SCALE = 12.5


def rotation_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Smallest rotation (3×3) turning direction ``a`` into direction ``b``."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    a = a / (np.linalg.norm(a) or 1.0)
    b = b / (np.linalg.norm(b) or 1.0)
    v = np.cross(a, b)
    c = float(np.dot(a, b))
    s = float(np.linalg.norm(v))
    if s < 1e-12:
        if c > 0:
            return np.eye(3)
        # opposite: rotate 180° about any axis perpendicular to a
        axis = np.cross(a, [1.0, 0.0, 0.0])
        if np.linalg.norm(axis) < 1e-6:
            axis = np.cross(a, [0.0, 1.0, 0.0])
        axis /= np.linalg.norm(axis)
        return axis_angle(axis, math.pi)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k * ((1 - c) / (s * s))


def axis_angle(axis: Sequence[float], angle: float) -> np.ndarray:
    axis = np.asarray(axis, float)
    axis = axis / (np.linalg.norm(axis) or 1.0)
    x, y, z = axis
    c, s, t = math.cos(angle), math.sin(angle), 1 - math.cos(angle)
    return np.array([[t * x * x + c, t * x * y - s * z, t * x * z + s * y],
                     [t * x * y + s * z, t * y * y + c, t * y * z - s * x],
                     [t * x * z - s * y, t * y * z + s * x, t * z * z + c]])


def rigid(rot: np.ndarray, pivot: np.ndarray) -> np.ndarray:
    """4×4 rotation ``rot`` about ``pivot``."""
    m = np.eye(4)
    m[:3, :3] = rot
    m[:3, 3] = pivot - rot @ pivot
    return m


def apply(m: np.ndarray, p: np.ndarray) -> np.ndarray:
    return m[:3, :3] @ p + m[:3, 3]


def down_angle(direction: np.ndarray) -> float:
    """Degrees below the horizontal plane (positive = pointing down)."""
    d = np.asarray(direction, float)
    n = float(np.linalg.norm(d))
    return math.degrees(math.asin(max(-1.0, min(1.0, -d[2] / n)))) if n > 1e-12 else 0.0


def forward_angle(direction: np.ndarray) -> float:
    """Degrees towards -Y (the front) out of the frontal XZ plane."""
    d = np.asarray(direction, float)
    n = float(np.linalg.norm(d))
    return math.degrees(math.asin(max(-1.0, min(1.0, -d[1] / n)))) if n > 1e-12 else 0.0


def arm_target_direction(side_sign: float, down_deg: float) -> np.ndarray:
    """Unit direction in the frontal plane, ``down_deg`` below horizontal, towards ``side_sign``·X."""
    r = math.radians(down_deg)
    return np.array([side_sign * math.cos(r), 0.0, -math.sin(r)])


@dataclass
class ArmPlan:
    side: str
    upper: int
    lower: int
    hand: int
    before_upper_deg: float = 0.0
    before_fore_deg: float = 0.0
    after_upper_deg: float = 0.0
    after_fore_deg: float = 0.0


@dataclass
class PosePlan:
    """Per-bone total transforms (bones not listed stay put) plus what was measured."""

    transforms: Dict[int, np.ndarray] = field(default_factory=dict)
    arms: List[ArmPlan] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def _descendants(parents: Sequence[int], root: int) -> List[int]:
    children: Dict[int, List[int]] = {}
    for i, p in enumerate(parents):
        children.setdefault(p, []).append(i)
    out, stack = [], [root]
    while stack:
        i = stack.pop()
        out.append(i)
        stack.extend(children.get(i, ()))
    return out


def plan_arm_pose(parents: Sequence[int], heads: np.ndarray, arms: Sequence[Tuple[str, int, int, int]],
                  upper_deg: float, fore_extra_deg: float = 0.0, tolerance_deg: float = 0.25) -> PosePlan:
    """Rotate each upper arm to ``upper_deg`` below horizontal (frontal plane) and the forearm to
    ``upper_deg + fore_extra_deg`` (0 = straight arm, 18-series; 10.56 = あにまさ ver.2.3).

    ``arms`` holds ``(side, upper, lower, hand)`` bone indices; the whole subtree of
    the upper arm follows, the forearm subtree follows its second rotation.
    """
    heads = np.asarray(heads, float)
    plan = PosePlan()
    total: Dict[int, np.ndarray] = {}
    for side, upper, lower, hand in arms:
        sign = 1.0 if side == "left" else -1.0
        a = ArmPlan(side, upper, lower, hand)
        d_up = heads[lower] - heads[upper]
        d_fore = heads[hand] - heads[lower]
        a.before_upper_deg, a.before_fore_deg = down_angle(d_up), down_angle(d_fore)
        target_up = arm_target_direction(sign, upper_deg)
        m_up = rigid(rotation_between(d_up, target_up), heads[upper])
        if _angle_deg(d_up, target_up) < tolerance_deg:
            m_up = np.eye(4)
        for b in _descendants(parents, upper):
            total[b] = m_up
        elbow = apply(m_up, heads[lower])
        wrist = apply(m_up, heads[hand])
        target_fore = arm_target_direction(sign, upper_deg + fore_extra_deg)
        if _angle_deg(wrist - elbow, target_fore) < tolerance_deg:
            m_fore = m_up
        else:
            m_fore = rigid(rotation_between(wrist - elbow, target_fore), elbow) @ m_up
        for b in _descendants(parents, lower):
            total[b] = m_fore
        a.after_upper_deg = down_angle(apply(m_up, heads[lower]) - apply(m_up, heads[upper]))
        a.after_fore_deg = down_angle(apply(m_fore, heads[hand]) - apply(m_fore, heads[lower]))
        plan.arms.append(a)
    plan.transforms = {b: m for b, m in total.items() if not np.allclose(m, np.eye(4), atol=1e-9)}
    return plan


def _angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, float) / (np.linalg.norm(a) or 1.0)
    b = np.asarray(b, float) / (np.linalg.norm(b) or 1.0)
    return math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(a, b))))))


def blend_matrices(bones: np.ndarray, weights: np.ndarray, transforms: Dict[int, np.ndarray]) -> np.ndarray:
    """Per-vertex blended 4×4 matrices (N, 4, 4); missing bones and unweighted vertices → identity."""
    n = bones.shape[0]
    out = np.zeros((n, 4, 4))
    total_w = np.zeros(n)
    for k in range(bones.shape[1]):
        b = bones[:, k]
        w = weights[:, k].astype(float)
        valid = (b >= 0) & (w > 0)
        if not valid.any():
            continue
        mats = np.repeat(np.eye(4)[None], n, axis=0)
        for bone in np.unique(b[valid]):
            m = transforms.get(int(bone))
            if m is not None:
                mats[b == bone] = m
        out += mats * (w * valid)[:, None, None]
        total_w += w * valid
    empty = total_w <= 1e-12
    out[empty] = np.eye(4)
    out[~empty] /= total_w[~empty, None, None]
    return out


def blend_points(points: np.ndarray, mats: np.ndarray) -> np.ndarray:
    pts = np.asarray(points, float)
    return np.einsum("nij,nj->ni", mats[:, :3, :3], pts) + mats[:, :3, 3]


def blend_directions(vectors: np.ndarray, mats: np.ndarray) -> np.ndarray:
    v = np.einsum("nij,nj->ni", mats[:, :3, :3], np.asarray(vectors, float))
    n = np.linalg.norm(v, axis=1, keepdims=True)
    return np.where(n > 1e-12, v / np.maximum(n, 1e-12), v)


# ---------------------------------------------------------------------------
# scale and ground

@dataclass
class ScalePlan:
    mode: str
    factor: float
    ground_z: float
    shoulder_z: float
    shoulder_pmx: float          # resulting shoulder height in PMX units
    height_pmx: float            # resulting model height in PMX units

    def matrix(self) -> np.ndarray:
        m = np.eye(4) * self.factor
        m[3, 3] = 1.0
        m[2, 3] = -self.ground_z * self.factor
        return m


def plan_scale(mode: str, shoulder_z: float, ground_z: float, top_z: float,
               shoulder_target_pmx: float = 17.0) -> ScalePlan:
    """``SHOULDER``: shoulder (腕 head) at ``shoulder_target_pmx`` after ×12.5 export (18 series);
    ``FIXED_125``: keep metres (export ×12.5); ``FIXED_10``: overall ×10 like the batch conversions."""
    span = shoulder_z - ground_z
    if mode == "SHOULDER":
        if span <= 1e-6:
            raise ValueError("shoulder is not above the ground")
        factor = shoulder_target_pmx / EXPORT_SCALE / span
    elif mode == "FIXED_125":
        factor = 1.0
    elif mode == "FIXED_10":
        factor = 10.0 / EXPORT_SCALE
    else:
        raise ValueError(f"unknown scale mode {mode!r}")
    return ScalePlan(mode, factor, ground_z, shoulder_z, span * factor * EXPORT_SCALE,
                     (top_z - ground_z) * factor * EXPORT_SCALE)


FLIP_180 = np.diag([-1.0, -1.0, 1.0, 1.0])


# ---------------------------------------------------------------------------
# geometry integrity (port of the owner's ROE ``mesh_distortion`` gate)

def edge_lengths(points: np.ndarray, edges: np.ndarray) -> np.ndarray:
    return np.linalg.norm(points[edges[:, 0]] - points[edges[:, 1]], axis=1)


def distortion(before: np.ndarray, after: np.ndarray, size: float, ratio_limit: float = 3.0,
               growth_fraction: float = 0.008) -> Dict[str, float]:
    """An edge is torn when it both multiplies (>3×) and grows by >0.8% of the model size.

    Ratios are normalised by their median so a uniform rescale reads as 1.0
    (measured on the ROE male base: wrist rip 7.0×/+33 mm, armpit fold 2.4×/+8 mm).
    """
    valid = before > 1e-9
    if not valid.any():
        return {"edges": 0, "torn": 0, "stretched": 0, "worst_ratio": 1.0, "worst_growth": 0.0}
    ratio = after[valid] / before[valid]
    median = float(np.median(ratio)) or 1.0
    scaled = before[valid] * median
    r = after[valid] / scaled
    growth = after[valid] - scaled
    limit = size * growth_fraction
    torn = int(((r > ratio_limit) & (growth > limit)).sum())
    worst = int(np.argmax(r))
    return {"edges": int(valid.sum()), "torn": torn, "stretched": int((np.abs(r - 1.0) > 0.25).sum()),
            "worst_ratio": float(r[worst]), "worst_growth": float(growth[worst]), "growth_limit": float(limit)}
