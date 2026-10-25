"""bone_slots.csv loader: the shipped table is valid and every rule has a counter-example."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xps_to_pmx.core.spec import (SpecError, load_bone_spec, mmd_name_problems, norm_name,  # noqa: E402
                                  parse_bone_spec)
from xps_to_pmx.core.spec.bone_slots import SPEC_COLUMNS  # noqa: E402

HEADER = ",".join(SPEC_COLUMNS) + ",xna_lara,mmd"
ROOT = "all_parents_bone,全ての親,master,control,20,single,C,,1,N,,N,Y,Y,Y,,,0,Root,,,,,origin,,root ground,全ての親"
ARM_L = ("left_upper_arm_bone,左腕,arm_L,arm,230,symmetric,L,right_upper_arm_bone,0,Y,all_parents_bone,"
         "Y,Y,Y,N,,,0,腕,,,,,,,arm left shoulder 2,左腕")
ARM_R = ("right_upper_arm_bone,右腕,arm_R,arm,430,symmetric,R,left_upper_arm_bone,0,Y,all_parents_bone,"
         "Y,Y,Y,N,,,0,腕,,,,,,,arm right shoulder 2,右腕")


def _csv(*rows, header=HEADER, schema="# xps_to_pmx bone_slots schema=1"):
    return "\n".join([schema, header, *rows])


def _problems(text):
    with pytest.raises(SpecError) as info:
        parse_bone_spec(text)
    return " | ".join(info.value.problems)


def test_shipped_table_is_valid():
    spec = load_bone_spec()
    assert len(spec) >= 100
    assert spec["left_leg_ik_bone"].ik_links[0].limit_max_deg == -0.5
    assert spec["left_arm_twist1_bone"].grant_parent == "left_arm_twist_bone"
    assert spec["upper_body_bone"].primary_aliases("xna_lara")[0].name == "spine lower"
    merge = spec["left_lower_arm_bone"].merge_aliases("daz_g8")
    assert [a.name for a in merge] == ["lForearmTwist"]


def test_minimal_valid_table():
    spec = parse_bone_spec(_csv(ROOT, ARM_L, ARM_R))
    assert [s.slot_id for s in spec.ordered()] == ["all_parents_bone", "left_upper_arm_bone",
                                                     "right_upper_arm_bone"]
    assert spec.alias_index("xna_lara")[norm_name("arm left shoulder 2")] == [("left_upper_arm_bone", False)]


def test_schema_line_required():
    with pytest.raises(SpecError):
        parse_bone_spec(_csv(ROOT, schema="slot_id"))
    with pytest.raises(SpecError):
        parse_bone_spec(_csv(ROOT, schema="# xps_to_pmx bone_slots schema=2"))


def test_unknown_and_missing_columns():
    bad_header = HEADER.replace("deform", "deformed")
    assert "missing column deform" in _problems(_csv(ROOT, header=bad_header))


def test_wrong_cell_count():
    assert "cells" in _problems(_csv(ROOT + ",extra"))


def test_duplicate_slot_and_name():
    dup = ROOT.replace("20,", "21,", 1)
    text = _problems(_csv(ROOT, dup))
    assert "duplicate slot_id" in text and "already used" in text


def test_bad_flags_and_numbers():
    assert "must be Y or N" in _problems(_csv(ROOT.replace(",N,Y,Y,Y,", ",x,Y,Y,Y,", 1)))
    assert "must be an integer" in _problems(_csv(ROOT.replace("control,20,", "control,twenty,")))


def test_dangling_parent_and_grant():
    arm = ARM_L.replace("all_parents_bone,Y", "nowhere_bone,Y")
    assert "parent nowhere_bone does not exist" in _problems(_csv(ROOT, arm, ARM_R))
    granted = ARM_L.replace("Y,Y,Y,N,,,0", "Y,Y,Y,N,ghost_bone,1.0,0")
    assert "grant_parent ghost_bone does not exist" in _problems(_csv(ROOT, granted, ARM_R))


def test_mirror_must_pair():
    assert "mirror" in _problems(_csv(ROOT, ARM_L))


def test_alias_conflict_within_convention():
    clash = ARM_R.replace("arm right shoulder 2", "Arm_Left_Shoulder_2")
    assert "used by left_upper_arm_bone and right_upper_arm_bone" in _problems(_csv(ROOT, ARM_L, clash))


def test_ik_needs_links_loop_and_unit():
    ik = ("left_leg_ik_bone,左足ＩＫ,leg IK_L,ik,810,hidden,L,right_leg_ik_bone,1,N,all_parents_bone,"
          "N,Y,Y,Y,,,0,ＩＫ,left_upper_arm_bone,,,,leg_ik,,,左足ＩＫ")
    ik_r = ik.replace("left_leg_ik_bone,左足ＩＫ,leg IK_L", "right_leg_ik_bone,右足ＩＫ,leg IK_R") \
        .replace(",L,right_leg_ik_bone", ",R,left_leg_ik_bone").replace("810", "840").replace("左足ＩＫ", "右足ＩＫ")
    assert "IK bone needs" in _problems(_csv(ROOT, ARM_L, ARM_R, ik, ik_r))


def test_parent_cycle_detected():
    a = ROOT.replace("Y,,,N,Y,Y,Y", "Y,,,N,Y,Y,Y").replace("1,N,,N", "1,N,left_upper_arm_bone,N")
    assert "cycle" in _problems(_csv(a, ARM_L, ARM_R))


@pytest.mark.parametrize("name,fragment", [
    ("左親指0", "full-width"),
    ("左足IK", "full-width 'ＩＫ'"),
    ("左足ＩＫ親", "half-width"),
    ("上半身 2", "spaces"),
    ("左乳奶", "cp932"),
    ("とても長いボーンの名前です", "bytes"),
])
def test_mmd_name_rules(name, fragment):
    assert any(fragment in p for p in mmd_name_problems(name))


def test_valid_mmd_names_pass():
    for name in ("左親指０", "左足ＩＫ", "左足IK親", "上半身2", "腰キャンセル左", "右つま先ＩＫ"):
        assert mmd_name_problems(name) == [], name


def test_norm_name_unifies_width_case_and_separators():
    assert norm_name("Bip001-Pelvis") == norm_name("bip001 pelvis") == norm_name("BIP001_PELVIS")
    assert norm_name("左親指０") == norm_name("左親指0")
    assert norm_name("thigh_twist.l") == "thigh_twist_l"
