#!/usr/bin/env python3
"""Survey the XPS / XNALara models on this machine: scale, skeleton naming, materials, format quirks.

Examples::

    python scripts/survey_xps_corpus.py                       # default roots + extra samples
    python scripts/survey_xps_corpus.py E:/mywork --no-extras --out report.md
    python scripts/survey_xps_corpus.py --json survey.json --stdout-only

The Markdown report is written between ``BEGIN GENERATED`` / ``END GENERATED``
markers, so hand-written text around the generated block survives re-runs.
All coordinates are reported in the XNA convention of the files (+Y up).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from xps_to_pmx.core.xps import (  # noqa: E402
    XpsModel,
    describe_render_group,
    load_pose,
    parse_xps_data,
    validate_model,
)

DEFAULT_ROOTS = ["E:/day_work", "E:/4090"]
DEFAULT_EXCLUDES = ["E:/code/model_tools"]
#: Same-character samples with known-good PMX conversions (scale comparison later).
DEFAULT_EXTRAS = [
    "E:/mywork/add_on/Purifier (Inase)/xps.xps",
    "E:/mywork/add_on/Purifier (Inase)/normal pose.xps",
    "E:/mywork/add_on/inase (purifier)_lezisell-A/xps.xps",
    "E:/mywork/mymodel/Purifier (Inase)/xps-A.xps",
    "E:/day_work/work/gantz/already/(Gantz) Reika Shimohira/xps.xps",
    "E:/day_work/work/gantz/already/Tifa Gantz/xps.xps",
]
DEFAULT_OUT = REPO_ROOT / "docs" / "research_notes" / "XPS 转 PMX 方案调研" / "09_本机XPS样本测量.md"
BEGIN_MARK = "<!-- BEGIN GENERATED: scripts/survey_xps_corpus.py -->"
END_MARK = "<!-- END GENERATED -->"
#: Artifact of repeated "save as" in one folder; skipped only when it fails to parse.
WEIRD_DUPLICATE_NAME = re.compile(r"(\.mesh\.ascii){2,}$", re.IGNORECASE)

# --------------------------------------------------------------------------- bone naming

#: Core body bones of the XNALara "generic" convention (left side only, lower case).
GENERIC_CORE = (
    "root hips", "pelvis", "spine lower", "spine upper", "head neck lower", "head neck upper",
    "arm left shoulder 1", "arm left shoulder 2", "arm left elbow", "arm left wrist",
    "leg left thigh", "leg left knee", "leg left ankle", "leg left toes",
)
#: Bones following the generic phrase style ("arm left elbow", "head eyelid upper left", ...).
#: Names starting with "unused" are an XPS tool marker and are counted separately.
GENERIC_STYLE = re.compile(
    r"^(root (ground|hips)|pelvis|spine (lower|middle|upper)( b)?|head\b.*|"
    r"(arm|leg) (left|right)\b.*|(breast|boob) (left|right)\b.*)$")
#: Core body bones of DAZ Genesis 3/8 (lower case); 8 or more of them means a DAZ skeleton.
DAZ_CORE = (
    "abdomenlower", "abdomenupper", "chestlower", "chestupper", "necklower", "neckupper",
    "lcollar", "lshldrbend", "lshldrtwist", "lforearmbend", "lforearmtwist", "lhand",
    "lthighbend", "lthightwist", "lshin", "lfoot", "lmetatarsals", "ltoe",
)
#: Any DAZ-specific name (feet, carpals, face rig...).  These also survive as
#: fragments in rigs that are otherwise something else, so they only add a tag.
DAZ_MARKERS = re.compile(
    r"^(abdomen(lower|upper)|chest(lower|upper)|neck(lower|upper)|lowerjaw|upperjaw|"
    r"upperfacerig|lowerfacerig|centerbrow|midnosebridge|tongue0\d|"
    r"[lr](collar|shldr(bend|twist)|forearm(bend|twist)|hand|thigh(bend|twist)|shin|foot|"
    r"metatarsals|toe|bigtoe(_2)?|smalltoe\d(_2)?|carpal\d|thumb\d|index\d|mid\d|ring\d|pinky\d|"
    r"pectoral|eye|ear|brow(inner|mid|outer)|cheek(lower|upper)|eyelid(lower|upper)\w*|"
    r"lip(belly|corner|lower\w*|upper\w*)|nostril|squintinner|squintouter|jawclench|"
    r"nasolabial\w*))$")
#: Other conventions seen in the corpus: (label, pattern, minimum number of matching bones).
OTHER_FAMILIES: Sequence[Tuple[str, re.Pattern, int]] = (
    # Blender Auto-Rig Pro: c_pos / c_traj controllers, ".x" centre and ".l"/".r" side suffixes.
    ("auto_rig_pro", re.compile(r"^(c_pos|c_traj|(c_)?[a-z0-9_]+\.(x|l|r)(_end)?)$"), 10),
    ("3dsmax_biped", re.compile(r"^bip0*1([ _-]|$)", re.IGNORECASE), 5),
    ("valve_biped", re.compile(r"^valvebiped\.", re.IGNORECASE), 5),
    ("mixamo", re.compile(r"^mixamorig\d*:", re.IGNORECASE), 5),
    ("unreal", re.compile(r"^(spine_0\d|clavicle_[lr]|upperarm_[lr]|lowerarm_[lr]|thigh_[lr]|calf_[lr]|"
                          r"ball_[lr]|hand_[lr]|(calf|thigh|upperarm|lowerarm)_twist_0\d_[lr])$",
                          re.IGNORECASE), 5),
    # RE Engine style ("l leg femur", "r arm humerus twist 3 H", "COG").
    ("re_engine", re.compile(r"^[lr] (leg|arm|hand|shoulder|scapula) ", re.IGNORECASE), 5),
    # "Master" / "M_Hips" / "L_Thigh" / "R_Forearm_twistX3" with _ST/_SR helper suffixes.
    ("lr_prefix", re.compile(r"^[LRM]_[A-Z]"), 10),
    ("mmd_japanese", re.compile(r"(センター|上半身|下半身|左足|右足|左腕|右腕|頭)"), 3),
    ("humanoid_camel", re.compile(r"^(hips|spine\d?|chest|upperchest|neck|head|"
                                  r"(left|right)(upleg|upperleg|leg|lowerleg|foot|toebase|toes|shoulder|"
                                  r"arm|upperarm|forearm|lowerarm|hand))$", re.IGNORECASE), 6),
)
#: Aggregation of the detailed labels into the three top-level classes of the brief.
def top_level_class(label: str) -> str:
    if label.startswith("daz_g8"):
        return "daz_g8"
    if label.startswith("xnalara_generic"):
        return "xnalara_generic"
    return "other"


def classify_bone_names(names: Sequence[str]) -> Tuple[str, int, int, int, str]:
    """Guess the naming convention of a skeleton.

    Returns ``(label, generic_core_hits, daz_core_hits, generic_style_hits, tags)``.
    ``label`` is ``daz_g8`` / ``daz_g8+xnalara_generic`` (8+ DAZ core bones),
    ``xnalara_generic`` (7+ of the 14 generic core bones), ``other:<family>``,
    ``xnalara_generic(partial)``, ``prop(<=3 bones)``, ``other`` or ``none``;
    ``tags`` lists further conventions present as fragments (e.g. DAZ toes in a
    Valve rig).
    """
    if not names:
        return "none", 0, 0, 0, ""
    stripped = [n.strip() for n in names]
    lowered = [n.lower() for n in stripped]
    present = set(lowered)
    generic_core = sum(1 for n in GENERIC_CORE if n in present)
    daz_core = sum(1 for n in DAZ_CORE if n in present)
    generic_style = sum(1 for n in lowered if GENERIC_STYLE.match(n))
    daz_style = sum(1 for n in lowered if DAZ_MARKERS.match(n))
    family_hits: Dict[str, int] = {}
    for family, pattern, minimum in OTHER_FAMILIES:
        hits = sum(1 for n in stripped if pattern.search(n))
        if hits >= minimum:
            family_hits[family] = hits
    if daz_core >= 8:
        label = "daz_g8+xnalara_generic" if (generic_core >= 3 or generic_style >= 10) else "daz_g8"
    elif generic_core >= 7:
        label = "xnalara_generic"
    elif family_hits:
        label = "other:" + max(family_hits, key=lambda k: family_hits[k])
    elif generic_core >= 3:
        label = "xnalara_generic(partial)"
    elif len(names) <= 3:
        label = "prop(<=3 bones)"
    else:
        label = "other"
    primary_family = label.split(":", 1)[1] if label.startswith("other:") else None
    tags = [f"{fam}×{hits}" for fam, hits in sorted(family_hits.items(), key=lambda kv: -kv[1])
            if fam != primary_family]
    if daz_core < 8 and daz_style >= 5:
        tags.append(f"daz_fragments×{daz_style}")
    if not label.startswith(("xnalara_generic", "daz_g8+")) and generic_style >= 5:
        tags.append(f"generic_style×{generic_style}")
    return label, generic_core, daz_core, generic_style, ", ".join(tags)


def _landmark_key(name: str) -> str:
    key = name.strip().lower()
    key = re.sub(r"\.(x|l|r)$", "", key)  # Auto-Rig Pro centre/side suffix
    return re.sub(r"[\s_\-]+", " ", key)


HIPS_EXACT = ("root hips", "pelvis", "hips", "hip", "bip001 pelvis", "bip01 pelvis",
              "valvebiped.bip01 pelvis", "m hips", "cog")
HEAD_EXACT = ("head neck upper", "head", "bip001 head", "bip01 head", "valvebiped.bip01 head1", "m head")
HIPS_FALLBACK = re.compile(r"(^|[\s.:])(pelvis|hips?)$")
HEAD_FALLBACK = re.compile(r"(^|[\s.:])head1?$")


def find_landmark(model: XpsModel, exact: Sequence[str], fallback: re.Pattern
                  ) -> Tuple[Optional[str], Optional[float]]:
    """First bone matching ``exact`` (normalised names, in priority order), else ``fallback``."""
    by_key: Dict[str, int] = {}
    for i, bone in enumerate(model.bones):
        by_key.setdefault(_landmark_key(bone.name), i)
    for name in exact:
        if name in by_key:
            bone = model.bones[by_key[name]]
            return bone.name, bone.position[1]
    for bone in model.bones:
        if fallback.search(_landmark_key(bone.name)):
            return bone.name, bone.position[1]
    if exact is HIPS_EXACT:
        for bone in model.bones:  # Auto-Rig Pro deform root sits at the hips
            if bone.name.strip().lower() == "root.x":
                return bone.name, bone.position[1]
    return None, None


# --------------------------------------------------------------------------- records


@dataclass
class Record:
    idx: int
    path: str
    display: str
    size: int
    sha1: str = ""
    duplicate_of: Optional[int] = None
    status: str = "ok"  # ok | partial | failed | skipped | duplicate
    error: str = ""
    fmt: str = ""
    version: str = ""
    seconds: float = 0.0
    bones: int = 0
    meshes: int = 0
    vertices: int = 0
    faces: int = 0
    bbox_min: Optional[Tuple[float, float, float]] = None
    bbox_max: Optional[Tuple[float, float, float]] = None
    height: Optional[float] = None
    height_default_visible: Optional[float] = None
    ground: Optional[float] = None
    width: Optional[float] = None
    depth: Optional[float] = None
    skeleton_height: Optional[float] = None
    roots: List[str] = field(default_factory=list)
    convention: str = ""
    generic_core: int = 0
    daz_core: int = 0
    generic_style: int = 0
    convention_tags: str = ""
    top_class: str = ""
    first_bones: List[str] = field(default_factory=list)
    unused_bones: int = 0
    render_groups: List[Tuple[Optional[int], bool, bool]] = field(default_factory=list)
    texture_exts: Dict[str, int] = field(default_factory=dict)
    optional_shown: int = 0
    optional_hidden: int = 0
    optional_groups: List[str] = field(default_factory=list)
    npart_meshes: int = 0
    blender_suffix_meshes: int = 0
    flags: Dict[int, int] = field(default_factory=dict)
    swizzle: str = ""
    default_pose_bones: Optional[int] = None
    settings_items: List[Tuple[int, int, int]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    hips_bone: Optional[str] = None
    hips_y: Optional[float] = None
    head_bone: Optional[str] = None
    head_y: Optional[float] = None
    is_character: bool = False
    is_pose_variant: bool = False
    weight_over: int = 0
    weight_under: int = 0
    weight_zero: int = 0
    max_influences: int = 0
    over4_vertices: int = 0
    layout: str = ""
    trailing_bytes: int = 0
    pmx_siblings: List[str] = field(default_factory=list)
    #: (pmx file, pmx bbox height, pmx height / xps height, error) for sibling PMX files.
    pmx: List[Tuple[str, Optional[float], Optional[float], str]] = field(default_factory=list)
    mesh_names: List[str] = field(default_factory=list)
    non_ascii_names: int = 0
    non_ascii_examples: List[str] = field(default_factory=list)


def _swizzle(flags_raw: Dict[int, int]) -> str:
    """Decode tangent-space flags 3/4/5; values seem to be 2*source_channel + invert."""
    if not any(k in flags_raw for k in (3, 4, 5)):
        return ""
    parts = []
    for axis, key, default in (("X", 3, 0), ("Y", 4, 3), ("Z", 5, 4)):
        value = flags_raw.get(key, default)
        channel = "RGB"[value // 2] if value // 2 < 3 else "?"
        parts.append(f"{axis}={channel}{'-' if value % 2 else '+'}")
    return " ".join(parts)


def analyse(record: Record, model: XpsModel) -> None:
    record.fmt = "ascii" if model.is_ascii else "bin"
    record.version = model.version or "no header"
    record.bones = len(model.bones)
    record.meshes = len(model.meshes)
    record.layout = ("tan" if model.has_tangents else "notan") + "+" + ("varw" if model.has_variable_weights else "w4")
    record.trailing_bytes = model.trailing_bytes
    record.warnings = list(model.warnings)
    record.status = "ok" if model.complete else "partial"

    inf = float("inf")
    mn = [inf, inf, inf]
    mx = [-inf, -inf, -inf]
    vis_min_y, vis_max_y = inf, -inf
    vertices = faces = 0
    over = under = zero = max_infl = over4 = 0
    for mesh in model.meshes:
        hidden = mesh.optional_visible is False
        vertices += len(mesh.vertices)
        faces += len(mesh.faces)
        for v in mesh.vertices:
            x, y, z = v.position
            if x < mn[0]:
                mn[0] = x
            if x > mx[0]:
                mx[0] = x
            if y < mn[1]:
                mn[1] = y
            if y > mx[1]:
                mx[1] = y
            if z < mn[2]:
                mn[2] = z
            if z > mx[2]:
                mx[2] = z
            if not hidden:
                if y < vis_min_y:
                    vis_min_y = y
                if y > vis_max_y:
                    vis_max_y = y
            weights = v.bone_weights
            if weights:
                total = 0.0
                nonzero = 0
                for w in weights:
                    total += w
                    if w > 0.0:
                        nonzero += 1
                if total > 1.01:
                    over += 1
                elif total == 0.0:
                    zero += 1
                elif total < 0.99:
                    under += 1
                if nonzero > max_infl:
                    max_infl = nonzero
                if nonzero > 4:
                    over4 += 1
    record.vertices, record.faces = vertices, faces
    record.weight_over, record.weight_under, record.weight_zero = over, under, zero
    record.max_influences, record.over4_vertices = max_infl, over4
    if mn[0] <= mx[0]:
        record.bbox_min = (mn[0], mn[1], mn[2])
        record.bbox_max = (mx[0], mx[1], mx[2])
        record.height = mx[1] - mn[1]
        record.width = mx[0] - mn[0]
        record.depth = mx[2] - mn[2]
        record.ground = mn[1]
    if vis_min_y <= vis_max_y:
        record.height_default_visible = vis_max_y - vis_min_y
    if model.bones:
        ys = [b.position[1] for b in model.bones]
        record.skeleton_height = max(ys) - min(ys)

    names = [b.name for b in model.bones]
    record.roots = [b.name for b in model.bones if b.parent_index < 0]
    (record.convention, record.generic_core, record.daz_core, record.generic_style,
     record.convention_tags) = classify_bone_names(names)
    record.top_class = top_level_class(record.convention)
    record.first_bones = names[:12]
    record.unused_bones = sum(1 for n in names if n.strip().lower().startswith("unused"))
    record.hips_bone, record.hips_y = find_landmark(model, HIPS_EXACT, HIPS_FALLBACK)
    record.head_bone, record.head_y = find_landmark(model, HEAD_EXACT, HEAD_FALLBACK)
    # A full character: hips and head found, mesh covers the head and reaches the lower legs.
    record.is_character = (record.hips_y is not None and record.head_y is not None
                           and record.head_y > record.hips_y and vertices >= 5000
                           and record.bbox_max is not None and record.bbox_max[1] >= record.head_y
                           and record.bbox_min[1] <= 0.3 * record.hips_y)

    groups = {}
    exts: Counter = Counter()
    opt_groups = set()
    for mesh in model.meshes:
        rg = mesh.render_group
        info = describe_render_group(rg)
        groups[rg if rg is not None else -1] = (rg, info.alpha, info.known)
        for tex in mesh.textures:
            exts[tex.extension or "(none)"] += 1
        if mesh.optional_visible is True:
            record.optional_shown += 1
        elif mesh.optional_visible is False:
            record.optional_hidden += 1
        if mesh.optional_group:
            opt_groups.add(mesh.optional_group)
        if mesh.part_index is not None or mesh.join_name != mesh.name:
            record.npart_meshes += 1
        if re.search(r"\.\d{3}$", mesh.name):
            record.blender_suffix_meshes += 1
    record.render_groups = [groups[k] for k in sorted(groups)]
    record.texture_exts = dict(exts.most_common())
    record.optional_groups = sorted(opt_groups)
    record.mesh_names = [m.name for m in model.meshes]
    all_names = names + record.mesh_names + [t.file for m in model.meshes for t in m.textures]
    odd = [n for n in all_names if any(ord(c) > 127 for c in n)]
    record.non_ascii_names = len(odd)
    record.non_ascii_examples = odd[:3]

    if model.header is not None:
        record.flags = dict(sorted(model.header.flags_raw.items()))
        record.swizzle = _swizzle(model.header.flags_raw)
        record.settings_items = list(model.header.settings_items)
        if model.header.default_pose:
            record.default_pose_bones = len(model.header.default_pose)
    record.issues = validate_model(model)


# --------------------------------------------------------------------------- discovery


def _norm(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


def discover(roots: Sequence[str], excludes: Sequence[str]) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Return ([(path, root_label)], [pose paths]) for model files under ``roots``."""
    excluded = [_norm(e) for e in excludes]
    models: List[Tuple[str, str]] = []
    poses: List[str] = []
    for root in roots:
        if not os.path.isdir(root):
            print(f"[warn] root not found: {root}", file=sys.stderr)
            continue
        label = Path(root).name or root
        for dirpath, dirnames, filenames in os.walk(root):
            ndir = _norm(dirpath)
            if any(ndir == e or ndir.startswith(e + os.sep) for e in excluded):
                dirnames[:] = []
                continue
            dirnames.sort()
            for name in sorted(filenames):
                lower = name.lower()
                if ".bak" in lower:
                    continue
                full = os.path.join(dirpath, name)
                if lower.endswith((".xps", ".mesh", ".ascii")):
                    models.append((full, label))
                elif lower.endswith(".pose"):
                    poses.append(full)
    return models, poses


def display_path(path: str, root_label: str, roots: Sequence[str]) -> str:
    for root in roots:
        try:
            rel = os.path.relpath(path, root)
        except ValueError:
            continue
        if not rel.startswith(".."):
            return (Path(root).name + "/" + rel).replace("\\", "/")
    drive, rest = os.path.splitdrive(path)
    return rest.replace("\\", "/").lstrip("/")


# --------------------------------------------------------------------------- PMX comparison


def pmx_vertex_bbox(path: str) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], int]:
    """Minimal PMX 2.0/2.1 reader: bounding box of the vertex positions (MMD units, +Y up).

    Only the header, the four info strings and the vertex block are walked;
    used to compare existing PMX conversions with their XPS sources.
    """
    import struct
    data = Path(path).read_bytes()
    if data[:4] != b"PMX ":
        raise ValueError("not a PMX file")
    pos = 8  # magic + float version
    global_count = data[pos]
    pos += 1
    globals_ = data[pos:pos + global_count]
    pos += global_count
    additional_uv = globals_[1]
    bone_size = globals_[5]
    for _ in range(4):  # model name / english name / comment / english comment
        (length,) = struct.unpack_from("<i", data, pos)
        pos += 4 + length
    (count,) = struct.unpack_from("<i", data, pos)
    pos += 4
    fixed = 32 + 16 * additional_uv  # position, normal, uv, additional vec4s
    deform_sizes = {0: bone_size, 1: 2 * bone_size + 4, 2: 4 * bone_size + 16,
                    3: 2 * bone_size + 4 + 36, 4: 4 * bone_size + 16}
    position = struct.Struct("<3f")
    inf = float("inf")
    mn = [inf, inf, inf]
    mx = [-inf, -inf, -inf]
    for _ in range(count):
        x, y, z = position.unpack_from(data, pos)
        pos += fixed
        deform = data[pos]
        pos += 1 + deform_sizes[deform] + 4  # weights + edge scale
        if x < mn[0]:
            mn[0] = x
        if x > mx[0]:
            mx[0] = x
        if y < mn[1]:
            mn[1] = y
        if y > mx[1]:
            mx[1] = y
        if z < mn[2]:
            mn[2] = z
        if z > mx[2]:
            mx[2] = z
    return (mn[0], mn[1], mn[2]), (mx[0], mx[1], mx[2]), count


# --------------------------------------------------------------------------- formatting


def esc(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def fnum(value: Optional[float], digits: int = 3) -> str:
    return "" if value is None else f"{value:.{digits}f}"


def rg_text(groups: Iterable[Tuple[Optional[int], bool, bool]]) -> str:
    out = []
    for rg, alpha, known in groups:
        label = "none(5)" if rg is None else str(rg)
        if alpha:
            label += "α"
        if not known:
            label += "?"
        out.append(label)
    return " ".join(out)


def warn_text(warnings: Sequence[str]) -> str:
    short = []
    for w in warnings:
        m = re.match(r"(\d+) (zero|unknown) bytes after the last mesh", w)
        if m:
            short.append(f"trailing {m.group(1)}B")
        elif "truncated or corrupt" in w:
            short.append("TRUNCATED")
        elif "vertex layout implied" in w:
            short.append("layout-fallback")
        elif "not valid UTF-8" in w:
            short.append("non-UTF-8 strings")
        else:
            short.append(w[:60])
    return "; ".join(short)


def stats_line(values: Sequence[float], digits: int = 3) -> str:
    vals = sorted(v for v in values if v is not None and v == v and abs(v) != float("inf"))
    if not vals:
        return "n=0"
    q = statistics.quantiles(vals, n=4) if len(vals) >= 2 else [vals[0]] * 3
    return (f"n={len(vals)}, min={vals[0]:.{digits}f}, P25={q[0]:.{digits}f}, "
            f"median={statistics.median(vals):.{digits}f}, P75={q[2]:.{digits}f}, max={vals[-1]:.{digits}f}")


def build_markdown(records: List[Record], poses: List[Tuple[str, int, str]], args: argparse.Namespace,
                   total_seconds: float) -> str:
    out: List[str] = []
    w = out.append
    parsed = [r for r in records if r.status in ("ok", "partial")]
    unique = [r for r in parsed if r.duplicate_of is None]
    w(BEGIN_MARK)
    w("")
    w(f"> 生成命令: `{args.command_line}`  ")
    w(f"> 扫描根目录: {', '.join(args.roots)};排除: {', '.join(args.exclude)};额外样本 {len(args.extras_used)} 个  ")
    w(f"> 文件 {len(records)} 个(唯一且解析成功 {len(unique)},与前面某文件字节相同而未重复解析 "
      f"{sum(1 for r in records if r.duplicate_of is not None)};"
      f"失败 {sum(1 for r in records if r.status == 'failed')},跳过 {sum(1 for r in records if r.status == 'skipped')});"
      f"总耗时 {total_seconds:.1f} s(含哈希与统计),纯解析 {sum(r.seconds for r in records):.1f} s")
    w("")

    w("### A. 几何与尺度(XNA 坐标,+Y 向上;单位为文件原始单位)")
    w("")
    w("| # | 文件 | 格式 | 版本 | 骨骼 | 网格 | 顶点 | 三角面 | 高度 Y | 默认可见高度 | 地面 minY | 宽 X | 深 Z | "
      "bbox min (x,y,z) | bbox max (x,y,z) | 髋骨 Y | 头骨 Y | 解析 s |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in records:
        if r.status in ("failed", "skipped"):
            w(f"| {r.idx} | {esc(r.display)} | — | — | | | | | | | | | | | | | | **{r.status}**: {esc(r.error[:120])} |")
            continue
        if r.duplicate_of is not None:
            w(f"| {r.idx} | {esc(r.display)} | 与 #{r.duplicate_of} 字节相同 | | | | | | | | | | | | | | | |")
            continue
        bmin = "({:.3f}, {:.3f}, {:.3f})".format(*r.bbox_min) if r.bbox_min else ""
        bmax = "({:.3f}, {:.3f}, {:.3f})".format(*r.bbox_max) if r.bbox_max else ""
        hips = f"{fnum(r.hips_y)} ({esc(r.hips_bone)})" if r.hips_bone else ""
        head = f"{fnum(r.head_y)} ({esc(r.head_bone)})" if r.head_bone else ""
        status = "" if r.status == "ok" else " ⚠partial"
        w(f"| {r.idx} | {esc(r.display)}{status} | {r.fmt} | {r.version} | {r.bones} | {r.meshes} | {r.vertices} | "
          f"{r.faces} | **{fnum(r.height)}** | {fnum(r.height_default_visible)} | {fnum(r.ground)} | {fnum(r.width)} | "
          f"{fnum(r.depth)} | {bmin} | {bmax} | {hips} | {head} | {r.seconds:.2f} |")
    w("")

    w("### B. 骨架与命名")
    w("")
    w("| # | 根骨骼 (parent −1) | 命名约定猜测 | 附加标签 | generic 核心/14 | DAZ 核心/18 | unused* | 前 12 个骨骼名 |")
    w("|---|---|---|---|---|---|---|---|")
    for r in unique:
        roots = ", ".join(r.roots[:4]) + (f" …(+{len(r.roots) - 4})" if len(r.roots) > 4 else "")
        w(f"| {r.idx} | {esc(roots)} | {r.convention} | {esc(r.convention_tags)} | {r.generic_core} | {r.daz_core} | {r.unused_bones} | "
          f"{esc(', '.join(r.first_bones))} |")
    w("")

    w("### C. 材质、标志、权重与警告")
    w("")
    w("| # | 渲染组 (α=alpha) | 贴图扩展名 | 可选项 +/− | 可选组 | nPart | .00N 后缀 | flags 原值 (id=value) | 法线 swizzle | "
      "默认姿势 | 权重和>1.01 | 权重和<0.99 | 全零权重 | 最大影响数 | >4 影响顶点 | 校验问题 | 警告 |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in unique:
        exts = " ".join(f"{k}×{v}" for k, v in r.texture_exts.items())
        flags = ",".join(f"{k}={v}" for k, v in r.flags.items())
        opt = f"{r.optional_shown}/{r.optional_hidden}" if (r.optional_shown or r.optional_hidden) else ""
        pose = "" if r.default_pose_bones is None else f"{r.default_pose_bones} 骨"
        w(f"| {r.idx} | {rg_text(r.render_groups)} | {esc(exts)} | {opt} | {esc(', '.join(r.optional_groups))} | "
          f"{r.npart_meshes or ''} | {r.blender_suffix_meshes or ''} | {flags} | {r.swizzle} | {pose} | "
          f"{r.weight_over or ''} | {r.weight_under or ''} | {r.weight_zero or ''} | {r.max_influences} | "
          f"{r.over4_vertices or ''} | {len(r.issues) or ''} | {esc(warn_text(r.warnings))} |")
    w("")

    # ---------------------------------------------------------------- summaries
    w("### D. 汇总")
    w("")
    chars = [r for r in unique if r.is_character and r.status == "ok"]
    primary = [r for r in chars if not r.is_pose_variant]
    w("**D1. 高度分布**(唯一文件;\"角色\" = 找到髋骨与头骨、头骨高于髋骨、顶点 ≥ 5000、"
      "网格覆盖头骨且最低点 ≤ 0.3×髋骨高度)")
    w("")
    w(f"- 全部唯一模型的 bbox 高度: {stats_line([r.height for r in unique if r.height is not None])}")
    w(f"- 角色模型 bbox 高度: {stats_line([r.height for r in chars])}")
    w(f"- 角色模型(排除文件名含 pose 的姿势变体): {stats_line([r.height for r in primary])}")
    w(f"- 角色模型默认可见高度(排除 `-` 默认隐藏网格): "
      f"{stats_line([r.height_default_visible for r in primary if r.height_default_visible is not None])}")
    w(f"- 角色模型地面偏移 minY: {stats_line([r.ground for r in primary if r.ground is not None])}")
    w(f"- 角色模型 头骨Y / bbox高度: "
      f"{stats_line([r.head_y / r.height for r in primary if r.height], 3)}")
    w(f"- 角色模型 髋骨Y / bbox高度: "
      f"{stats_line([r.hips_y / r.height for r in primary if r.height], 3)}")
    w(f"- 角色模型 骨架高度(骨骼 head Y 极差): "
      f"{stats_line([r.skeleton_height for r in primary if r.skeleton_height is not None])}")
    w(f"- 角色模型 头骨 Y(绝对值): {stats_line([r.head_y for r in primary])}")
    w(f"- 角色模型 髋骨 Y(绝对值): {stats_line([r.hips_y for r in primary])}")
    w(f"- 角色模型 bbox高度 − 头骨Y(头骨以上的网格,含发型/帽子/耳朵等): "
      f"{stats_line([r.height - (r.head_y - r.ground) for r in primary])}")
    ranked = sorted(primary, key=lambda r: r.height)
    if ranked:
        w("- bbox 最矮 5 个: " + "; ".join(f"#{r.idx} {esc(Path(r.display).parent.name)} H={r.height:.3f} 头骨Y={r.head_y:.3f}" for r in ranked[:5]))
        w("- bbox 最高 5 个: " + "; ".join(f"#{r.idx} {esc(Path(r.display).parent.name)} H={r.height:.3f} 头骨Y={r.head_y:.3f}" for r in ranked[-5:]))
    outliers = [r for r in primary if r.height is not None and not 1.3 <= r.height <= 2.1]
    if outliers:
        w("- 高度在 1.3–2.1 之外的角色: " + "; ".join(f"#{r.idx} {esc(r.display)} = {r.height:.3f}" for r in outliers))
    non_chars = [r for r in unique if not r.is_character]
    if non_chars:
        w(f"- 非角色(道具/部件/无骨架)共 {len(non_chars)} 个: " + "; ".join(
            f"#{r.idx} {esc(Path(r.display).parent.name + '/' + Path(r.display).name)} "
            f"(H={fnum(r.height)}, bones={r.bones})" for r in non_chars))
    w("")

    w("**D2. 骨骼命名约定**(唯一文件)")
    w("")
    top = Counter(r.top_class for r in unique)
    w("顶层分类: " + ", ".join(f"`{k}` {v}" for k, v in top.most_common()) + f"(共 {len(unique)} 个唯一文件)")
    w("")
    conv = Counter(r.convention for r in unique)
    w("| 约定 | 数量 | 文件 # |")
    w("|---|---|---|")
    for label, count in conv.most_common():
        ids = ", ".join(str(r.idx) for r in unique if r.convention == label)
        w(f"| {label} | {count} | {ids} |")
    w("")

    w("**D3. 全语料使用的渲染组**(按网格计数,唯一文件)")
    w("")
    rg_models: Dict[Optional[int], set] = {}
    for r in unique:
        seen = set()
        for rg, alpha, known in r.render_groups:
            seen.add(rg)
        for rg in seen:
            rg_models.setdefault(rg, set()).add(r.idx)
    w("| RG | alpha | 贴图槽 | 光照 | 使用该 RG 的模型数 | 网格数 |")
    w("|---|---|---|---|---|---|")
    for rg in sorted(rg_models, key=lambda k: (k is None, k if k is not None else 0)):
        info = describe_render_group(rg)
        label = "无前缀(按 5)" if rg is None else str(rg)
        w(f"| {label} | {'是' if info.alpha else '否'} | {', '.join(info.texture_slots)} | {info.shading} | "
          f"{len(rg_models[rg])} | {args.rg_mesh_counts.get(rg, 0)} |")
    w("")

    w("**D4. 版本 / 布局直方图**(唯一文件)")
    w("")
    ver = Counter((r.fmt, r.version, r.layout) for r in unique)
    w("| 格式 | 版本 | 顶点布局 | 数量 |")
    w("|---|---|---|---|")
    for (fmt, version, layout), count in sorted(ver.items(), key=lambda kv: (-kv[1], kv[0])):
        w(f"| {fmt} | {version} | {layout} | {count} |")
    w("")

    w("**D5. 权重、可选项、命名细节**(唯一文件)")
    w("")
    w(f"- 有顶点权重和 > 1.01 的模型: {sum(1 for r in unique if r.weight_over)} / {len(unique)}"
      f"(顶点合计 {sum(r.weight_over for r in unique)})")
    w(f"- 有顶点权重和 < 0.99(非零)的模型: {sum(1 for r in unique if r.weight_under)};"
      f"有全零权重顶点的模型: {sum(1 for r in unique if r.weight_zero)}")
    w(f"- 有 > 4 个非零影响顶点的模型: {sum(1 for r in unique if r.over4_vertices)}"
      f"(最大影响数分布: {dict(sorted(Counter(r.max_influences for r in unique).items()))})")
    w(f"- 含可选项(+/−)的模型: {sum(1 for r in unique if r.optional_shown or r.optional_hidden)};"
      f"使用 `|` 分组的模型: {sum(1 for r in unique if r.optional_groups)}")
    w(f"- 含 nPart 分片网格的模型: {sum(1 for r in unique if r.npart_meshes)};"
      f"网格名以 Blender 式 `.00N` 结尾的模型: {sum(1 for r in unique if r.blender_suffix_meshes)}")
    w(f"- 含 `unused*` 骨骼的模型: {sum(1 for r in unique if r.unused_bones)}")
    odd = [r for r in unique if r.non_ascii_names]
    w(f"- 骨骼/网格/贴图名含非 ASCII 字符的模型: {len(odd)}"
      + ("(" + "; ".join(f"#{r.idx}: {esc(', '.join(r.non_ascii_examples))}" for r in odd[:8]) + ")" if odd else ""))
    w(f"- 头部嵌入默认姿势(settings type 1 长度>0)的模型: {sum(1 for r in unique if r.default_pose_bones)}")
    flag_sets = Counter(",".join(f"{k}={v}" for k, v in r.flags.items()) or "(无 / 旧格式)" for r in unique if r.fmt == "bin")
    w("- 二进制文件 flags 组合: " + "; ".join(f"`{k}` ×{v}" for k, v in flag_sets.most_common()))
    items = Counter(str(r.settings_items) for r in unique if r.settings_items)
    w("- settings 条目序列: " + "; ".join(f"`{k}` ×{v}" for k, v in items.most_common()))
    wc = Counter()
    for r in unique:
        for text in warn_text(r.warnings).split("; "):
            if text:
                wc[re.sub(r"\d+B", "NB", text)] += 1
    w("- 警告类型: " + ("; ".join(f"{k} ×{v}" for k, v in wc.most_common()) or "无"))
    tb = Counter(r.trailing_bytes for r in unique if r.trailing_bytes)
    w(f"- 尾随字节长度分布: {dict(sorted(tb.items()))}")
    issues = [(r.idx, i) for r in unique for i in r.issues]
    w(f"- validate_model 问题: {len(issues)} 条,涉及 {len({i for i, _ in issues})} 个模型(权重和>1 的条目也计入)")
    w("")

    failed = [r for r in records if r.status in ("failed", "skipped")]
    w("**D6. 解析失败 / 跳过**")
    w("")
    if failed:
        for r in failed:
            w(f"- #{r.idx} {esc(r.display)}: {r.status} — {esc(r.error)}")
    else:
        w("- 无")
    w("")

    if poses:
        w("**D7. `.pose` 文件**(load_pose 解析检查)")
        w("")
        for path, count, note in poses:
            w(f"- {esc(display_path(path, '', args.roots))}: {count} 条骨骼{(';' + note) if note else ''}")
        w("")

    w("**D8. 同目录已有 PMX 的 XPS 文件**(PMX 顶点 bbox 高度 ÷ XPS bbox 高度 = 既有转换所用的缩放系数)")
    w("")
    folders: Dict[str, Record] = {}
    for r in unique:
        if not r.pmx:
            continue
        folder = str(Path(r.path).parent)
        current = folders.get(folder)
        if current is None or (current.is_pose_variant and not r.is_pose_variant):
            folders[folder] = r  # one representative XPS per folder, preferring the non-pose file
    rows = []
    bone_only: Dict[int, List[str]] = {}
    for r in folders.values():
        for name, height, ratio, error in r.pmx:
            if height is None or ratio is None:
                bone_only.setdefault(r.idx, []).append(name if not error or "bone-only" in error
                                                       else f"{name} ({error})")
            else:
                rows.append((r, name, height, ratio))
    if rows:
        w("| # | XPS 文件(每目录取一个) | XPS bbox 高度 | 头骨 Y | PMX 文件 | PMX bbox 高度 | PMX/XPS |")
        w("|---|---|---|---|---|---|---|")
        for r, name, height, ratio in rows:
            w(f"| {r.idx} | {esc(r.display)} | {fnum(r.height)} | {fnum(r.head_y)} | {esc(name)} | "
              f"{fnum(height)} | {ratio:.2f} |")
        w("")
        ratios = [ratio for _, _, _, ratio in rows]
        hist = Counter(round(ratio, 1) for ratio in ratios)
        w(f"- PMX/XPS 比值(每个 PMX 文件计一次,共 {len(ratios)} 个): "
          + ", ".join(f"×{k:g}: {v}" for k, v in sorted(hist.items(), key=lambda kv: -kv[1])))
        w(f"- 比值统计: {stats_line(ratios, 2)}")
    if bone_only:
        w("- 仅骨骼(0 顶点)或无法读取、未计入比值的 PMX: " + "; ".join(
            f"#{idx}: {esc(', '.join(names))}" for idx, names in bone_only.items()))
    if not rows and not bone_only:
        w("- 无")
    w("")
    w(END_MARK)
    return "\n".join(out)


def write_report(path: Path, generated: str) -> None:
    """Create ``path`` or replace only its generated block.

    The whole file is rewritten in text mode, so it ends up with the platform
    line endings (CRLF on Windows, like the other research notes).
    """
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if BEGIN_MARK in text and END_MARK in text:
            head = text[:text.index(BEGIN_MARK)]
            tail = text[text.index(END_MARK) + len(END_MARK):]
            path.write_text(head + generated + tail, encoding="utf-8")
            return
        path.write_text(text.rstrip() + "\n\n" + generated + "\n", encoding="utf-8")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generated + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- main


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("roots", nargs="*", help=f"folders to scan (default: {' '.join(DEFAULT_ROOTS)})")
    parser.add_argument("--exclude", action="append", default=None, help="folder to skip (repeatable)")
    parser.add_argument("--extra", action="append", default=[], help="additional model file (repeatable)")
    parser.add_argument("--no-extras", action="store_true", help="do not add the built-in extra samples")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Markdown report to create/update")
    parser.add_argument("--stdout-only", action="store_true", help="do not write the Markdown report")
    parser.add_argument("--json", default=None, help="also dump per-file records as JSON")
    parser.add_argument("--no-dedupe", action="store_true", help="parse byte-identical files again")
    parser.add_argument("--no-pmx", action="store_true", help="skip measuring PMX files next to the models")
    args = parser.parse_args(argv)
    args.roots = args.roots or list(DEFAULT_ROOTS)
    args.exclude = args.exclude if args.exclude is not None else list(DEFAULT_EXCLUDES)
    args.command_line = "python " + " ".join(
        [Path(sys.argv[0]).as_posix() if sys.argv else "scripts/survey_xps_corpus.py"] +
        [f'"{a}"' if " " in a else a for a in (argv if argv is not None else sys.argv[1:])])
    logging.getLogger("xps_to_pmx").setLevel(logging.ERROR)

    started = time.perf_counter()
    found, pose_paths = discover(args.roots, args.exclude)
    extras = [] if args.no_extras else list(DEFAULT_EXTRAS)
    extras += args.extra
    known = {_norm(p) for p, _ in found}
    args.extras_used = []
    for extra in extras:
        if os.path.isfile(extra) and _norm(extra) not in known:
            found.append((extra, "extra"))
            known.add(_norm(extra))
            args.extras_used.append(extra)
        elif os.path.isfile(extra):
            args.extras_used.append(extra)
        else:
            print(f"[warn] extra sample not found: {extra}", file=sys.stderr)

    records: List[Record] = []
    by_hash: Dict[str, int] = {}
    rg_mesh_counts: Counter = Counter()
    for idx, (path, label) in enumerate(found, start=1):
        rec = Record(idx=idx, path=path, display=display_path(path, label, args.roots), size=os.path.getsize(path))
        rec.is_pose_variant = "pose" in Path(path).stem.lower()
        folder = Path(path).parent
        rec.pmx_siblings = sorted(p.name for p in folder.glob("*.pmx"))
        records.append(rec)
        data = Path(path).read_bytes()
        rec.sha1 = hashlib.sha1(data).hexdigest()
        if not args.no_dedupe and rec.sha1 in by_hash:
            rec.duplicate_of = by_hash[rec.sha1]
            rec.status = "duplicate"
            print(f"#{idx:3d} dup of #{rec.duplicate_of:<3d} {rec.display}")
            continue
        by_hash[rec.sha1] = idx
        t0 = time.perf_counter()
        try:
            model = parse_xps_data(data, path)
        except Exception as err:  # noqa: BLE001 - a survey reports failures instead of stopping
            rec.seconds = time.perf_counter() - t0
            rec.status = "skipped" if WEIRD_DUPLICATE_NAME.search(path) else "failed"
            rec.error = f"{type(err).__name__}: {err}"
            print(f"#{idx:3d} {rec.status.upper()} {rec.display}: {rec.error}")
            continue
        rec.seconds = time.perf_counter() - t0
        analyse(rec, model)
        if rec.duplicate_of is None:
            for mesh in model.meshes:
                rg_mesh_counts[mesh.render_group] += 1
        del model
        print(f"#{idx:3d} {rec.fmt:5s} {rec.version:9s} bones={rec.bones:5d} meshes={rec.meshes:3d} "
              f"verts={rec.vertices:7d} H={fnum(rec.height):>7s} minY={fnum(rec.ground):>7s} "
              f"{rec.convention:24s} {rec.seconds:5.2f}s {rec.display}"
              + (f"  [{warn_text(rec.warnings)}]" if rec.warnings else ""))
    args.rg_mesh_counts = rg_mesh_counts

    if not args.no_pmx:
        pmx_cache: Dict[str, Tuple[Optional[float], str]] = {}
        for rec in records:
            if rec.duplicate_of is not None or rec.status != "ok" or not rec.pmx_siblings:
                continue
            for name in rec.pmx_siblings:
                pmx_path = str(Path(rec.path).parent / name)
                if pmx_path not in pmx_cache:
                    try:
                        lo, hi, vertex_count = pmx_vertex_bbox(pmx_path)
                        pmx_cache[pmx_path] = ((hi[1] - lo[1], "") if vertex_count
                                               else (None, "0 vertices (bone-only PMX)"))
                    except Exception as err:  # noqa: BLE001
                        pmx_cache[pmx_path] = (None, f"{type(err).__name__}: {err}")
                height, error = pmx_cache[pmx_path]
                ratio = height / rec.height if (height and rec.height) else None
                rec.pmx.append((name, height, ratio, error))

    poses: List[Tuple[str, int, str]] = []
    for pose_path in pose_paths:
        try:
            entries = load_pose(pose_path)
            poses.append((pose_path, len(entries), ""))
        except Exception as err:  # noqa: BLE001 - report and continue
            poses.append((pose_path, 0, f"失败: {err}"))

    total = time.perf_counter() - started
    generated = build_markdown(records, poses, args, total)
    if not args.stdout_only:
        write_report(Path(args.out), generated)
        print(f"\nreport written: {args.out}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump([asdict(r) for r in records], fh, ensure_ascii=False, indent=1)
        print(f"json written: {args.json}")
    unique = [r for r in records if r.status in ("ok", "partial") and r.duplicate_of is None]
    chars = [r.height for r in unique if r.is_character and not r.is_pose_variant and r.status == "ok"]
    print(f"\nfiles={len(records)} unique_parsed={len(unique)} failed={sum(r.status == 'failed' for r in records)} "
          f"skipped={sum(r.status == 'skipped' for r in records)} total={total:.1f}s "
          f"parse={sum(r.seconds for r in records):.1f}s")
    if chars:
        print("character heights: " + stats_line(chars))
    print("conventions: " + ", ".join(f"{k}={v}" for k, v in Counter(r.convention for r in unique).most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
