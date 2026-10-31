"""Split one bone's weights by side (fix kind ``split_side``, design doc §15.3).

Used for duplicate source bone names: the file's vertices all reference the
first copy, so the copy on the other side moves nothing.  The weight of every
vertex on the twin's side of the centre line moves to the twin; within
``margin`` of the centre line it changes linearly so the seam stays smooth.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np


def side_fraction(x: np.ndarray, twin_side: float, margin: float) -> np.ndarray:
    """Share of the weight that goes to the twin, per vertex x (0 on the bone's side, 1 on the twin's)."""
    s = 1.0 if twin_side > 0 else -1.0
    if margin <= 0:
        return (x * s > 0).astype(float)
    return np.clip(0.5 + s * np.asarray(x, float) / (2.0 * margin), 0.0, 1.0)


def split_by_side(x: np.ndarray, weights: np.ndarray, twin_side: float, margin: float
                  ) -> Tuple[np.ndarray, np.ndarray]:
    """Weights that stay on the bone and weights that go to the twin; their sum equals ``weights``."""
    f = side_fraction(x, twin_side, margin)
    w = np.asarray(weights, float)
    return w * (1.0 - f), w * f
