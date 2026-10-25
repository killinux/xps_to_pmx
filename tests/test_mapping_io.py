"""Per-model mapping CSV: round trip, validation and the owner's two-column lists."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xps_to_pmx.core.mapping_io import MappingRow, parse_mapping, write_mapping  # noqa: E402
from xps_to_pmx.core.spec import load_bone_spec  # noqa: E402

SPEC = load_bone_spec()
OWNER_LIST = r"E:/mywork/xps2mmd/Purifier_bones.txt"


def test_round_trip():
    rows = [MappingRow("arm left shoulder 2", "map", "left_upper_arm_bone", "左腕", "csv", 1.0, ""),
            MappingRow("unused bip001 xtra07", "merge", "left_upper_arm_bone", "左腕", "classifier", 0.9, "辅助骨"),
            MappingRow("hair 1", "keep", "", "", "classifier", 0.8, "头发链,逗号也行")]
    text = write_mapping(rows, source="E:/x/xps.xps", convention="xna_lara")
    assert text.startswith("\ufeff# xps_to_pmx mapping schema=1")
    parsed = parse_mapping(text, SPEC)
    assert not parsed.problems
    assert parsed.convention == "xna_lara" and parsed.source == "E:/x/xps.xps"
    assert [(r.source_bone, r.action, r.slot_id, r.note) for r in parsed.rows] == \
        [(r.source_bone, r.action, r.slot_id, r.note) for r in rows]
    assert parsed.slot_assignments() == {"left_upper_arm_bone": "arm left shoulder 2"}


def test_problems_are_reported_not_raised():
    text = "\n".join(["# xps_to_pmx mapping schema=1", ",".join(
        ("source_bone", "action", "slot_id", "name_j", "origin", "confidence", "note")),
        "a,map,left_upper_arm_bone,左腕,user,1,", "b,map,left_upper_arm_bone,左腕,user,1,",
        "c,fly,,,user,1,", "d,map,no_such_slot,,user,1,"])
    parsed = parse_mapping(text, SPEC)
    assert len(parsed.rows) == 1 and len(parsed.problems) == 3


def test_wrong_version():
    parsed = parse_mapping("# xps_to_pmx mapping schema=9\nsource_bone,action", SPEC)
    assert parsed.problems and not parsed.rows


def test_two_column_owner_format():
    text = "root,全ての親\n\nlThighBend,左足\nlThighTwist,左足\nabdomenLower,上半身\nfoo,存在しない骨\n左乳,左乳奶\n"
    parsed = parse_mapping(text, SPEC)
    actions = [(r.source_bone, r.action, r.slot_id) for r in parsed.rows]
    assert ("lThighBend", "map", "left_thigh_bone") in actions
    assert ("lThighTwist", "merge", "left_thigh_bone") in actions
    assert ("左乳", "map", "left_breast_bone") in actions  # MMD alias column accepted
    assert len(parsed.problems) == 1


def test_owner_list_on_disk():
    if not os.path.isfile(OWNER_LIST):
        return
    with open(OWNER_LIST, encoding="utf-8-sig") as f:
        parsed = parse_mapping(f.read(), SPEC)
    assert any(r.slot_id == "left_upper_arm_bone" and r.action == "map" for r in parsed.rows)
