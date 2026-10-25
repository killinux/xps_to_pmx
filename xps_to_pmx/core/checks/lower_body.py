"""下半身 acceptance checks on the planned weights (design doc §6; note 11 §5.4).

Measured on the 18-series reference (Purifier Inase → Inase18): Σw/nV 0.48,
w>0.5 median between 足 and 上半身, nothing above t = 1.75, side 50/50 at
t ≈ 0, centre ≥ 0.8 for |t| < 0.5.  Game rigs deviate (UE pelvises reach over
the buttocks, lezisell pelvises into the belly), so everything here is a
warning with the measured value, never a blocker.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np

from .mapping import CheckItem

HIGH_T = 1.75
HIGH_MASS_LIMIT = 0.02        # share of 下半身 weight allowed above t = 1.75
MEDIAN_RANGE = (-1.5, 1.3)    # in units of L around 足 (UE pelvises sit at ≈ -1.1)
CENTRE_MIN = 0.6
SIDE_RANGE = (0.2, 0.8)


def lower_body_metrics(positions: np.ndarray, lower: np.ndarray, upper: np.ndarray, legs: np.ndarray,
                       thigh_z: float, waist_z: float, thigh_x: float) -> Dict[str, float]:
    seg = waist_z - thigh_z
    if seg <= 1e-9:
        return {}
    t = (positions[:, 2] - thigh_z) / seg
    x = np.abs(positions[:, 0])
    total = float(lower.sum())
    nv = int((lower > 0).sum())
    strong = lower > 0.5
    out = {"vertices": nv, "sum": round(total, 2),
           "sum_per_vertex": round(total / nv, 3) if nv else 0.0,
           "median_t": round(float(np.median(t[strong])), 3) if strong.any() else float("nan"),
           "high_mass": round(float(lower[t >= HIGH_T].sum()) / total, 4) if total > 0 else 0.0,
           "overlap_legs": int(((lower > 0.01) & (legs > 0.01)).sum())}
    side = (np.abs(t) < 0.25) & (x > 1.2 * thigh_x) & ((lower + legs) > 0.5)
    if side.any():
        out["side_share"] = round(float(np.mean(lower[side] / np.maximum(lower[side] + legs[side], 1e-9))), 3)
    centre = (np.abs(t) < 0.5) & (x < 0.3 * thigh_x) & ((lower + upper + legs) > 0.5)
    if centre.any():
        share = lower[centre] / np.maximum(lower[centre] + upper[centre] + legs[centre], 1e-9)
        out["centre_share"] = round(float(np.median(share)), 3)
    return out


def check_lower_body(m: Dict[str, float], name: str = "下半身") -> List[CheckItem]:
    items: List[CheckItem] = []

    def warn(code: str, text: str) -> None:
        items.append(CheckItem("warning", code, text, "lower_body_bone", name))

    if not m or not m.get("vertices"):
        warn("lower_body.no_weight", f"{name} 没有权重，腰部会随 上半身/足 撕裂")
        return items
    if m["high_mass"] > HIGH_MASS_LIMIT:
        warn("lower_body.high", f"{name} 有 {m['high_mass'] * 100:.1f}% 的权重在腰节以上 1.75L 处（18 系列为 0），"
                                f"弯腰/扭腰时腹部会跟着 {name} 走")
    med = m.get("median_t")
    if med is not None and not (MEDIAN_RANGE[0] <= med <= MEDIAN_RANGE[1]):
        warn("lower_body.median", f"{name} 主权重（w>0.5）的中位高度 t={med:+.2f}，不在 [{MEDIAN_RANGE[0]}, "
                                  f"{MEDIAN_RANGE[1]}] 内")
    centre = m.get("centre_share")
    if centre is not None and centre < CENTRE_MIN:
        warn("lower_body.centre", f"正中髋部 {name} 只占 {centre:.2f}（18 系列 ≥0.8）")
    side = m.get("side_share")
    if side is not None and not (SIDE_RANGE[0] <= side <= SIDE_RANGE[1]):
        warn("lower_body.side", f"股关节侧面 {name}/足 = {side:.2f}/{1 - side:.2f}（18 系列约各半）")
    if m.get("overlap_legs", 0) == 0:
        warn("lower_body.hard_cut", f"{name} 与腿骨之间没有过渡权重（硬切），抬腿时髋部会断开")
    return items
