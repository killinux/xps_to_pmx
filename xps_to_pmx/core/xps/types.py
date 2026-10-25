"""Plain data containers for XPS / XNALara model files.

The classes mirror what the file formats actually store (see
``docs/research_notes/XPS 转 PMX 方案调研/01_xps格式与导入.md``).  Nothing is
converted here: positions and normals stay in the XNA convention (+X right,
+Y up, +Z towards the viewer), UVs keep their original V orientation and faces
keep the winding used by XNALara.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Tuple

Vec2 = Tuple[float, float]
Vec3 = Tuple[float, float, float]
Vec4 = Tuple[float, float, float, float]
RGBA = Tuple[int, int, int, int]

#: First uint32 of a binary file that carries a header (decimal 323232).
MAGIC = 323232
#: Fixed string stored right after the version numbers of the header.
XNA_ARAL = "XNAaraL"

#: Flag ids of the type-2 settings item of the header, keyed by id.
FLAG_NAMES: Dict[int, str] = {
    0: "backFaceCulling",
    1: "alwaysForceCulling",
    2: "modelCastShadows",
    3: "tangentSpaceRed",
    4: "tangentSpaceGreen",
    5: "tangentSpaceBlue",
    6: "gloss",
    7: "hasBoneDirections",
}

#: Values XPS assumes when a flag is absent from the header.  The tangent-space
#: triple ``(0, 1, 0)`` is the default normal-map swizzle ``X+ Y- Z+``.
DEFAULT_FLAGS: Dict[str, Any] = {
    "backFaceCulling": False,
    "alwaysForceCulling": False,
    "modelCastShadows": True,
    "tangentSpaceRed": 0,
    "tangentSpaceGreen": 1,
    "tangentSpaceBlue": 0,
    "gloss": 10,
    "hasBoneDirections": False,
}


class XpsPoseEntry(NamedTuple):
    """One line of a ``.pose`` file: Euler rotation in degrees, translation and scale (XNA axes)."""

    rotation_deg: Vec3
    translation: Vec3
    scale: Vec3


@dataclass(slots=True)
class XpsBone:
    """A bone: only a name, a parent index (-1 for roots) and a head position exist in XPS."""

    name: str
    parent_index: int
    position: Vec3

    @property
    def is_root(self) -> bool:
        return self.parent_index < 0


@dataclass(slots=True)
class XpsTexture:
    """A texture reference of a mesh.

    ``file`` is the file name with any directory part removed (what importers
    use to find the image next to the model); ``raw_path`` is the string as stored.
    """

    file: str
    uv_layer: int
    raw_path: str = ""

    @property
    def extension(self) -> str:
        dot = self.file.rfind(".")
        return self.file[dot:].lower() if dot >= 0 else ""


@dataclass(slots=True)
class XpsVertex:
    """A vertex exactly as stored; ``tangents`` is ``None`` when the layout has no tangents.

    ``bone_indices`` / ``bone_weights`` always have the same length (4 for the
    fixed layout, N for the variable layout of version 3.x, 0 when the model has
    no bones).  Weights are *not* re-normalised and zero-weight slots are kept.
    """

    position: Vec3
    normal: Vec3
    color_rgba: RGBA
    uvs: List[Vec2]
    tangents: Optional[List[Vec4]]
    bone_indices: List[int]
    bone_weights: List[float]


@dataclass(slots=True)
class MeshNameInfo:
    """Result of :func:`xps_to_pmx.core.xps.reader.parse_mesh_name`.

    * ``render_group`` is ``None`` when the first ``_`` token is not a number
      (XPS then renders the mesh as group 5, see :attr:`effective_render_group`).
    * ``base_name`` is the name token(s) without the optional-item prefix.
    * ``optional_visible`` is ``True`` for a ``+`` prefix (optional item shown by
      default), ``False`` for ``-`` (hidden by default), ``None`` otherwise.
    * For optional items, ``optional_group`` is the menu group before ``|``,
      ``optional_item`` the menu entry and ``optional_part`` the ``.`` suffix
      that lets several meshes form one entry (``-glasses.frame``).
    * ``join_name`` is the full name with ``nPart!`` split markers removed;
      meshes sharing a ``join_name`` are parts of one logical mesh and
      ``part_index`` is the number in front of ``nPart!`` (``None`` if absent).
    """

    raw_name: str
    render_group: Optional[int]
    base_name: str
    specular: float
    bump_repeat1: float
    bump_repeat2: float
    extra_params: List[str]
    optional_visible: Optional[bool]
    optional_group: Optional[str]
    optional_item: Optional[str]
    optional_part: Optional[str]
    join_name: str
    part_index: Optional[int]

    @property
    def is_optional(self) -> bool:
        return self.optional_visible is not None

    @property
    def is_split_part(self) -> bool:
        return self.join_name != self.raw_name

    @property
    def effective_render_group(self) -> int:
        return 5 if self.render_group is None else self.render_group


@dataclass(slots=True)
class XpsMesh:
    """A mesh (= one XPS material) with the parsed meaning of its name flattened in."""

    name: str
    uv_layer_count: int
    textures: List[XpsTexture]
    vertices: List[XpsVertex]
    faces: List[Tuple[int, int, int]]
    render_group: Optional[int]
    mesh_base_name: str
    specular: float
    bump_repeat1: float
    bump_repeat2: float
    optional_visible: Optional[bool]
    optional_group: Optional[str]
    optional_item: Optional[str] = None
    optional_part: Optional[str] = None
    extra_params: List[str] = field(default_factory=list)
    join_name: str = ""
    part_index: Optional[int] = None

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def face_count(self) -> int:
        return len(self.faces)

    @property
    def is_optional(self) -> bool:
        return self.optional_visible is not None

    @property
    def effective_render_group(self) -> int:
        return 5 if self.render_group is None else self.render_group


@dataclass(slots=True)
class XpsHeader:
    """Header of a binary ``.xps`` (or headered ``.mesh``) file.

    ``flags`` holds only the flags explicitly present in the settings block,
    keyed by the names of :data:`FLAG_NAMES` (unknown ids become ``flag_<id>``):
    booleans for flags 0/1/2/7, ``value % 2`` for the tangent-space flags 3/4/5
    and the raw number for ``gloss`` (6).  ``flags_raw`` keeps every stored
    ``id -> value`` pair untouched.  Use :meth:`flag` for the effective value
    with XPS defaults applied.  ``settings_raw`` is the complete settings block
    (``settings_len * 4`` bytes); it is only interpreted for versions newer
    than 2.12, like the reference importer does.  ``settings_items`` lists the
    ``(type, count, info)`` triples encountered, in order.
    """

    magic: int
    major: int
    minor: int
    xna_string: str
    settings_len: int
    machine: str
    user: str
    files: str
    settings_raw: bytes
    flags: Dict[str, Any] = field(default_factory=dict)
    flags_raw: Dict[int, int] = field(default_factory=dict)
    default_pose_text: Optional[str] = None
    default_pose: Optional[Dict[str, XpsPoseEntry]] = None
    settings_hash: Optional[int] = None
    settings_item_count: Optional[int] = None
    settings_items: List[Tuple[int, int, int]] = field(default_factory=list)
    settings_parsed: bool = False

    @property
    def version(self) -> str:
        return f"{self.major}.{self.minor}"

    def flag(self, name: str, default: Any = None) -> Any:
        """Return the value of ``name`` as stored, else the XPS default, else ``default``."""
        if name in self.flags:
            return self.flags[name]
        return DEFAULT_FLAGS.get(name, default)

    @property
    def normal_map_swizzle(self) -> str:
        """Normal-map channel orientation implied by the tangent-space flags, e.g. ``X+ Y- Z+``."""
        signs = []
        for axis, key in (("X", "tangentSpaceRed"), ("Y", "tangentSpaceGreen"), ("Z", "tangentSpaceBlue")):
            value = self.flag(key)
            signs.append(axis + ("-" if value == 1 else "+" if value == 0 else "?"))
        return " ".join(signs)


@dataclass(slots=True)
class XpsModel:
    """A whole model file.  ``header`` is ``None`` for headerless ``.mesh`` and for text files.

    ``complete`` is ``False`` when the reader stopped early on corrupt or
    truncated data (non-strict mode); ``warnings`` then explains where.
    """

    header: Optional[XpsHeader]
    bones: List[XpsBone]
    meshes: List[XpsMesh]
    source_path: str
    is_ascii: bool
    warnings: List[str] = field(default_factory=list)
    #: Bytes (binary) or non-blank lines (text) left after the last mesh.
    trailing_bytes: int = 0
    #: Vertex layout actually used while reading.
    has_tangents: bool = False
    has_variable_weights: bool = False
    complete: bool = True
    declared_mesh_count: Optional[int] = None
    non_utf8_strings: int = 0

    @property
    def has_header(self) -> bool:
        return self.header is not None

    @property
    def version(self) -> Optional[str]:
        return self.header.version if self.header is not None else None

    @property
    def vertex_count(self) -> int:
        return sum(len(m.vertices) for m in self.meshes)

    @property
    def face_count(self) -> int:
        return sum(len(m.faces) for m in self.meshes)

    @property
    def root_bones(self) -> List[XpsBone]:
        return [b for b in self.bones if b.parent_index < 0]

    def iter_vertices(self) -> Iterator[XpsVertex]:
        for mesh in self.meshes:
            yield from mesh.vertices

    def bounding_box(self, include_optional_hidden: bool = True) -> Optional[Tuple[Vec3, Vec3]]:
        """Axis-aligned bounding box of all vertices in XNA coordinates, or ``None`` without vertices.

        With ``include_optional_hidden=False`` meshes whose name starts with
        ``-`` (optional items hidden by default) are ignored.  Non-finite
        coordinates never win a comparison and are therefore ignored.
        """
        min_x = min_y = min_z = float("inf")
        max_x = max_y = max_z = float("-inf")
        for mesh in self.meshes:
            if not include_optional_hidden and mesh.optional_visible is False:
                continue
            for v in mesh.vertices:
                x, y, z = v.position
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y
                if z < min_z:
                    min_z = z
                if z > max_z:
                    max_z = z
        if min_x > max_x:
            return None
        return (min_x, min_y, min_z), (max_x, max_y, max_z)

    def bone_index(self, name: str) -> Optional[int]:
        """Index of the first bone called ``name`` (case-insensitive), or ``None``."""
        wanted = name.lower()
        for i, bone in enumerate(self.bones):
            if bone.name.lower() == wanted:
                return i
        return None
