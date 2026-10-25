"""Per-model mapping files (design doc §5.2): one row per source bone, exportable and re-importable.

Format (UTF-8 with BOM so Excel opens it correctly)::

    # xps_to_pmx mapping schema=1 source=<xps path> convention=xna_lara
    source_bone,action,slot_id,name_j,origin,confidence,note
    arm left shoulder 2,map,left_upper_arm_bone,左腕,csv,1.00,

The owner's older two-column lists (``源骨,日文名``) are accepted too: the
first row naming an MMD bone maps it, later rows with the same MMD name are
merged into it, rows naming an unknown MMD bone are reported.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from .spec import BoneSpec, norm_name

SCHEMA_PREFIX = "# xps_to_pmx mapping schema="
SCHEMA_VERSION = 1
COLUMNS = ("source_bone", "action", "slot_id", "name_j", "origin", "confidence", "note")
ACTIONS = ("map", "merge", "keep", "delete")


@dataclass
class MappingRow:
    source_bone: str
    action: str
    slot_id: str = ""
    name_j: str = ""
    origin: str = ""
    confidence: float = 1.0
    note: str = ""


@dataclass
class MappingFile:
    rows: List[MappingRow] = field(default_factory=list)
    source: str = ""
    convention: str = ""
    problems: List[str] = field(default_factory=list)

    def slot_assignments(self) -> Dict[str, str]:
        return {r.slot_id: r.source_bone for r in self.rows if r.action == "map" and r.slot_id}


def write_mapping(rows: Sequence[MappingRow], source: str = "", convention: str = "") -> str:
    buf = io.StringIO()
    buf.write(f"{SCHEMA_PREFIX}{SCHEMA_VERSION} source={source} convention={convention}\n")
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(COLUMNS)
    for r in rows:
        writer.writerow([r.source_bone, r.action, r.slot_id, r.name_j, r.origin, f"{r.confidence:.2f}", r.note])
    return "﻿" + buf.getvalue()


def _header_meta(line: str) -> Dict[str, str]:
    meta = {}
    for part in line[len(SCHEMA_PREFIX):].split():
        key, _, value = part.partition("=")
        if value:
            meta[key] = value
    return meta


def parse_mapping(text: str, spec: BoneSpec) -> MappingFile:
    """Parse either format; never raises for content problems (they go to ``problems``)."""
    text = text.lstrip("﻿")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    out = MappingFile()
    if not lines:
        out.problems.append("文件是空的")
        return out
    if lines[0].startswith(SCHEMA_PREFIX):
        meta = _header_meta(lines[0])
        try:
            version = int(lines[0][len(SCHEMA_PREFIX):].split()[0])
        except (ValueError, IndexError):
            version = -1
        if version != SCHEMA_VERSION:
            out.problems.append(f"不支持的映射文件版本 {version}")
            return out
        out.source = meta.get("source", "")
        out.convention = meta.get("convention", "")
        _parse_full(lines[1:], spec, out)
    else:
        _parse_two_column(lines, spec, out)
    return out


def _parse_full(lines: List[str], spec: BoneSpec, out: MappingFile) -> None:
    reader = csv.reader(io.StringIO("\n".join(lines)))
    header = next(reader, None)
    if header is None or tuple(h.strip() for h in header) != COLUMNS:
        out.problems.append(f"表头必须是 {','.join(COLUMNS)}")
        return
    seen_slots: Dict[str, str] = {}
    for n, row in enumerate(reader, start=3):
        if len(row) != len(COLUMNS):
            out.problems.append(f"第 {n} 行列数不对")
            continue
        src, action, slot_id, name_j, origin, conf, note = (c.strip() for c in row)
        if action not in ACTIONS:
            out.problems.append(f"第 {n} 行：未知处置 {action!r}")
            continue
        if action in ("map", "merge"):
            if slot_id not in spec.by_id:
                out.problems.append(f"第 {n} 行：未知槽位 {slot_id!r}")
                continue
            if action == "map":
                if slot_id in seen_slots:
                    out.problems.append(f"第 {n} 行：槽位 {slot_id} 已由 {seen_slots[slot_id]} 占用")
                    continue
                seen_slots[slot_id] = src
        try:
            confidence = float(conf) if conf else 1.0
        except ValueError:
            confidence = 1.0
        out.rows.append(MappingRow(src, action, slot_id, name_j or (spec[slot_id].name_j if slot_id else ""),
                                   origin or "user", confidence, note))


def _parse_two_column(lines: List[str], spec: BoneSpec, out: MappingFile) -> None:
    by_norm = {norm_name(s.name_j): s for s in spec}
    # also accept the MMD column aliases (e.g. 左乳奶 for 左胸)
    for s in spec:
        for alias in s.aliases.get("mmd", ()):
            by_norm.setdefault(alias.norm, s)
    taken: Dict[str, str] = {}
    for n, line in enumerate(lines, start=1):
        if line.lstrip().startswith("#"):
            continue
        parts = next(csv.reader([line]))
        if len(parts) < 2 or not parts[0].strip():
            continue
        src, mmd = parts[0].strip(), parts[1].strip()
        slot = by_norm.get(norm_name(mmd))
        if slot is None:
            out.problems.append(f"第 {n} 行：{mmd} 不是规格表里的 MMD 骨名（{src} 未导入）")
            continue
        if slot.slot_id in taken:
            out.rows.append(MappingRow(src, "merge", slot.slot_id, slot.name_j, "user", 1.0,
                                       f"并入 {taken[slot.slot_id]}"))
        else:
            taken[slot.slot_id] = src
            out.rows.append(MappingRow(src, "map", slot.slot_id, slot.name_j, "user", 1.0, ""))
