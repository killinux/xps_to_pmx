"""Turn an :class:`XpsModel` into import-ready arrays in Blender coordinates.

Pure Python + numpy (no bpy), so the whole conversion is testable offline on
real files.  Conventions (see note 01 of the research notes):

* positions / normals: XNA (+X right, +Y up, +Z towards the viewer) to Blender
  (+Z up, model facing -Y): ``(x, y, z) -> (x, -z, y)`` -- a pure rotation;
* faces: DirectX front faces are clockwise, Blender's counter-clockwise, so
  every triangle ``(a, b, c)`` becomes ``(a, c, b)``;
* UVs: ``v -> 1 - v``;
* weights: invalid indices and zero weights dropped, duplicate bones merged,
  the 4 largest kept and re-normalised to sum 1 (PMX BDEF limit);
* bone tails do not exist in XPS; :func:`compute_tails` derives them.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .render_groups import BUMP, RenderGroupInfo, describe_render_group
from .types import XpsMesh, XpsModel

#: Shortest bone Blender keeps (zero-length bones are deleted on leaving edit mode).
MIN_BONE_LENGTH = 0.005
#: PMX BDEF4 limit.
MAX_INFLUENCES = 4

#: Helper bones that should not decide where their parent's tail points.
_HELPER_RE = re.compile(r"(twist|adj|ctr|unused|helper|xtra|muscle|_end$|\bend\b)", re.IGNORECASE)
#: File stems too generic to name a model; the folder name is used instead.
_GENERIC_STEMS = {"xps", "generic_item", "model", "normal pose", "t-pose", "tpose", "a-pose", "apose",
                  "default", "mesh"}


def xna_to_blender(points: np.ndarray) -> np.ndarray:
    """Rotate ``(N, 3)`` XNA coordinates into Blender coordinates."""
    pts = np.asarray(points, dtype=np.float64)
    out = np.empty_like(pts)
    out[..., 0] = pts[..., 0]
    out[..., 1] = -pts[..., 2]
    out[..., 2] = pts[..., 1]
    return out


def model_display_name(path: str) -> str:
    """Readable model name: the file stem, or the folder name when the stem is generic (``xps.xps``)."""
    stem = os.path.basename(path)
    lower = stem.lower()
    for ext in (".mesh.ascii", ".xps", ".mesh", ".ascii"):
        if lower.endswith(ext):
            stem = stem[: -len(ext)]
            break
    if stem.strip().lower() in _GENERIC_STEMS or not stem.strip():
        parent = os.path.basename(os.path.dirname(os.path.abspath(path)))
        return parent or stem or "xps_model"
    return stem


@dataclass
class ImportBone:
    index: int
    name: str
    parent: int
    head: Tuple[float, float, float]
    tail: Tuple[float, float, float]


@dataclass
class ImportTexture:
    slot: int
    role: str
    file: str
    raw_path: str
    uv_layer: int
    path: Optional[str]

    @property
    def found(self) -> bool:
        return self.path is not None


@dataclass
class WeightStats:
    vertices: int = 0
    renormalized: int = 0
    truncated: int = 0
    unweighted: int = 0
    invalid_refs: int = 0
    max_influences: int = 0


@dataclass
class ImportMesh:
    index: int
    raw_name: str
    base_name: str
    join_name: str
    material_key: str
    render_group: Optional[int]
    rg_info: RenderGroupInfo
    specular: float
    bump_repeat1: float
    bump_repeat2: float
    optional_visible: Optional[bool]
    optional_group: Optional[str]
    optional_item: Optional[str]
    optional_part: Optional[str]
    positions: np.ndarray
    normals: np.ndarray
    uvs: List[np.ndarray]
    colors: np.ndarray
    faces: np.ndarray
    dropped_faces: int
    weight_bones: np.ndarray
    weight_values: np.ndarray
    weight_stats: WeightStats
    textures: List[ImportTexture]

    @property
    def vertex_count(self) -> int:
        return int(self.positions.shape[0])

    @property
    def face_count(self) -> int:
        return int(self.faces.shape[0])

    def texture(self, role: str) -> Optional[ImportTexture]:
        for tex in self.textures:
            if tex.role == role:
                return tex
        return None

    @property
    def colors_are_uniform(self) -> bool:
        return self.vertex_count == 0 or bool(np.all(self.colors == self.colors[0]))


@dataclass
class ImportData:
    source_path: str
    model_name: str
    version: Optional[str]
    bones: List[ImportBone]
    meshes: List[ImportMesh]
    normal_swizzle: str
    has_default_pose: bool
    warnings: List[str] = field(default_factory=list)

    @property
    def vertex_count(self) -> int:
        return sum(m.vertex_count for m in self.meshes)

    @property
    def face_count(self) -> int:
        return sum(m.face_count for m in self.meshes)

    def weight_totals(self) -> WeightStats:
        total = WeightStats()
        for m in self.meshes:
            s = m.weight_stats
            total.vertices += s.vertices
            total.renormalized += s.renormalized
            total.truncated += s.truncated
            total.unweighted += s.unweighted
            total.invalid_refs += s.invalid_refs
            total.max_influences = max(total.max_influences, s.max_influences)
        return total


# ---------------------------------------------------------------------------
# bones

def compute_tails(names: Sequence[str], parents: Sequence[int], heads: np.ndarray,
                  min_length: float = MIN_BONE_LENGTH) -> np.ndarray:
    """Derive a tail for every bone from the hierarchy (XPS stores heads only).

    * one usable child: tail = that child's head;
    * several: a centred bone prefers centred children (spine -> neck rather
      than an arm); a centred bone whose children are all off-centre (pelvis
      -> two thighs) points at their midpoint; otherwise the child with the
      largest subtree wins, ties broken by how far the child reaches along the
      incoming parent->bone direction (hand -> middle finger);
    * no usable child: continue the parent direction for half the parent
      length (clamped to 1-10 cm); roots without children point up 10 cm;
    * children whose head coincides with this head and helper bones (twist,
      adj, unused, ...) are ignored unless nothing else is left.
    """
    n = len(names)
    heads = np.asarray(heads, dtype=np.float64).reshape(n, 3)
    children: List[List[int]] = [[] for _ in range(n)]
    for i, p in enumerate(parents):
        if 0 <= p < n and p != i:
            children[p].append(i)
    subtree = _subtree_sizes(children, parents)
    centre_eps = max(1e-4, 0.01 * _span(heads))
    tails = np.empty_like(heads)
    for i in range(n):
        head = heads[i]
        kids = [c for c in children[i] if np.linalg.norm(heads[c] - head) > min_length]
        usable = [c for c in kids if not _HELPER_RE.search(names[c])] or kids
        tail = None
        if len(usable) == 1:
            tail = heads[usable[0]]
        elif usable:
            pool = usable
            centred_bone = abs(head[0]) < centre_eps
            if centred_bone:
                pool = [c for c in usable if abs(heads[c][0]) < centre_eps]
            if not pool:  # centred bone with only side children: aim between them
                mid = heads[usable].mean(axis=0)
                if np.linalg.norm(mid - head) > min_length:
                    tail = mid
                pool = usable
            if tail is None:
                p = parents[i]
                incoming = head - heads[p] if 0 <= p < n else heads[pool].mean(axis=0) - head
                norm = float(np.linalg.norm(incoming))
                incoming = incoming / norm if norm > 1e-12 else np.zeros(3)
                best = max(pool, key=lambda c: (subtree[c], float(np.dot(heads[c] - head, incoming))))
                tail = heads[best]
        else:
            p = parents[i]
            if 0 <= p < n:
                direction = head - heads[p]
                length = float(np.linalg.norm(direction))
                if length > 1e-9:
                    tail = head + direction / length * min(0.1, max(0.01, 0.5 * length))
            if tail is None:
                tail = head + np.array([0.0, 0.0, 0.1])
        vec = tail - head
        length = float(np.linalg.norm(vec))
        if length < min_length:
            vec = vec / length * min_length if length > 1e-12 else np.array([0.0, 0.0, min_length])
            tail = head + vec
        tails[i] = tail
    return tails


def _span(points: np.ndarray) -> float:
    if points.size == 0:
        return 1.0
    return float(np.max(points.max(axis=0) - points.min(axis=0))) or 1.0


def _subtree_sizes(children: List[List[int]], parents: Sequence[int]) -> List[int]:
    n = len(children)
    sizes = [1] * n
    order: List[int] = []
    roots = [i for i in range(n) if not (0 <= parents[i] < n) or parents[i] == i]
    stack = list(roots)
    seen = set()
    while stack:
        i = stack.pop()
        if i in seen:
            continue
        seen.add(i)
        order.append(i)
        stack.extend(children[i])
    for i in reversed(order):
        for c in children[i]:
            sizes[i] += sizes[c]
    return sizes


def build_bones(model: XpsModel) -> List[ImportBone]:
    if not model.bones:
        return []
    heads = xna_to_blender(np.array([b.position for b in model.bones], dtype=np.float64))
    names = [b.name for b in model.bones]
    parents = [b.parent_index if 0 <= b.parent_index < len(model.bones) else -1 for b in model.bones]
    tails = compute_tails(names, parents, heads)
    return [ImportBone(i, names[i], parents[i], tuple(map(float, heads[i])), tuple(map(float, tails[i])))
            for i in range(len(names))]


# ---------------------------------------------------------------------------
# meshes

def convert_weights(mesh: XpsMesh, bone_count: int) -> Tuple[np.ndarray, np.ndarray, WeightStats]:
    """Clean per-vertex skin weights into ``(N, 4)`` bone-index / weight arrays (``-1`` = empty slot)."""
    n = len(mesh.vertices)
    bones = np.full((n, MAX_INFLUENCES), -1, dtype=np.int32)
    values = np.zeros((n, MAX_INFLUENCES), dtype=np.float32)
    stats = WeightStats(vertices=n)
    for i, vert in enumerate(mesh.vertices):
        acc: Dict[int, float] = {}
        for b, w in zip(vert.bone_indices, vert.bone_weights):
            if not (w > 0.0):
                continue
            if 0 <= b < bone_count:
                acc[b] = acc.get(b, 0.0) + w
            else:
                stats.invalid_refs += 1
        if not acc:
            stats.unweighted += 1
            continue
        if len(acc) > stats.max_influences:
            stats.max_influences = len(acc)
        items = sorted(acc.items(), key=lambda t: (-t[1], t[0]))
        if len(items) > MAX_INFLUENCES:
            stats.truncated += 1
            items = items[:MAX_INFLUENCES]
        total = sum(w for _, w in items)
        if abs(total - 1.0) > 1e-4:
            stats.renormalized += 1
        for k, (b, w) in enumerate(items):
            bones[i, k] = b
            values[i, k] = w / total
    return bones, values, stats


def convert_faces(mesh: XpsMesh) -> Tuple[np.ndarray, int]:
    """Re-wind faces for Blender and drop degenerate / out-of-range triangles."""
    if not mesh.faces:
        return np.zeros((0, 3), dtype=np.int32), 0
    faces = np.asarray(mesh.faces, dtype=np.int64).reshape(-1, 3)
    n = len(mesh.vertices)
    valid = np.all((faces >= 0) & (faces < n), axis=1)
    valid &= (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    kept = faces[valid][:, [0, 2, 1]].astype(np.int32)
    return kept, int((~valid).sum())


def material_key(index: int, base_name: str) -> str:
    """Stable, ASCII-safe key that survives renames (``m03_body``)."""
    slug = re.sub(r"[^0-9A-Za-z]+", "_", base_name).strip("_").lower() or "mesh"
    return f"m{index:02d}_{slug[:40]}"


class TextureResolver:
    """Find texture files next to the model, case-insensitively, also one folder level down."""

    def __init__(self, search_dirs: Iterable[str]):
        self._index: Dict[str, str] = {}
        self._dirs = [d for d in search_dirs if d and os.path.isdir(d)]
        for d in self._dirs:
            self._add_dir(d, depth=1)

    def _add_dir(self, directory: str, depth: int) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda e: e.name.lower())
        except OSError:
            return
        subdirs = []
        for entry in entries:
            if entry.is_file():
                self._index.setdefault(entry.name.lower(), entry.path)
            elif entry.is_dir() and depth > 0:
                subdirs.append(entry.path)
        for sub in subdirs:
            self._add_dir(sub, depth - 1)

    def resolve(self, file: str, raw_path: str = "") -> Optional[str]:
        if raw_path:
            rel = raw_path.replace("\\", "/")
            for d in self._dirs:
                cand = os.path.normpath(os.path.join(d, rel))
                if os.path.isfile(cand):
                    return cand
        return self._index.get(file.lower()) if file else None


def build_mesh(model: XpsModel, index: int, resolver: TextureResolver) -> ImportMesh:
    mesh = model.meshes[index]
    verts = mesh.vertices
    n = len(verts)
    if n:
        positions = xna_to_blender(np.array([v.position for v in verts], dtype=np.float64)).astype(np.float32)
        normals = xna_to_blender(np.array([v.normal for v in verts], dtype=np.float64))
        lengths = np.linalg.norm(normals, axis=1, keepdims=True)
        normals = np.where(lengths > 1e-12, normals / np.maximum(lengths, 1e-12), normals).astype(np.float32)
        colors = (np.array([v.color_rgba for v in verts], dtype=np.float32) / 255.0)
        uvs = []
        for layer in range(mesh.uv_layer_count):
            uv = np.array([v.uvs[layer] if layer < len(v.uvs) else (0.0, 0.0) for v in verts], dtype=np.float32)
            uv[:, 1] = 1.0 - uv[:, 1]
            uvs.append(uv)
    else:
        positions = np.zeros((0, 3), np.float32)
        normals = np.zeros((0, 3), np.float32)
        colors = np.zeros((0, 4), np.float32)
        uvs = [np.zeros((0, 2), np.float32) for _ in range(mesh.uv_layer_count)]
    faces, dropped = convert_faces(mesh)
    wb, wv, stats = convert_weights(mesh, len(model.bones))
    rg = describe_render_group(mesh.render_group)
    textures = []
    for slot, tex in enumerate(mesh.textures):
        role = rg.slot_kind(slot) or "extra"
        textures.append(ImportTexture(slot, role, tex.file, tex.raw_path, tex.uv_layer,
                                      resolver.resolve(tex.file, tex.raw_path)))
    return ImportMesh(
        index=index, raw_name=mesh.name, base_name=mesh.mesh_base_name or mesh.name,
        join_name=mesh.join_name or mesh.name, material_key="", render_group=mesh.render_group, rg_info=rg,
        specular=mesh.specular, bump_repeat1=mesh.bump_repeat1, bump_repeat2=mesh.bump_repeat2,
        optional_visible=mesh.optional_visible, optional_group=mesh.optional_group,
        optional_item=mesh.optional_item, optional_part=mesh.optional_part,
        positions=positions, normals=normals, uvs=uvs, colors=colors, faces=faces, dropped_faces=dropped,
        weight_bones=wb, weight_values=wv, weight_stats=stats, textures=textures)


def _assign_material_keys(meshes: List[ImportMesh]) -> None:
    """Split parts of one logical mesh (``nPart!``) share one material key; others get their own."""
    by_join: Dict[str, str] = {}
    for m in meshes:
        signature = (m.join_name, m.render_group, tuple((t.role, t.file.lower()) for t in m.textures))
        key = by_join.get(repr(signature))
        if key is None:
            key = material_key(m.index, m.base_name)
            by_join[repr(signature)] = key
        m.material_key = key


def build_import_data(model: XpsModel, extra_texture_dirs: Sequence[str] = ()) -> ImportData:
    """Convert a loaded model; never raises for content problems, they end up in ``warnings``."""
    src_dir = os.path.dirname(os.path.abspath(model.source_path)) if model.source_path else ""
    resolver = TextureResolver([src_dir, *extra_texture_dirs])
    bones = build_bones(model)
    meshes = [build_mesh(model, i, resolver) for i in range(len(model.meshes))]
    _assign_material_keys(meshes)
    header = model.header
    swizzle = header.normal_map_swizzle if header is not None else "X+ Y- Z+"
    has_pose = bool(header is not None and header.default_pose)
    return ImportData(
        source_path=model.source_path, model_name=model_display_name(model.source_path or "model.xps"),
        version=model.version, bones=bones, meshes=meshes, normal_swizzle=swizzle,
        has_default_pose=has_pose, warnings=list(model.warnings))


def normal_green_inverted(swizzle: str) -> bool:
    """True when the normal map stores green as Y- (DirectX); Blender wants Y+ (OpenGL)."""
    return "Y-" in swizzle.split()


def has_bump(mesh: ImportMesh) -> bool:
    tex = mesh.texture(BUMP)
    return tex is not None and tex.found
