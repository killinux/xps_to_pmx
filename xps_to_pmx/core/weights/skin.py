"""Vectorised skin-weight editing on the top-K ``(bone, weight)`` representation (no bpy).

Every vertex carries up to K influences (bone index -1 = empty slot).  The
editor only ever *moves* weight between bones, so the per-vertex total is
conserved by construction; :meth:`SkinEditor.compact` then merges duplicates,
drops dust, caps the influence count and renormalises (design doc §8.2 收尾).
"""
from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple

import numpy as np

#: Weights below this are dust and removed when compacting (design doc §8.2).
MIN_WEIGHT = 0.001
#: PMX BDEF4 / mmd_tools export limit.
MAX_INFLUENCES = 4


class SkinEditor:
    def __init__(self, bones: np.ndarray, weights: np.ndarray):
        self.bones = np.array(bones, dtype=np.int32, copy=True)
        self.weights = np.array(weights, dtype=np.float64, copy=True)
        self.weights[self.bones < 0] = 0.0
        self.bones[self.weights <= 0] = -1

    @property
    def count(self) -> int:
        return int(self.bones.shape[0])

    # -- queries --------------------------------------------------------------

    def column(self, bone: int) -> np.ndarray:
        """Per-vertex weight of ``bone``."""
        return np.where(self.bones == bone, self.weights, 0.0).sum(axis=1)

    def totals(self) -> np.ndarray:
        return self.weights.sum(axis=1)

    def bone_totals(self, n_bones: int) -> np.ndarray:
        mask = self.bones >= 0
        return np.bincount(self.bones[mask], weights=self.weights[mask], minlength=n_bones)

    # -- edits ----------------------------------------------------------------

    def remap(self, mapping: Dict[int, int]) -> None:
        """Rename bone indices (several sources may map to one target; duplicates merge on compact)."""
        if not mapping:
            return
        out = self.bones.copy()
        for src, dst in mapping.items():
            out[self.bones == src] = dst
        self.bones = out
        self.weights[self.bones < 0] = 0.0

    def transfer(self, src: int, dst: int, factor: Optional[np.ndarray] = None) -> float:
        """Move ``factor`` (per vertex, 0..1; default all) of ``src``'s weight to ``dst``. Returns the moved sum."""
        if src == dst:
            return 0.0
        if factor is None:
            moved = float(self.column(src).sum())
            self.bones[self.bones == src] = dst
            return moved
        return self.split(src, [(dst, factor)])

    def split(self, src: int, parts: Sequence[Tuple[int, np.ndarray]]) -> float:
        """Redistribute ``src``'s weight: part ``k`` gets ``w * f_k``; whatever the factors leave stays on ``src``.

        Factors are clipped to [0, 1] and, if they add up to more than 1 on a
        vertex, scaled down so that weight is never created.
        """
        if not parts:
            return 0.0
        f = np.stack([np.clip(np.asarray(fk, dtype=np.float64), 0.0, 1.0) for _, fk in parts], axis=1)
        total = f.sum(axis=1, keepdims=True)
        f = np.where(total > 1.0, f / np.maximum(total, 1e-12), f)
        w = self.column(src)
        rows = np.nonzero(w > 0)[0]
        if not len(rows):
            return 0.0
        moved = 0.0
        new_b, new_w = [], []
        for k, (dst, _) in enumerate(parts):
            share = w[rows] * f[rows, k]
            keep = share > 0
            if dst == src or not keep.any():
                continue
            col_b = np.full(self.count, -1, dtype=np.int32)
            col_w = np.zeros(self.count)
            col_b[rows[keep]] = dst
            col_w[rows[keep]] = share[keep]
            new_b.append(col_b)
            new_w.append(col_w)
            moved += float(share[keep].sum())
        stay = 1.0 - sum(f[:, k] for k, (dst, _) in enumerate(parts) if dst != src)
        here = self.bones == src
        self.weights = np.where(here, self.weights * stay[:, None], self.weights)
        if new_b:
            self.bones = np.concatenate([self.bones, np.stack(new_b, axis=1)], axis=1)
            self.weights = np.concatenate([self.weights, np.stack(new_w, axis=1)], axis=1)
        return moved

    # -- finishing ------------------------------------------------------------

    def compact(self, max_influences: int = MAX_INFLUENCES, min_weight: float = MIN_WEIGHT) -> Dict[str, int]:
        """Merge duplicate bones per vertex, drop dust, keep the strongest ``max_influences``, renormalise.

        Vertices whose weight is all dust keep their single strongest influence.
        Returns counts of vertices that lost influences to the cap / to dust.
        """
        n, k = self.bones.shape
        b = np.where(self.weights > 0, self.bones, -1)
        w = np.where(b >= 0, self.weights, 0.0)
        # merge duplicates: sort by bone per row, sum runs of equal bones
        order = np.argsort(b, axis=1, kind="stable")
        b = np.take_along_axis(b, order, axis=1)
        w = np.take_along_axis(w, order, axis=1)
        for j in range(1, k):
            same = (b[:, j] == b[:, j - 1]) & (b[:, j] >= 0)
            w[same, j] += w[same, j - 1]
            w[same, j - 1] = 0.0
            b[same, j - 1] = -1
        before_total = w.sum(axis=1)
        strongest = np.argmax(w, axis=1)
        dust = (w > 0) & (w < min_weight)
        all_dust = before_total > 0
        all_dust &= ~((w >= min_weight).any(axis=1))
        dust[np.arange(n)[all_dust], strongest[all_dust]] = False
        dust_rows = int(dust.any(axis=1).sum())
        w[dust] = 0.0
        b[w <= 0] = -1
        # strongest first
        order = np.argsort(-w, axis=1, kind="stable")
        b = np.take_along_axis(b, order, axis=1)
        w = np.take_along_axis(w, order, axis=1)
        capped_rows = int((w[:, max_influences:] > 0).any(axis=1).sum()) if k > max_influences else 0
        b, w = b[:, :max_influences], w[:, :max_influences]
        if b.shape[1] < max_influences:
            pad = max_influences - b.shape[1]
            b = np.concatenate([b, np.full((n, pad), -1, dtype=np.int32)], axis=1)
            w = np.concatenate([w, np.zeros((n, pad))], axis=1)
        total = w.sum(axis=1, keepdims=True)
        w = np.where(total > 0, w / np.maximum(total, 1e-12), 0.0)
        self.bones = b.astype(np.int32)
        self.weights = w
        return {"capped": capped_rows, "dust": dust_rows}

    def arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        return self.bones.copy(), self.weights.astype(np.float32)


def changed_rows(old_bones: np.ndarray, old_weights: np.ndarray, new_bones: np.ndarray, new_weights: np.ndarray,
                 tol: float = 1e-5) -> np.ndarray:
    """Indices of vertices whose influence set differs (order-insensitive); used to limit Blender writes."""

    def canon(b, w):
        b = np.where(w > 0, b, -1)
        order = np.argsort(b, axis=1, kind="stable")
        return np.take_along_axis(b, order, axis=1), np.take_along_axis(np.where(b >= 0, w, 0.0), order, axis=1)

    k = max(old_bones.shape[1], new_bones.shape[1])

    def pad(b, w):
        if b.shape[1] < k:
            extra = k - b.shape[1]
            b = np.concatenate([b, np.full((b.shape[0], extra), -1, dtype=b.dtype)], axis=1)
            w = np.concatenate([w, np.zeros((w.shape[0], extra), dtype=w.dtype)], axis=1)
        return b, w

    ob, ow = canon(*pad(old_bones, old_weights))
    nb, nw = canon(*pad(new_bones, new_weights))
    differ = (ob != nb).any(axis=1) | (np.abs(ow - nw) > tol).any(axis=1)
    return np.nonzero(differ)[0]


def segment_param(points: np.ndarray, start: np.ndarray, end: np.ndarray) -> np.ndarray:
    """Projection parameter of ``points`` on the segment start→end (0 at start, 1 at end, unclamped)."""
    d = np.asarray(end, float) - np.asarray(start, float)
    dd = float(d @ d)
    if dd <= 1e-18:
        return np.zeros(len(points))
    return (np.asarray(points, float) - start) @ d / dd


def ramp(x: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """0 below ``lo``, 1 above ``hi``, linear in between."""
    if hi <= lo:
        return (np.asarray(x) >= hi).astype(float)
    return np.clip((np.asarray(x, float) - lo) / (hi - lo), 0.0, 1.0)

