"""Load and validate ``bone_slots.csv`` -- the single source of truth for the
target MMD skeleton and for source-bone aliases (design doc §5.1).

The loader is strict (hard constraint 5): wrong schema version, unknown or
missing columns, duplicate slots, dangling references, unpaired sides and
malformed MMD names all raise :class:`SpecError` listing every problem found.
Alias columns are every column after ``recipe_args``; each one is a skeleton
naming convention (``xna_lara``, ``daz_g8`` …).  Alias cells hold candidates
separated by ``|``; a ``+`` prefix marks a bone whose weights are merged into
the slot instead of being its primary bone.
"""
from __future__ import annotations

import csv
import io
import os
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SCHEMA_PREFIX = "# xps_to_pmx bone_slots schema="
SCHEMA_VERSION = 1

SPEC_COLUMNS: Tuple[str, ...] = (
    "slot_id", "name_j", "name_e", "group", "order", "row_type", "side", "mirror", "tier", "required",
    "parent", "deform", "visible", "controllable", "movable", "grant_parent", "grant_rate",
    "transform_order", "display_frame", "ik_target", "ik_links", "ik_loop", "ik_unit_deg", "recipe",
    "recipe_args",
)
ROW_TYPES = ("single", "symmetric", "finger", "hidden")
SIDES = ("C", "L", "R")
GROUPS = ("control", "trunk", "eye", "arm", "finger", "leg", "ik", "dbone", "other")
MAX_NAME_BYTES = 15
DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "data", "bone_slots.csv")

_SEP_RE = re.compile(r"[\s_\-.:]+")
_HALF_DIGIT_FINGER_RE = re.compile(r"(親指|人指|中指|薬指|小指)[0-9]")


class SpecError(ValueError):
    """Raised with every problem found in a spec file."""

    def __init__(self, problems: Sequence[str], source: str = ""):
        self.problems = list(problems)
        self.source = source
        head = f"{source}: " if source else ""
        super().__init__(head + f"{len(self.problems)} problem(s):\n  " + "\n  ".join(self.problems))


def norm_name(name: str) -> str:
    """Comparison key for bone names: NFKC (full-width → ASCII), case-folded, separators unified."""
    text = unicodedata.normalize("NFKC", name).casefold()
    return _SEP_RE.sub("_", text).strip("_")


def mmd_name_problems(name: str) -> List[str]:
    """Problems of an MMD (Japanese) bone name: spacing, digit width, IK width, cp932, 15 bytes."""
    problems = []
    if name != name.strip() or " " in name or "　" in name:
        problems.append("contains spaces")
    if _HALF_DIGIT_FINGER_RE.search(name):
        problems.append("finger numbers must be full-width (０１２３)")
    if "ＩＫ親" in name:
        problems.append("use half-width 'IK親'")
    if "IK" in name and not name.endswith("IK親"):
        problems.append("use full-width 'ＩＫ'")
    try:
        encoded = name.encode("cp932")
    except UnicodeEncodeError:
        problems.append("not encodable in cp932 (MMD shows '?' and VMD cannot reference it)")
    else:
        if len(encoded) > MAX_NAME_BYTES:
            problems.append(f"{len(encoded)} bytes in cp932 (> {MAX_NAME_BYTES}, VMD truncates)")
    return problems


@dataclass(frozen=True)
class Alias:
    name: str
    norm: str
    merge: bool


@dataclass(frozen=True)
class IkLink:
    slot_id: str
    limit_min_deg: Optional[float] = None
    limit_max_deg: Optional[float] = None

    @property
    def limited(self) -> bool:
        return self.limit_min_deg is not None


@dataclass(frozen=True)
class SlotSpec:
    slot_id: str
    name_j: str
    name_e: str
    group: str
    order: int
    row_type: str
    side: str
    mirror: str
    tier: int
    required: bool
    parents: Tuple[str, ...]
    deform: bool
    visible: bool
    controllable: bool
    movable: bool
    grant_parent: str
    grant_rate: Optional[float]
    transform_order: int
    display_frame: str
    ik_target: str
    ik_links: Tuple[IkLink, ...]
    ik_loop: Optional[int]
    ik_unit_deg: Optional[float]
    recipe: str
    recipe_args: Dict[str, str]
    aliases: Dict[str, Tuple[Alias, ...]] = field(default_factory=dict)

    @property
    def is_source_slot(self) -> bool:
        """Slots that can be filled from a source bone (tier 0, or generated only when missing)."""
        return self.tier in (0, 1, 2) and any(a for a in self.aliases.values()) or self.tier == 0

    @property
    def is_ik(self) -> bool:
        return bool(self.ik_target)

    def primary_aliases(self, convention: str) -> Tuple[Alias, ...]:
        return tuple(a for a in self.aliases.get(convention, ()) if not a.merge)

    def merge_aliases(self, convention: str) -> Tuple[Alias, ...]:
        return tuple(a for a in self.aliases.get(convention, ()) if a.merge)

    def arg(self, key: str, default: Optional[float] = None) -> Optional[float]:
        value = self.recipe_args.get(key)
        return default if value is None else float(value)


class BoneSpec:
    """Validated, ordered collection of :class:`SlotSpec`."""

    def __init__(self, slots: Sequence[SlotSpec], conventions: Sequence[str], source: str = ""):
        self.slots: List[SlotSpec] = list(slots)
        self.conventions: List[str] = list(conventions)
        self.source = source
        self.by_id: Dict[str, SlotSpec] = {s.slot_id: s for s in self.slots}
        self.by_name_j: Dict[str, SlotSpec] = {s.name_j: s for s in self.slots}

    def __iter__(self):
        return iter(self.slots)

    def __len__(self) -> int:
        return len(self.slots)

    def __getitem__(self, slot_id: str) -> SlotSpec:
        return self.by_id[slot_id]

    def get(self, slot_id: str) -> Optional[SlotSpec]:
        return self.by_id.get(slot_id)

    def alias_index(self, convention: str) -> Dict[str, List[Tuple[str, bool]]]:
        """``norm(alias) -> [(slot_id, is_merge), ...]`` for one convention column."""
        index: Dict[str, List[Tuple[str, bool]]] = {}
        for slot in self.slots:
            for alias in slot.aliases.get(convention, ()):
                index.setdefault(alias.norm, []).append((slot.slot_id, alias.merge))
        return index

    def first_existing_parent(self, slot_id: str, exists) -> Optional[str]:
        """First slot in ``parents`` for which ``exists(slot_id)`` is true (parent fallbacks)."""
        for parent in self.by_id[slot_id].parents:
            if exists(parent):
                return parent
        return None

    def ordered(self) -> List[SlotSpec]:
        return sorted(self.slots, key=lambda s: (s.order, s.slot_id))


# ---------------------------------------------------------------------------
# parsing

def _bool(value: str, column: str, row: int, problems: List[str]) -> bool:
    if value in ("Y", "N"):
        return value == "Y"
    problems.append(f"row {row}: column {column} must be Y or N, got {value!r}")
    return False


def _int(value: str, column: str, row: int, problems: List[str], allow_empty=False) -> Optional[int]:
    if value == "" and allow_empty:
        return None
    try:
        return int(value)
    except ValueError:
        problems.append(f"row {row}: column {column} must be an integer, got {value!r}")
        return None


def _float(value: str, column: str, row: int, problems: List[str]) -> Optional[float]:
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        problems.append(f"row {row}: column {column} must be a number, got {value!r}")
        return None


def _parse_args(value: str, row: int, problems: List[str]) -> Dict[str, str]:
    args: Dict[str, str] = {}
    for part in filter(None, (p.strip() for p in value.split(";"))):
        key, sep, val = part.partition("=")
        if not sep or not key.strip():
            problems.append(f"row {row}: recipe_args item {part!r} is not key=value")
            continue
        args[key.strip()] = val.strip()
    return args


_IK_LINK_RE = re.compile(r"^([A-Za-z0-9_]+)(?:\[(-?[0-9.]+):(-?[0-9.]+)\])?$")


def _parse_ik_links(value: str, row: int, problems: List[str]) -> Tuple[IkLink, ...]:
    links = []
    for part in filter(None, (p.strip() for p in value.split("|"))):
        m = _IK_LINK_RE.match(part)
        if not m:
            problems.append(f"row {row}: ik_links item {part!r} is not slot_id or slot_id[min:max]")
            continue
        lo = float(m.group(2)) if m.group(2) is not None else None
        hi = float(m.group(3)) if m.group(3) is not None else None
        links.append(IkLink(m.group(1), lo, hi))
    return tuple(links)


def _parse_aliases(value: str) -> Tuple[Alias, ...]:
    out = []
    for part in filter(None, (p.strip() for p in value.split("|"))):
        merge = part.startswith("+")
        name = part[1:].strip() if merge else part
        if name:
            out.append(Alias(name, norm_name(name), merge))
    return tuple(out)


def parse_bone_spec(text: str, source: str = "") -> BoneSpec:
    problems: List[str] = []
    lines = text.lstrip("﻿").splitlines()
    if not lines or not lines[0].startswith(SCHEMA_PREFIX):
        raise SpecError([f"first line must be '{SCHEMA_PREFIX}{SCHEMA_VERSION}'"], source)
    try:
        version = int(lines[0][len(SCHEMA_PREFIX):].strip())
    except ValueError:
        raise SpecError(["schema version is not an integer"], source)
    if version != SCHEMA_VERSION:
        raise SpecError([f"schema version {version} is not supported (expected {SCHEMA_VERSION})"], source)

    body = [ln for ln in lines[1:] if ln.strip() and not ln.lstrip().startswith("#")]
    reader = csv.reader(io.StringIO("\n".join(body)))
    try:
        header = [h.strip() for h in next(reader)]
    except StopIteration:
        raise SpecError(["no header row"], source)
    spec_part = header[:len(SPEC_COLUMNS)]
    if tuple(spec_part) != SPEC_COLUMNS:
        missing = [c for c in SPEC_COLUMNS if c not in header]
        unknown = [c for c in spec_part if c not in SPEC_COLUMNS]
        raise SpecError([f"spec columns must be exactly {', '.join(SPEC_COLUMNS)} in this order"]
                        + [f"missing column {c}" for c in missing] + [f"unknown column {c}" for c in unknown],
                        source)
    conventions = header[len(SPEC_COLUMNS):]
    if not conventions:
        problems.append("no alias (convention) columns after recipe_args")
    if len(set(conventions)) != len(conventions):
        problems.append("duplicate convention columns")
    for conv in conventions:
        if not re.match(r"^[a-z][a-z0-9_]*$", conv):
            problems.append(f"convention column {conv!r} must be lower_snake_case")

    slots: List[SlotSpec] = []
    for row_no, row in enumerate(reader, start=3):
        if len(row) != len(header):
            problems.append(f"row {row_no}: {len(row)} cells, header has {len(header)}")
            continue
        cells = dict(zip(header, (c.strip() for c in row)))
        slot = SlotSpec(
            slot_id=cells["slot_id"], name_j=cells["name_j"], name_e=cells["name_e"], group=cells["group"],
            order=_int(cells["order"], "order", row_no, problems) or 0,
            row_type=cells["row_type"], side=cells["side"], mirror=cells["mirror"],
            tier=_int(cells["tier"], "tier", row_no, problems) or 0,
            required=_bool(cells["required"], "required", row_no, problems),
            parents=tuple(p for p in cells["parent"].split("|") if p),
            deform=_bool(cells["deform"], "deform", row_no, problems),
            visible=_bool(cells["visible"], "visible", row_no, problems),
            controllable=_bool(cells["controllable"], "controllable", row_no, problems),
            movable=_bool(cells["movable"], "movable", row_no, problems),
            grant_parent=cells["grant_parent"],
            grant_rate=_float(cells["grant_rate"], "grant_rate", row_no, problems),
            transform_order=_int(cells["transform_order"] or "0", "transform_order", row_no, problems) or 0,
            display_frame=cells["display_frame"], ik_target=cells["ik_target"],
            ik_links=_parse_ik_links(cells["ik_links"], row_no, problems),
            ik_loop=_int(cells["ik_loop"], "ik_loop", row_no, problems, allow_empty=True),
            ik_unit_deg=_float(cells["ik_unit_deg"], "ik_unit_deg", row_no, problems),
            recipe=cells["recipe"], recipe_args=_parse_args(cells["recipe_args"], row_no, problems),
            aliases={conv: _parse_aliases(cells[conv]) for conv in conventions},
        )
        slots.append(slot)
    problems.extend(validate_slots(slots, conventions))
    if problems:
        raise SpecError(problems, source)
    return BoneSpec(slots, conventions, source)


def validate_slots(slots: Sequence[SlotSpec], conventions: Sequence[str]) -> List[str]:
    """Cross-row consistency rules; returns problems (empty when valid)."""
    problems: List[str] = []
    by_id: Dict[str, SlotSpec] = {}
    names: Dict[str, str] = {}
    orders: Dict[int, str] = {}
    for s in slots:
        if not re.match(r"^[a-z][a-z0-9_]*$", s.slot_id):
            problems.append(f"{s.slot_id!r}: slot_id must be lower_snake_case ASCII")
        if s.slot_id in by_id:
            problems.append(f"{s.slot_id}: duplicate slot_id")
        by_id[s.slot_id] = s
        if s.name_j in names:
            problems.append(f"{s.slot_id}: name_j {s.name_j} already used by {names[s.name_j]}")
        names[s.name_j] = s.slot_id
        if s.order in orders:
            problems.append(f"{s.slot_id}: order {s.order} already used by {orders[s.order]}")
        orders[s.order] = s.slot_id
        for p in mmd_name_problems(s.name_j):
            problems.append(f"{s.slot_id}: name_j {s.name_j}: {p}")
        if not s.name_e:
            problems.append(f"{s.slot_id}: name_e is empty")
        if s.row_type not in ROW_TYPES:
            problems.append(f"{s.slot_id}: row_type {s.row_type!r} not in {ROW_TYPES}")
        if s.side not in SIDES:
            problems.append(f"{s.slot_id}: side {s.side!r} not in {SIDES}")
        if s.group not in GROUPS:
            problems.append(f"{s.slot_id}: group {s.group!r} not in {GROUPS}")
        if s.tier not in (0, 1, 2, 3):
            problems.append(f"{s.slot_id}: tier must be 0-3")
        if s.tier in (1, 2, 3) and not s.recipe and not s.required:
            problems.append(f"{s.slot_id}: generated tier {s.tier} needs a recipe")
        if s.grant_parent and s.grant_rate is None:
            problems.append(f"{s.slot_id}: grant_parent without grant_rate")
        if s.ik_target and (s.ik_loop is None or s.ik_unit_deg is None or not s.ik_links):
            problems.append(f"{s.slot_id}: IK bone needs ik_links, ik_loop and ik_unit_deg")
    for s in slots:
        for p in s.parents:
            if p not in by_id:
                problems.append(f"{s.slot_id}: parent {p} does not exist")
            elif p == s.slot_id:
                problems.append(f"{s.slot_id}: is its own parent")
        if s.grant_parent and s.grant_parent not in by_id:
            problems.append(f"{s.slot_id}: grant_parent {s.grant_parent} does not exist")
        if s.ik_target and s.ik_target not in by_id:
            problems.append(f"{s.slot_id}: ik_target {s.ik_target} does not exist")
        for link in s.ik_links:
            if link.slot_id not in by_id:
                problems.append(f"{s.slot_id}: ik link {link.slot_id} does not exist")
        if s.side == "C":
            if s.mirror:
                problems.append(f"{s.slot_id}: centre slot must not have a mirror")
        else:
            m = by_id.get(s.mirror)
            if m is None:
                problems.append(f"{s.slot_id}: mirror {s.mirror!r} does not exist")
            elif m.mirror != s.slot_id or m.side == s.side or m.side == "C":
                problems.append(f"{s.slot_id}: mirror {s.mirror} is not its opposite-side partner")
    for conv in conventions:
        seen: Dict[str, str] = {}
        for s in slots:
            for a in s.aliases.get(conv, ()):
                if a.norm in seen and seen[a.norm] != s.slot_id:
                    problems.append(f"{conv}: alias {a.name!r} used by {seen[a.norm]} and {s.slot_id}")
                seen.setdefault(a.norm, s.slot_id)
    problems.extend(_parent_cycles(slots))
    return problems


def _parent_cycles(slots: Sequence[SlotSpec]) -> List[str]:
    """Following the first parent of every slot must reach a root."""
    first = {s.slot_id: (s.parents[0] if s.parents else "") for s in slots}
    problems = []
    for start in first:
        seen = set()
        cur = start
        while cur:
            if cur in seen:
                problems.append(f"{start}: parent chain has a cycle through {cur}")
                break
            seen.add(cur)
            cur = first.get(cur, "")
    return problems


def merge_specs(base: BoneSpec, override: BoneSpec) -> BoneSpec:
    """User override: rows replace base rows by ``slot_id``; new rows are appended; columns are unioned."""
    conventions = list(base.conventions) + [c for c in override.conventions if c not in base.conventions]
    slots = {s.slot_id: s for s in base.slots}
    for s in override.slots:
        slots[s.slot_id] = s
    merged = list(slots.values())
    problems = validate_slots(merged, conventions)
    if problems:
        raise SpecError(problems, f"{base.source} + {override.source}")
    return BoneSpec(merged, conventions, f"{base.source} + {override.source}")


def load_bone_spec(path: str = DEFAULT_PATH, override_paths: Iterable[str] = ()) -> BoneSpec:
    with open(path, encoding="utf-8-sig") as f:
        spec = parse_bone_spec(f.read(), source=path)
    for extra in override_paths:
        if extra and os.path.isfile(extra):
            with open(extra, encoding="utf-8-sig") as f:
                spec = merge_specs(spec, parse_bone_spec(f.read(), source=extra))
    return spec
