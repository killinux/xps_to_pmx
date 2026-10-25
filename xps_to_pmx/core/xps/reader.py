"""Pure-Python reader for XPS / XNALara models and poses (no Blender dependency).

Supported inputs
----------------
* binary ``.xps`` / ``.mesh`` with a header (first uint32 == 323232),
* binary ``.mesh`` without a header,
* text ``.mesh.ascii`` / ``.ascii``,
* text ``.pose`` (the same text is embedded in the header as the default pose).

The byte layout follows section 1 of
``docs/research_notes/XPS 转 PMX 方案调研/01_xps格式与导入.md``:

* little-endian numbers; strings are .NET ``BinaryWriter`` strings (7-bit
  variable-length byte count, then UTF-8 bytes, decoded as ``utf-8-sig``);
* header: magic, uint16 major, uint16 minor, ``"XNAaraL"``, uint32 settings
  length in 4-byte words, machine, user, files, then the settings block;
* **tangents**: present when there is no header, or when the header version
  is ``major <= 2 and minor <= 12``; one float4 tangent follows *each* UV pair;
* **variable weights**: when the header version has ``major >= 3`` every
  vertex stores a uint16 count, N int16 bone indices and N float weights;
  otherwise exactly 4 indices + 4 weights (no weights at all without bones);
* bones: name, int16 parent (-1 = root), float3 head position;
* meshes: name, uint32 UV layer count, textures (name + uint32 UV layer),
  vertices (float3 position, float3 normal, uint8 RGBA, UVs [+ tangents],
  weights), uint32 triangle count and uint32 x3 indices.

Coordinates are returned untouched (XNA: +X right, +Y up, +Z towards the
viewer).  The reader is tolerant: unknown trailing data, odd settings blocks
and undecodable strings produce entries in ``XpsModel.warnings`` (also logged)
instead of exceptions; in non-strict mode a truncated mesh table yields the
meshes read so far with ``XpsModel.complete = False``.
"""
from __future__ import annotations

import logging
import math
import os
import re
import struct
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .types import (
    FLAG_NAMES,
    MAGIC,
    XNA_ARAL,
    MeshNameInfo,
    XpsBone,
    XpsHeader,
    XpsMesh,
    XpsModel,
    XpsPoseEntry,
    XpsTexture,
    XpsVertex,
)

__all__ = [
    "XpsFormatError",
    "has_tangent_layout",
    "has_variable_weight_layout",
    "load_pose",
    "load_xps",
    "parse_mesh_name",
    "parse_pose_text",
    "parse_xps_ascii",
    "parse_xps_bytes",
    "parse_xps_data",
    "validate_model",
]

log = logging.getLogger(__name__)

PathLike = Union[str, "os.PathLike[str]"]

_U16 = struct.Struct("<H")
_U32 = struct.Struct("<I")
_BONE_TAIL = struct.Struct("<h3f")  # parent index + head position
_SETTINGS_ITEM = struct.Struct("<3I")  # type, count, info
_FLAG_PAIR = struct.Struct("<2I")  # flag id, value

#: Sanity limits; exceeding one means the layout guess is wrong or the data corrupt.
MAX_UV_LAYERS = 32
MAX_TEXTURES = 512
MAX_WEIGHTS_PER_VERTEX = 1024

#: Smallest possible byte sizes, used to reject absurd counts before allocating.
_MIN_BONE_BYTES = 1 + 2 + 12
_MIN_MESH_BYTES = 1 + 4 + 4 + 4 + 4


class XpsFormatError(ValueError):
    """The data does not follow the XPS layout (or is truncated)."""


# --------------------------------------------------------------------------- layout rules


def has_tangent_layout(header: Optional[XpsHeader]) -> bool:
    """Whether vertices carry one float4 tangent per UV layer (no header, or version <= 2.12)."""
    if header is None:
        return True
    return header.major <= 2 and header.minor <= 12


def has_variable_weight_layout(header: Optional[XpsHeader]) -> bool:
    """Whether vertices store a weight count followed by N indices and N weights (version >= 3)."""
    return header is not None and header.major >= 3


# --------------------------------------------------------------------------- binary helpers


class _Cursor:
    """Read position over an immutable bytes buffer with bounds checking."""

    __slots__ = ("data", "pos", "end", "non_utf8")

    def __init__(self, data: bytes, pos: int = 0) -> None:
        self.data = data
        self.pos = pos
        self.end = len(data)
        self.non_utf8 = 0

    @property
    def remaining(self) -> int:
        return self.end - self.pos

    def need(self, size: int, what: str) -> None:
        if size < 0 or self.pos + size > self.end:
            raise XpsFormatError(
                f"unexpected end of data while reading {what} at offset {self.pos} "
                f"(need {size} bytes, {self.end - self.pos} left)")

    def u16(self, what: str) -> int:
        self.need(2, what)
        value = _U16.unpack_from(self.data, self.pos)[0]
        self.pos += 2
        return value

    def u32(self, what: str) -> int:
        self.need(4, what)
        value = _U32.unpack_from(self.data, self.pos)[0]
        self.pos += 4
        return value

    def string(self, what: str) -> str:
        """Read a .NET ``BinaryWriter`` string: 7-bit encoded byte length, then the bytes.

        For lengths below 16384 this is exactly the importer rule
        ``length = b1 % 128 + b2 * 128``; longer strings continue the 7-bit chain.
        """
        data = self.data
        length = 0
        shift = 0
        while True:
            self.need(1, what + " length")
            byte = data[self.pos]
            self.pos += 1
            length |= (byte & 0x7F) << shift
            if byte < 0x80:
                break
            shift += 7
            if shift > 28:
                raise XpsFormatError(f"invalid length prefix for {what} at offset {self.pos}")
        self.need(length, what)
        raw = data[self.pos:self.pos + length]
        self.pos += length
        return self.decode(raw)

    def decode(self, raw: bytes) -> str:
        try:
            return raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            self.non_utf8 += 1
            return raw.decode("latin-1")


_LINE_BREAK = re.compile(r"\r+\n?|\n")


def _split_lines(text: str) -> List[str]:
    """Split on LF, CRLF, CR CR LF and lone CR only.

    ``str.splitlines`` is avoided on purpose: it also breaks on U+0085 and
    other separators that latin-1 decoded names may contain, and it turns a
    doubled CR CR LF into an extra blank line that would desync the format.
    """
    return _LINE_BREAK.split(text)


def _round_up4(value: int) -> int:
    return (value + 3) // 4 * 4


def _basename(path: str) -> str:
    """File name part of a Windows or POSIX path (texture names are often stored with directories)."""
    return re.split(r"[\\/]", path)[-1]


def _flag_value(flag_id: int, value: int):
    if flag_id in (0, 1, 2, 7):
        return bool(value)
    if flag_id in (3, 4, 5):
        return value % 2
    # 6 = gloss and unknown ids keep the stored number (the reference importer
    # coerces gloss to bool, which loses the value).
    return value


# --------------------------------------------------------------------------- header


def _read_header(cur: _Cursor, warnings: List[str]) -> XpsHeader:
    magic = cur.u32("magic number")
    major = cur.u16("major version")
    minor = cur.u16("minor version")
    xna_string = cur.string("XNAaraL marker")
    settings_len = cur.u32("settings length")
    machine = cur.string("machine name")
    user = cur.string("user name")
    files = cur.string("files string")
    size = settings_len * 4
    cur.need(size, "settings block")
    raw = cur.data[cur.pos:cur.pos + size]
    cur.pos += size
    header = XpsHeader(magic=magic, major=major, minor=minor, xna_string=xna_string,
                       settings_len=settings_len, machine=machine, user=user, files=files,
                       settings_raw=raw)
    if xna_string != XNA_ARAL:
        warnings.append(f"header marker is {xna_string!r}, expected {XNA_ARAL!r}")
    if not has_tangent_layout(header):
        # Versions <= 2.12 store an uninterpreted block; newer ones use typed items.
        _parse_settings(header, warnings)
    return header


def _parse_settings(header: XpsHeader, warnings: List[str]) -> None:
    """Interpret the typed settings items (type 0 = padding, 1 = default pose, 2 = flags).

    The block length from the header is authoritative: whatever the items say,
    reading of bones always resumes at the end of the block.
    """
    raw = header.settings_raw
    cur = _Cursor(raw)
    try:
        header.settings_hash = cur.u32("settings hash")
        item_count = cur.u32("settings item count")
        header.settings_item_count = item_count
        for index in range(item_count):
            if cur.remaining < _SETTINGS_ITEM.size:
                warnings.append(f"settings block ends after {index} of {item_count} items")
                break
            opt_type, opt_count, opt_info = _SETTINGS_ITEM.unpack_from(raw, cur.pos)
            cur.pos += _SETTINGS_ITEM.size
            header.settings_items.append((opt_type, opt_count, opt_info))
            if opt_type == 0:
                # Unused words (XPS pads the block this way).
                cur.need(opt_count * 4, "settings padding item")
                cur.pos += opt_count * 4
            elif opt_type == 1:
                # Default pose: count = unpadded byte length, info = number of bone lines.
                cur.need(opt_count, "default pose text")
                text_bytes = raw[cur.pos:cur.pos + opt_count]
                cur.pos = min(cur.end, cur.pos + _round_up4(opt_count))
                if opt_count:
                    text = cur.decode(text_bytes)
                    header.default_pose_text = text
                    header.default_pose = parse_pose_text(text)
                    lines = sum(1 for line in _split_lines(text) if line.strip())
                    if lines != opt_info:
                        warnings.append(
                            f"default pose declares {opt_info} bone lines but contains {lines}")
            elif opt_type == 2:
                # Flags: count pairs of (flag id, value).
                cur.need(opt_count * _FLAG_PAIR.size, "settings flags")
                for _ in range(opt_count):
                    flag_id, value = _FLAG_PAIR.unpack_from(raw, cur.pos)
                    cur.pos += _FLAG_PAIR.size
                    header.flags_raw[flag_id] = value
                    header.flags[FLAG_NAMES.get(flag_id, f"flag_{flag_id}")] = _flag_value(flag_id, value)
            else:
                # Unknown item: the reference importer treats the rest of the block as padding.
                break
        header.settings_parsed = True
    except XpsFormatError as err:
        warnings.append(f"settings block only partially understood: {err}")
    if cur.non_utf8:
        warnings.append("default pose text is not valid UTF-8 (decoded as latin-1)")


# --------------------------------------------------------------------------- bones and meshes


def _read_bones(cur: _Cursor) -> List[XpsBone]:
    count = cur.u32("bone count")
    if count * _MIN_BONE_BYTES > cur.remaining:
        raise XpsFormatError(f"implausible bone count {count} at offset {cur.pos - 4}")
    bones: List[XpsBone] = []
    data = cur.data
    for index in range(count):
        name = cur.string(f"name of bone {index}")
        cur.need(_BONE_TAIL.size, f"bone {index}")
        parent, x, y, z = _BONE_TAIL.unpack_from(data, cur.pos)
        cur.pos += _BONE_TAIL.size
        bones.append(XpsBone(name, parent, (x, y, z)))
    return bones


def _read_vertices_binary(cur: _Cursor, count: int, uv_count: int, has_tangents: bool,
                          has_bones: bool, variable_weights: bool) -> List[XpsVertex]:
    vertices: List[XpsVertex] = []
    if count == 0:
        return vertices
    uv_step = 6 if has_tangents else 2
    head_fmt = "3f3f4B" + ("2f4f" if has_tangents else "2f") * uv_count
    uv_slices = tuple(slice(10 + k * uv_step, 12 + k * uv_step) for k in range(uv_count))
    tan_slices = tuple(slice(12 + k * uv_step, 16 + k * uv_step) for k in range(uv_count))
    w0 = 10 + uv_count * uv_step  # index of the first value after the UV block
    make = XpsVertex
    append = vertices.append
    data = cur.data

    if has_bones and variable_weights:
        head = struct.Struct("<" + head_fmt + "H")  # the weight count closes the fixed part
        hsize = head.size
        if count * hsize > cur.remaining:
            raise XpsFormatError(
                f"{count} vertices need at least {count * hsize} bytes, only {cur.remaining} left")
        weight_structs: Dict[int, struct.Struct] = {}
        pos = cur.pos
        end = cur.end
        for vi in range(count):
            if pos + hsize > end:
                raise XpsFormatError(f"unexpected end of data in vertex {vi} at offset {pos}")
            r = head.unpack_from(data, pos)
            pos += hsize
            n = r[w0]
            if n > MAX_WEIGHTS_PER_VERTEX:
                raise XpsFormatError(f"vertex {vi}: implausible weight count {n} at offset {pos - 2}")
            ws = weight_structs.get(n)
            if ws is None:
                ws = weight_structs[n] = struct.Struct(f"<{n}h{n}f")
            if pos + ws.size > end:
                raise XpsFormatError(f"unexpected end of data in weights of vertex {vi}")
            w = ws.unpack_from(data, pos)
            pos += ws.size
            append(make(r[0:3], r[3:6], r[6:10], [r[s] for s in uv_slices],
                        [r[s] for s in tan_slices] if has_tangents else None,
                        list(w[:n]), list(w[n:])))
        cur.pos = pos
        return vertices

    rec = struct.Struct("<" + head_fmt + ("4h4f" if has_bones else ""))
    total = rec.size * count
    if total > cur.remaining:
        raise XpsFormatError(
            f"{count} vertices of {rec.size} bytes need {total} bytes, only {cur.remaining} left")
    view = memoryview(data)[cur.pos:cur.pos + total]
    try:
        if has_bones:
            i1, i2 = w0 + 4, w0 + 8
            if has_tangents:
                for r in rec.iter_unpack(view):
                    append(make(r[0:3], r[3:6], r[6:10], [r[s] for s in uv_slices],
                                [r[s] for s in tan_slices], list(r[w0:i1]), list(r[i1:i2])))
            elif uv_count == 1:
                for r in rec.iter_unpack(view):
                    append(make(r[0:3], r[3:6], r[6:10], [r[10:12]], None,
                                list(r[12:16]), list(r[16:20])))
            else:
                for r in rec.iter_unpack(view):
                    append(make(r[0:3], r[3:6], r[6:10], [r[s] for s in uv_slices], None,
                                list(r[w0:i1]), list(r[i1:i2])))
        else:
            for r in rec.iter_unpack(view):
                append(make(r[0:3], r[3:6], r[6:10], [r[s] for s in uv_slices],
                            [r[s] for s in tan_slices] if has_tangents else None, [], []))
    finally:
        view.release()
    cur.pos += total
    return vertices


def _read_faces_binary(cur: _Cursor, count: int) -> List[Tuple[int, int, int]]:
    size = 12 * count
    cur.need(size, f"{count} triangles")
    if count == 0:
        return []
    flat = struct.unpack_from(f"<{3 * count}I", cur.data, cur.pos)
    cur.pos += size
    it = iter(flat)
    return list(zip(it, it, it))


def _read_mesh_binary(cur: _Cursor, index: int, has_bones: bool, has_tangents: bool,
                      variable_weights: bool) -> XpsMesh:
    name = cur.string(f"name of mesh {index}")
    uv_count = cur.u32("UV layer count")
    if uv_count > MAX_UV_LAYERS:
        raise XpsFormatError(f"implausible UV layer count {uv_count} (mesh {name!r})")
    tex_count = cur.u32("texture count")
    if tex_count > MAX_TEXTURES:
        raise XpsFormatError(f"implausible texture count {tex_count} (mesh {name!r})")
    textures = []
    for t in range(tex_count):
        path = cur.string(f"texture {t} file name")
        uv_layer = cur.u32(f"texture {t} UV layer")
        textures.append(XpsTexture(_basename(path), uv_layer, path))
    vertex_count = cur.u32("vertex count")
    vertices = _read_vertices_binary(cur, vertex_count, uv_count, has_tangents, has_bones,
                                     variable_weights)
    face_count = cur.u32("triangle count")
    faces = _read_faces_binary(cur, face_count)
    return _build_mesh(name or "unnamed", uv_count, textures, vertices, faces)


def _read_meshes_binary(cur: _Cursor, has_bones: bool, has_tangents: bool, variable_weights: bool
                        ) -> Tuple[List[XpsMesh], int, Optional[XpsFormatError]]:
    """Read the mesh table; on a failure inside a mesh return what was read plus the error."""
    declared = cur.u32("mesh count")
    if declared * _MIN_MESH_BYTES > cur.remaining:
        raise XpsFormatError(f"implausible mesh count {declared} at offset {cur.pos - 4}")
    meshes: List[XpsMesh] = []
    for index in range(declared):
        start = cur.pos
        try:
            meshes.append(_read_mesh_binary(cur, index, has_bones, has_tangents, variable_weights))
        except XpsFormatError as err:
            return meshes, declared, XpsFormatError(f"mesh {index} (offset {start}): {err}")
    return meshes, declared, None


def _layout_label(layout: Tuple[bool, bool]) -> str:
    return (f"tangents={'yes' if layout[0] else 'no'}, "
            f"weights={'variable' if layout[1] else 'fixed 4'}")


def parse_xps_bytes(data: bytes, source_path: str = "", strict: bool = False) -> XpsModel:
    """Parse a binary ``.xps`` / ``.mesh`` buffer (with or without header)."""
    data = bytes(data)
    warnings: List[str] = []
    cur = _Cursor(data)
    header: Optional[XpsHeader] = None
    if len(data) >= 4 and _U32.unpack_from(data, 0)[0] == MAGIC:
        header = _read_header(cur, warnings)
    bones = _read_bones(cur)
    has_bones = bool(bones)
    mesh_start = cur.pos

    primary = (has_tangent_layout(header), has_variable_weight_layout(header))
    candidates = [primary] + [alt for alt in ((False, False), (True, False), (False, True), (True, True))
                              if alt != primary]
    chosen = None
    primary_result = None
    for layout in candidates:
        cur.pos = mesh_start
        try:
            meshes, declared, error = _read_meshes_binary(cur, has_bones, *layout)
        except XpsFormatError as err:
            meshes, declared, error = [], None, err
        if layout == primary:
            primary_result = (meshes, declared, error, cur.pos)
            if error is None:
                chosen = (layout, meshes, declared, cur.pos)
                break
        elif error is None and cur.pos == len(data):
            # An alternative layout is only trusted if it consumes the file exactly.
            chosen = (layout, meshes, declared, cur.pos)
            warnings.append(
                f"vertex layout implied by {'version ' + header.version if header else 'missing header'} "
                f"({_layout_label(primary)}) failed: {primary_result[2]}; parsed with {_layout_label(layout)}")
            break

    complete = True
    if chosen is None:
        meshes, declared, error, end_pos = primary_result
        if strict:
            raise error
        complete = False
        warnings.append(f"model is truncated or corrupt, kept {len(meshes)} of "
                        f"{declared if declared is not None else '?'} meshes: {error}")
        layout = primary
        trailing = 0
    else:
        layout, meshes, declared, end_pos = chosen
        trailing = len(data) - end_pos
        if trailing:
            zeros = data.count(0, end_pos) == trailing
            warnings.append(f"{trailing} {'zero' if zeros else 'unknown'} bytes after the last mesh "
                            f"(offset {end_pos}) were ignored")
    if cur.non_utf8:
        warnings.append(f"{cur.non_utf8} strings were not valid UTF-8 and were decoded as latin-1")

    model = XpsModel(header=header, bones=bones, meshes=meshes, source_path=source_path,
                     is_ascii=False, warnings=warnings, trailing_bytes=trailing,
                     has_tangents=layout[0], has_variable_weights=layout[1], complete=complete,
                     declared_mesh_count=declared, non_utf8_strings=cur.non_utf8)
    _log_warnings(model)
    return model


# --------------------------------------------------------------------------- text (.mesh.ascii)


def _to_int(token: str, what: str, line_no: int) -> int:
    try:
        return int(token)
    except ValueError:
        pass
    try:
        value = float(token)
    except ValueError:
        value = math.nan
    if math.isfinite(value) and value.is_integer():
        return int(value)
    raise XpsFormatError(f"line {line_no}: expected an integer for {what}, got {token!r}")


_ODD_FLOAT = re.compile(r"^[+-]?\d*\.?\d*#(IND|QNAN|SNAN|NAN|INF)", re.IGNORECASE)


def _to_float(token: str, what: str, line_no: int) -> float:
    try:
        return float(token)
    except ValueError:
        pass
    match = _ODD_FLOAT.match(token)  # MSVC style "-1.#IND00" / "1.#INF00"
    if match:
        return math.inf if match.group(1).upper() == "INF" else math.nan
    raise XpsFormatError(f"line {line_no}: expected a number for {what}, got {token!r}")


class _TextCursor:
    """Line-oriented reader: numeric fields skip blank lines and ``#`` comments."""

    __slots__ = ("lines", "i", "n")

    def __init__(self, lines: List[str]) -> None:
        self.lines = lines
        self.i = 0
        self.n = len(lines)

    def tokens(self, what: str) -> List[str]:
        lines = self.lines
        i = self.i
        n = self.n
        while i < n:
            line = lines[i]
            i += 1
            if "#" in line:
                line = line[:line.index("#")]
            parts = line.split()
            if parts:
                self.i = i
                return parts
        self.i = i
        raise XpsFormatError(f"unexpected end of text while reading {what}")

    def string(self, what: str) -> str:
        if self.i >= self.n:
            raise XpsFormatError(f"unexpected end of text while reading {what}")
        line = self.lines[self.i]
        self.i += 1
        if "#" in line:
            line = line[:line.index("#")]
        return line.strip()

    def int(self, what: str) -> int:
        return _to_int(self.tokens(what)[0], what, self.i)

    def floats(self, count: int, what: str) -> tuple:
        parts = self.tokens(what)
        if len(parts) < count:
            raise XpsFormatError(f"line {self.i}: {what} needs {count} values, got {len(parts)}")
        try:
            return tuple(map(float, parts[:count]))
        except ValueError:
            return tuple(_to_float(p, what, self.i) for p in parts[:count])

    def int_list(self, what: str) -> List[int]:
        parts = self.tokens(what)
        try:
            return list(map(int, parts))
        except ValueError:
            return [_to_int(p, what, self.i) for p in parts]

    def float_list(self, what: str) -> List[float]:
        parts = self.tokens(what)
        try:
            return list(map(float, parts))
        except ValueError:
            return [_to_float(p, what, self.i) for p in parts]

    def remaining_nonblank(self) -> int:
        count = 0
        for line in self.lines[self.i:]:
            if line.split("#", 1)[0].strip():
                count += 1
        return count


def _read_mesh_ascii(rd: _TextCursor, index: int, has_bones: bool) -> Tuple[XpsMesh, int]:
    name = rd.string(f"name of mesh {index}")
    uv_count = rd.int("UV layer count")
    if not 0 <= uv_count <= MAX_UV_LAYERS:
        raise XpsFormatError(f"line {rd.i}: implausible UV layer count {uv_count} (mesh {name!r})")
    tex_count = rd.int("texture count")
    if not 0 <= tex_count <= MAX_TEXTURES:
        raise XpsFormatError(f"line {rd.i}: implausible texture count {tex_count} (mesh {name!r})")
    textures = []
    for t in range(tex_count):
        path = rd.string(f"texture {t} file name")
        uv_layer = rd.int(f"texture {t} UV layer")
        textures.append(XpsTexture(_basename(path), uv_layer, path))
    vertex_count = rd.int("vertex count")
    lines_per_vertex = 3 + uv_count + (2 if has_bones else 0)
    if vertex_count < 0 or vertex_count * lines_per_vertex > rd.n - rd.i:
        raise XpsFormatError(f"line {rd.i}: implausible vertex count {vertex_count} (mesh {name!r})")
    vertices: List[XpsVertex] = []
    append = vertices.append
    max_weights = 0
    for _ in range(vertex_count):
        position = rd.floats(3, "vertex position")
        normal = rd.floats(3, "vertex normal")
        color_values = rd.int_list("vertex colour")
        if len(color_values) < 4:
            color_values += [0] * (4 - len(color_values))
        uvs = [rd.floats(2, "UV") for _ in range(uv_count)]
        if has_bones:
            indices = rd.int_list("bone indices")
            weights = rd.float_list("bone weights")
            stored = max(len(indices), len(weights))
            if stored > max_weights:
                max_weights = stored
            width = max(stored, 4)  # pad like the binary fixed layout
            if len(indices) < width:
                indices += [0] * (width - len(indices))
            if len(weights) < width:
                weights += [0.0] * (width - len(weights))
        else:
            indices = []
            weights = []
        append(XpsVertex(position, normal, tuple(color_values[:4]), uvs, None, indices, weights))
    face_count = rd.int("triangle count")
    if face_count < 0 or face_count > rd.n - rd.i:
        raise XpsFormatError(f"line {rd.i}: implausible triangle count {face_count} (mesh {name!r})")
    faces = []
    for _ in range(face_count):
        parts = rd.tokens("triangle")
        if len(parts) < 3:
            raise XpsFormatError(f"line {rd.i}: triangle needs 3 indices, got {len(parts)}")
        try:
            faces.append((int(parts[0]), int(parts[1]), int(parts[2])))
        except ValueError:
            faces.append(tuple(_to_int(p, "triangle index", rd.i) for p in parts[:3]))
    return _build_mesh(name or "unnamed", uv_count, textures, vertices, faces), max_weights


def parse_xps_ascii(text: str, source_path: str = "", strict: bool = False) -> XpsModel:
    """Parse the text format (``.mesh.ascii``).  Text files never have a header or tangents."""
    warnings: List[str] = []
    rd = _TextCursor(_split_lines(text))
    bone_count = rd.int("bone count")
    if bone_count < 0 or bone_count * 3 > rd.n:
        raise XpsFormatError(f"implausible bone count {bone_count}")
    bones: List[XpsBone] = []
    for index in range(bone_count):
        name = rd.string(f"name of bone {index}")
        parent = rd.int(f"parent of bone {index}")
        bones.append(XpsBone(name, parent, rd.floats(3, f"position of bone {index}")))

    meshes: List[XpsMesh] = []
    declared: Optional[int] = None
    error: Optional[XpsFormatError] = None
    max_weights = 0
    try:
        declared = rd.int("mesh count")
        if declared < 0:
            raise XpsFormatError(f"negative mesh count {declared}")
        for index in range(declared):
            try:
                mesh, mesh_max = _read_mesh_ascii(rd, index, bool(bones))
            except XpsFormatError as err:
                error = XpsFormatError(f"mesh {index}: {err}")
                break
            meshes.append(mesh)
            max_weights = max(max_weights, mesh_max)
    except XpsFormatError as err:
        error = err

    complete = error is None
    trailing = 0
    if error is not None:
        if strict:
            raise error
        warnings.append(f"model is truncated or corrupt, kept {len(meshes)} of "
                        f"{declared if declared is not None else '?'} meshes: {error}")
    else:
        trailing = rd.remaining_nonblank()
        if trailing:
            warnings.append(f"{trailing} non-blank lines after the last mesh were ignored")

    model = XpsModel(header=None, bones=bones, meshes=meshes, source_path=source_path,
                     is_ascii=True, warnings=warnings, trailing_bytes=trailing,
                     has_tangents=False, has_variable_weights=max_weights > 4,
                     complete=complete, declared_mesh_count=declared)
    _log_warnings(model)
    return model


# --------------------------------------------------------------------------- dispatch


_TEXT_FIRST_LINE = re.compile(rb"^[ \t]*\d+[ \t]*(?:#[^\r\n]*)?\r*\n")  # tolerates "\r\r\n"


def _looks_like_text(data: bytes) -> bool:
    head = data[:512]
    if head.startswith(b"\xef\xbb\xbf"):
        head = head[3:]
    return bool(_TEXT_FIRST_LINE.match(head))


def _decode_text(data: bytes, warnings: List[str]) -> str:
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        warnings.append("text is not valid UTF-8; decoded as latin-1")
        return data.decode("latin-1")


def parse_xps_data(data: bytes, source_path: str = "", strict: bool = False) -> XpsModel:
    """Parse model bytes, choosing binary or text by content (magic number / first line) and extension."""
    data = bytes(data)
    lower = source_path.lower()
    notes: List[str] = []
    if len(data) >= 4 and _U32.unpack_from(data, 0)[0] == MAGIC:
        if lower.endswith(".ascii"):
            notes.append("file has a text extension but binary XPS content")
        model = parse_xps_bytes(data, source_path, strict)
    elif _looks_like_text(data):
        if lower.endswith((".xps", ".mesh")):
            notes.append("file has a binary extension but text content")
        text = _decode_text(data, notes)
        model = parse_xps_ascii(text, source_path, strict)
    else:
        if lower.endswith(".ascii"):
            notes.append("file has a text extension but binary content")
        model = parse_xps_bytes(data, source_path, strict)
    if notes:
        model.warnings[:0] = notes
        for note in notes:
            log.warning("%s: %s", source_path or "<data>", note)
    return model


def load_xps(path: PathLike, strict: bool = False) -> XpsModel:
    """Load ``.xps`` / ``.mesh`` / ``.mesh.ascii`` / ``.ascii`` from disk.

    With ``strict=False`` (default) a truncated mesh table yields a partial
    model (``complete=False``) instead of an exception; structural errors
    before the mesh table (header, bones) always raise :class:`XpsFormatError`.
    """
    file_path = Path(path)
    return parse_xps_data(file_path.read_bytes(), str(file_path), strict=strict)


# --------------------------------------------------------------------------- poses


def _pad3(values: Sequence[float], fill: float) -> Tuple[float, float, float]:
    padded = list(values[:3]) + [fill] * (3 - len(values[:3]))
    return padded[0], padded[1], padded[2]


def parse_pose_text(text: str) -> Dict[str, XpsPoseEntry]:
    """Parse ``.pose`` text: one ``bone name: rx ry rz tx ty tz sx sy sz`` line per bone.

    Rotations are Euler angles in degrees on the model (XNA) axes.  The bone
    name is everything before the *last* colon.  Missing values default to
    0 for rotation/translation and 1 for scale (the reference importer pads
    every missing value with 1, which only matters for malformed lines).
    """
    pose: Dict[str, XpsPoseEntry] = {}
    for line in _split_lines(text):
        line = line.strip()
        if not line:
            continue
        name, sep, values_text = line.rpartition(":")
        if not sep:
            continue
        values = []
        for token in values_text.split():
            try:
                values.append(float(token))
            except ValueError:
                values.append(math.nan)
        pose[name.strip()] = XpsPoseEntry(_pad3(values[0:3], 0.0), _pad3(values[3:6], 0.0),
                                          _pad3(values[6:9], 1.0))
    return pose


def load_pose(path: PathLike) -> Dict[str, XpsPoseEntry]:
    """Load a ``.pose`` file: ``{bone_name: (rotation_deg_xyz, translation_xyz, scale_xyz)}``."""
    data = Path(path).read_bytes()
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = data.decode("latin-1")
    return parse_pose_text(text)


# --------------------------------------------------------------------------- mesh names


_RG_TOKEN = re.compile(r"^\s*([+-]?)(\d+)(?:\.0*)?\s*$")
_NUMBER = re.compile(r"^\s*[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\s*$")
# Split-part markers as removed by the reference importer before joining parts:
# "<digits>nPart!" and anything enclosed in "!...!" (e.g. "body1nPart!!wrong!").
_NPART_MARKERS = re.compile(r"(?:!.*)*(?:\d+nPart)*!")
_NPART_INDEX = re.compile(r"(\d+)nPart!")


def _param(params: Sequence[str], index: int, default: float) -> float:
    if index < len(params):
        token = params[index].strip()
        if token and _NUMBER.match(token):
            return float(token)
    return default


def parse_mesh_name(name: str) -> MeshNameInfo:
    """Decode the conventions packed into an XPS mesh name.

    ``RG_Name_Spec_Bump1Repeat_Bump2Repeat[_extra...]``:

    * a numeric first token is the render group; otherwise the render group is
      ``None`` (rendered as 5) and the parameters shift left by one;
    * missing or non-numeric parameters keep the defaults specular = 1,
      bump repeats = 0;
    * if the name part itself contains ``_`` (a non-numeric token where a
      parameter is expected) everything up to the last non-numeric token is
      the name;
    * optional items: ``+`` (shown by default) / ``-`` (hidden) prefix on the
      name part (``40_+hat_0.5_0_0``; a sign in front of the render group,
      ``+40_hat``, is accepted too), ``|`` separates the menu group from the
      entry (``-FAU|neutral``) and a ``.`` suffix joins several meshes into
      one entry (``-glasses.frame``);
    * ``nPart!`` split markers are removed first (``24_body1nPart!_0_16_16``
      is part 1 of ``24_body_0_16_16``).
    """
    join_name = _NPART_MARKERS.sub("", name)
    part_match = _NPART_INDEX.search(name)
    part_index = int(part_match.group(1)) if part_match else None

    tokens = join_name.split("_")
    render_group: Optional[int] = None
    sign = ""
    rg_match = _RG_TOKEN.match(tokens[0])
    if rg_match:
        sign = rg_match.group(1)
        render_group = int(rg_match.group(2))
        rest = tokens[1:] or [""]
    else:
        rest = tokens

    if all(not t.strip() or _NUMBER.match(t) for t in rest[1:4]):
        base, params, extra = rest[0], rest[1:4], rest[4:]
    else:
        last_text = max(i for i, t in enumerate(rest) if t.strip() and not _NUMBER.match(t))
        base = "_".join(rest[:last_text + 1])
        params = rest[last_text + 1:last_text + 4]
        extra = rest[last_text + 4:]

    visible: Optional[bool] = None
    if sign:
        visible = sign == "+"
    base = base.strip()
    if base[:1] in ("+", "-"):
        visible = base[0] == "+"
        base = base[1:].strip()

    group = item = part = None
    if visible is not None:
        if len(base) >= 2 and base[0] == base[-1] == '"':
            base = base[1:-1].strip()  # forum examples quote the name: + "FAU|happy"
        entry = base
        if "|" in entry:
            group, _, entry = entry.partition("|")
        item, dot, suffix = entry.partition(".")
        part = suffix if dot else None

    return MeshNameInfo(
        raw_name=name, render_group=render_group, base_name=base,
        specular=_param(params, 0, 1.0), bump_repeat1=_param(params, 1, 0.0),
        bump_repeat2=_param(params, 2, 0.0), extra_params=[t for t in extra],
        optional_visible=visible, optional_group=group, optional_item=item, optional_part=part,
        join_name=join_name, part_index=part_index)


def _build_mesh(name: str, uv_count: int, textures: List[XpsTexture], vertices: List[XpsVertex],
                faces: List[Tuple[int, int, int]]) -> XpsMesh:
    info = parse_mesh_name(name)
    return XpsMesh(
        name=name, uv_layer_count=uv_count, textures=textures, vertices=vertices, faces=faces,
        render_group=info.render_group, mesh_base_name=info.base_name, specular=info.specular,
        bump_repeat1=info.bump_repeat1, bump_repeat2=info.bump_repeat2,
        optional_visible=info.optional_visible, optional_group=info.optional_group,
        optional_item=info.optional_item, optional_part=info.optional_part,
        extra_params=info.extra_params, join_name=info.join_name, part_index=info.part_index)


# --------------------------------------------------------------------------- validation


def validate_model(model: XpsModel, weight_tolerance: float = 0.01) -> List[str]:
    """Return structural problems: bad parents/cycles, out-of-range indices, weights summing above 1.

    Vertices whose weights sum to *less* than 1 (including all-zero) are not
    reported; XPS tolerates them and the converter has to normalise anyway.
    """
    issues: List[str] = []
    bones = model.bones
    bone_count = len(bones)
    for i, bone in enumerate(bones):
        parent = bone.parent_index
        if parent < -1 or parent >= bone_count or parent == i:
            issues.append(f"bone {i} {bone.name!r}: invalid parent index {parent}")
    resolved = [False] * bone_count
    for i in range(bone_count):
        path = []
        on_path = set()
        j = i
        while 0 <= j < bone_count and not resolved[j]:
            if j in on_path:
                issues.append(f"bone hierarchy cycle through bone {j} {bones[j].name!r}")
                break
            on_path.add(j)
            path.append(j)
            j = bones[j].parent_index
        for k in path:
            resolved[k] = True

    for mi, mesh in enumerate(model.meshes):
        vertex_count = len(mesh.vertices)
        bad_faces = sum(1 for a, b, c in mesh.faces
                        if a >= vertex_count or b >= vertex_count or c >= vertex_count)
        if bad_faces:
            issues.append(f"mesh {mi} {mesh.name!r}: {bad_faces} triangles index past {vertex_count} vertices")
        for tex in mesh.textures:
            if mesh.uv_layer_count and tex.uv_layer >= mesh.uv_layer_count:
                issues.append(f"mesh {mi} {mesh.name!r}: texture {tex.file!r} uses UV layer "
                              f"{tex.uv_layer} of {mesh.uv_layer_count}")
        bad_index = over = negative = non_finite = 0
        for v in mesh.vertices:
            total = 0.0
            for index, weight in zip(v.bone_indices, v.bone_weights):
                if weight != 0.0 and not 0 <= index < bone_count:
                    bad_index += 1
                if weight < 0.0:
                    negative += 1
                total += weight
            if total > 1.0 + weight_tolerance:
                over += 1
            x, y, z = v.position
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                non_finite += 1
        if bad_index:
            issues.append(f"mesh {mi} {mesh.name!r}: {bad_index} weighted bone indices out of range")
        if over:
            issues.append(f"mesh {mi} {mesh.name!r}: {over} vertices with weight sum > 1 + {weight_tolerance}")
        if negative:
            issues.append(f"mesh {mi} {mesh.name!r}: {negative} negative weights")
        if non_finite:
            issues.append(f"mesh {mi} {mesh.name!r}: {non_finite} vertices with non-finite positions")
    return issues


def _log_warnings(model: XpsModel) -> None:
    for message in model.warnings:
        log.warning("%s: %s", model.source_path or "<data>", message)
