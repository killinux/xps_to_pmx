"""Split one bone's weights by side (fix kind ``split_side``, design doc §15.3).

Used for duplicate source bone names: the file's vertices all reference the
first copy, so the copy on the other side moves nothing.  The weight of every
vertex on the twin's side of the centre line moves to the twin; within
``margin`` of the centre line it changes linearly so the seam stays smooth.

The same files resolve parents by name too: rouffe's right ``shawl back right 2``
hangs from the *left* ``shawl back right 1``, so after the split the right half
still followed the left shoulder (found by the shrug pose test, 2026-10-31).
:func:`twin_parent` finds the parent's namesake on the twin's side.
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple

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


def twin_parent(twin_x: float, parent: str, parent_x: float, namesakes: Sequence[Tuple[str, float]],
                margin: float) -> Optional[str]:
    """The bone the twin should hang from, when its parent sits on the other side and has a namesake.

    ``namesakes``: (name, head x) of the bones whose source name equals the parent's.  Returns the
    namesake on the twin's side closest to the parent's mirror position, or None when nothing changes.
    """
    s = 1.0 if twin_x > 0 else -1.0
    if parent_x * s >= -margin:      # parent on the twin's side or on the centre line
        return None
    best = sorted((abs(x + parent_x), name) for name, x in namesakes if name != parent and x * s > margin)
    return best[0][1] if best else None
