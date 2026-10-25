"""Synthetic humanoid rigs for offline tests (Blender coordinates, metres, T-pose, facing -Y)."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from xps_to_pmx.core.rig.rigdata import RigBone, RigData, SkinData

# name -> (parent, head)
BASE: List[Tuple[str, str, Tuple[float, float, float]]] = [
    ("root ground", "", (0, 0, 0)),
    ("root hips", "root ground", (0, 0, 1.00)),
    ("pelvis", "root hips", (0, 0, 1.00)),
    ("spine lower", "root hips", (0, 0, 1.05)),
    ("spine middle", "spine lower", (0, 0, 1.15)),
    ("spine upper", "spine middle", (0, 0, 1.25)),
    ("head neck lower", "spine upper", (0, 0, 1.45)),
    ("head neck upper", "head neck lower", (0, 0, 1.54)),
    ("head eyeball left", "head neck upper", (0.03, -0.08, 1.60)),
    ("head eyeball right", "head neck upper", (-0.03, -0.08, 1.60)),
    ("head jaw", "head neck upper", (0, -0.03, 1.56)),
]


def _arm(side: str, sign: float):
    s = side
    rows = [
        (f"arm {s} shoulder 1", "spine upper", (0.03 * sign, 0, 1.41)),
        (f"arm {s} shoulder 2", f"arm {s} shoulder 1", (0.14 * sign, 0, 1.41)),
        (f"arm {s} elbow", f"arm {s} shoulder 2", (0.35 * sign, 0, 1.41)),
        (f"arm {s} wrist", f"arm {s} elbow", (0.56 * sign, 0, 1.41)),
    ]
    finger_y = {1: -0.03, 2: -0.015, 3: 0.0, 4: 0.015, 5: 0.03}
    for f in range(1, 6):
        x0 = 0.58 if f == 1 else 0.635
        z0 = 1.40 if f == 1 else 1.41
        parent = f"arm {s} wrist"
        for k, letter in enumerate("abc"):
            name = f"arm {s} finger {f}{letter}"
            rows.append((name, parent, ((x0 + 0.022 * k) * sign, finger_y[f] - (0.01 * k if f == 1 else 0), z0)))
            parent = name
    return rows


def _leg(side: str, sign: float):
    s = side
    return [
        (f"leg {s} thigh", "pelvis", (0.085 * sign, 0, 0.99)),
        (f"leg {s} knee", f"leg {s} thigh", (0.083 * sign, 0, 0.55)),
        (f"leg {s} ankle", f"leg {s} knee", (0.081 * sign, 0, 0.12)),
        (f"leg {s} toes", f"leg {s} ankle", (0.078 * sign, -0.12, 0.02)),
    ]


def build(rename: Optional[Dict[str, str]] = None, drop: Tuple[str, ...] = (), extra=(),
          lower_case: str = "A") -> RigData:
    """Build a rig; ``lower_case`` shapes the hip weights: "A" clean pelvis, "C" pelvis covers the
    belly, "D" no pelvis weights (spine lower covers the hips)."""
    rows = BASE + _arm("left", 1) + _arm("right", -1) + _leg("left", 1) + _leg("right", -1) + list(extra)
    rename = rename or {}
    rows = [r for r in rows if r[0] not in drop]
    names = [r[0] for r in rows]
    index = {n: i for i, n in enumerate(names)}
    bones = []
    for i, (name, parent, head) in enumerate(rows):
        p = index.get(parent, -1)
        while p < 0 and parent and parent in drop:  # re-parent through dropped bones
            parent = next(r[1] for r in BASE + _arm("left", 1) + _arm("right", -1) + _leg("left", 1)
                          + _leg("right", -1) if r[0] == parent)
            p = index.get(parent, -1)
        kids = [j for j, r in enumerate(rows) if r[1] == name]
        head = np.array(head, float)
        tail = np.array(rows[kids[0]][2], float) if kids else head + np.array([0, 0, 0.05])
        if np.linalg.norm(tail - head) < 0.005:
            tail = head + np.array([0, 0, 0.05])
        bones.append(RigBone(i, rename.get(name, name), p, head, tail, rename.get(name, name)))
    skin = _skin(bones, rows, lower_case)
    return RigData(bones, skin, "synthetic")


def _skin(bones, rows, lower_case):
    pts, bidx = [], []
    rng = np.random.default_rng(0)
    for b in bones:
        name = rows[b.index][0]
        if name in ("root ground", "root hips") or name.startswith(("head eyeball", "unused")):
            continue
        if name == "pelvis":
            if lower_case == "D":
                continue
            top = 1.05 if lower_case == "A" else 1.30
            n = 400
            z = rng.uniform(0.92, top, n)
            xy = rng.normal(0, 0.06, (n, 2))
            pts.append(np.column_stack([xy[:, 0], xy[:, 1], z]))
            bidx.append(np.full(n, b.index))
            continue
        if name == "spine lower" and lower_case == "D":
            n = 600
            z = rng.uniform(0.92, 1.15, n)
            xy = rng.normal(0, 0.06, (n, 2))
            pts.append(np.column_stack([xy[:, 0], xy[:, 1], z]))
            bidx.append(np.full(n, b.index))
            continue
        n = 60
        t = rng.uniform(0, 1, n)[:, None]
        seg = b.head + t * (b.tail - b.head) + rng.normal(0, 0.01, (n, 3))
        pts.append(seg)
        bidx.append(np.full(n, b.index))
    positions = np.concatenate(pts).astype(np.float32)
    bones_arr = np.full((len(positions), 4), -1, np.int32)
    weights = np.zeros((len(positions), 4), np.float32)
    bones_arr[:, 0] = np.concatenate(bidx)
    weights[:, 0] = 1.0
    return SkinData(positions, bones_arr, weights)
