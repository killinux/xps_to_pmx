"""Pure-data snapshot of an armature and its skin weights (no bpy).

``RigData`` is what every analysis step works on.  It can be built offline from
:class:`ImportData` (tests run on real XPS files without Blender) or from a
Blender scene by ``blender/snapshot.py``.  Coordinates are Blender's (Z up,
model facing -Y, character's left side at +X).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


@dataclass
class RigBone:
    index: int
    name: str
    parent: int
    head: np.ndarray
    tail: np.ndarray
    src_name: str = ""
    children: List[int] = field(default_factory=list)
    weight_vertices: int = 0      # vertices with weight > 0
    weight_sum: float = 0.0

    @property
    def weighted(self) -> bool:
        return self.weight_vertices > 0

    @property
    def length(self) -> float:
        return float(np.linalg.norm(self.tail - self.head))


@dataclass
class SkinData:
    """All mesh vertices concatenated, with up to 4 (bone, weight) pairs each (bone -1 = empty)."""

    positions: np.ndarray      # (N, 3) float32
    bones: np.ndarray          # (N, 4) int32
    weights: np.ndarray        # (N, 4) float32
    #: ``(mesh object name, start, end)`` rows of each mesh (filled by ``blender/snapshot``)
    mesh_slices: Optional[List[Tuple[str, int, int]]] = None

    @property
    def count(self) -> int:
        return int(self.positions.shape[0])

    def bone_weight_column(self, bone: int) -> np.ndarray:
        """Per-vertex weight of one bone, shape (N,)."""
        return np.where(self.bones == bone, self.weights, 0.0).sum(axis=1)


class RigData:
    def __init__(self, bones: Sequence[RigBone], skin: Optional[SkinData] = None, source: str = ""):
        self.bones: List[RigBone] = list(bones)
        self.skin = skin
        self.source = source
        for b in self.bones:
            b.children = []
        for b in self.bones:
            if 0 <= b.parent < len(self.bones):
                self.bones[b.parent].children.append(b.index)
        self.by_name: Dict[str, int] = {}
        for b in self.bones:
            self.by_name.setdefault(b.name, b.index)
        self._subtree_cache: Dict[int, List[int]] = {}
        if skin is not None and skin.count:
            self._accumulate_weights()
        heads = np.array([b.head for b in self.bones]) if self.bones else np.zeros((0, 3))
        if skin is not None and skin.count:
            zmin, zmax = float(skin.positions[:, 2].min()), float(skin.positions[:, 2].max())
        elif len(heads):
            zmin, zmax = float(heads[:, 2].min()), float(heads[:, 2].max())
        else:
            zmin, zmax = 0.0, 1.0
        self.floor = zmin
        self.height = max(zmax - zmin, 1e-6)

    # -- construction -------------------------------------------------------

    @classmethod
    def from_import_data(cls, data) -> "RigData":
        """Build from :class:`xps_to_pmx.core.xps.convert.ImportData` (offline)."""
        bones = [RigBone(b.index, b.name, b.parent, np.array(b.head, float), np.array(b.tail, float), b.name)
                 for b in data.bones]
        meshes = [m for m in data.meshes if m.vertex_count]
        skin = None
        if meshes:
            skin = SkinData(np.concatenate([m.positions for m in meshes]),
                            np.concatenate([m.weight_bones for m in meshes]),
                            np.concatenate([m.weight_values for m in meshes]))
        return cls(bones, skin, data.source_path)

    def _accumulate_weights(self) -> None:
        bones = self.skin.bones.reshape(-1)
        weights = self.skin.weights.reshape(-1)
        mask = (bones >= 0) & (weights > 0)
        counts = np.bincount(bones[mask], minlength=len(self.bones))
        sums = np.bincount(bones[mask], weights=weights[mask], minlength=len(self.bones))
        for b in self.bones:
            if b.index < len(counts):
                b.weight_vertices = int(counts[b.index])
                b.weight_sum = float(sums[b.index])

    # -- queries --------------------------------------------------------------

    def __len__(self) -> int:
        return len(self.bones)

    def bone(self, name: str) -> Optional[RigBone]:
        idx = self.by_name.get(name)
        return None if idx is None else self.bones[idx]

    def roots(self) -> List[int]:
        return [b.index for b in self.bones if not (0 <= b.parent < len(self.bones))]

    def ancestors(self, index: int) -> List[int]:
        """Parent chain from the direct parent up to the root."""
        out, seen = [], set()
        cur = self.bones[index].parent
        while 0 <= cur < len(self.bones) and cur not in seen:
            out.append(cur)
            seen.add(cur)
            cur = self.bones[cur].parent
        return out

    def is_ancestor(self, ancestor: int, index: int) -> bool:
        return ancestor in self.ancestors(index)

    def subtree(self, index: int) -> List[int]:
        """The bone and all its descendants (cached)."""
        cached = self._subtree_cache.get(index)
        if cached is not None:
            return cached
        out, stack = [], [index]
        while stack:
            i = stack.pop()
            out.append(i)
            stack.extend(self.bones[i].children)
        self._subtree_cache[index] = out
        return out

    def subtree_weighted(self, index: int) -> bool:
        return any(self.bones[i].weighted for i in self.subtree(index))

    def lca(self, a: int, b: int) -> int:
        chain_a = [a] + self.ancestors(a)
        chain_b = set([b] + self.ancestors(b))
        for i in chain_a:
            if i in chain_b:
                return i
        return -1

    def path_down(self, ancestor: int, index: int) -> List[int]:
        """Bones from just below ``ancestor`` down to ``index`` (inclusive); [] if not a descendant."""
        chain = [index] + self.ancestors(index)
        if ancestor not in chain:
            return []
        return list(reversed(chain[: chain.index(ancestor)]))

    def heads(self, indices: Iterable[int]) -> np.ndarray:
        return np.array([self.bones[i].head for i in indices]) if indices else np.zeros((0, 3))

    def rel_z(self, index: int) -> float:
        """Head height as a fraction of model height above the floor."""
        return (float(self.bones[index].head[2]) - self.floor) / self.height

    def centre_eps(self) -> float:
        return 0.01 * self.height
