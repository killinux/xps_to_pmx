"""Identification engine: synthetic rigs (alias / topology / 下半身 cases) and the regression models."""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import synthetic  # noqa: E402
from xps_to_pmx.core.checks.mapping import ERROR, check_mapping  # noqa: E402
from xps_to_pmx.core.rig.identify import identify  # noqa: E402
from xps_to_pmx.core.spec import load_bone_spec  # noqa: E402

SPEC = load_bone_spec()
REQUIRED = [s.slot_id for s in SPEC if s.required]


def _names(rig, ident, slots):
    return {s: (rig.bones[ident.bone_of(s)].name if ident.bone_of(s) >= 0 else None) for s in slots}


def test_alias_mapping_on_synthetic_rig():
    rig = synthetic.build()
    ident = identify(rig, SPEC)
    assert ident.convention == "xna_lara"
    assert all(ident.slots[s].mapped for s in REQUIRED)
    names = _names(rig, ident, ["upper_body_bone", "upper_body2_bone", "upper_body3_bone", "neck_bone",
                                "head_bone", "left_thumb_0", "left_pinky_3", "right_toe_bone"])
    assert names == {"upper_body_bone": "spine lower", "upper_body2_bone": "spine middle",
                     "upper_body3_bone": "spine upper", "neck_bone": "head neck lower",
                     "head_bone": "head neck upper", "left_thumb_0": "arm left finger 1a",
                     "left_pinky_3": "arm left finger 5c", "right_toe_bone": "leg right toes"}
    assert ident.slots["upper_body2_bone"].origin == "spine"


def test_topology_alone_finds_the_same_bones():
    named = synthetic.build()
    named_ident = identify(named, SPEC)
    anon = synthetic.build(rename={b.name: f"bone_{b.index:03d}" for b in named.bones})
    anon_ident = identify(anon, SPEC)
    assert anon_ident.convention == ""
    for slot in REQUIRED + ["left_thumb_0", "left_index_1", "left_pinky_3", "left_toe_bone", "neck_bone"]:
        assert anon_ident.bone_of(slot) == named_ident.bone_of(slot), slot
        assert anon_ident.slots[slot].origin in ("topology", "spine", "diagnosis")


@pytest.mark.parametrize("case", ["A", "C", "D"])
def test_lower_body_cases(case):
    rig = synthetic.build(lower_case=case)
    ident = identify(rig, SPEC)
    diag = ident.lower_body
    assert diag.case == case
    pelvis = rig.by_name["pelvis"]
    if case == "A":
        assert ident.bone_of("lower_body_bone") == pelvis
    elif case == "C":
        assert diag.split_bone == pelvis and diag.needs_split
    else:
        assert diag.split_bone == rig.by_name["spine lower"]


def test_user_fixed_slot_is_never_overridden():
    rig = synthetic.build()
    wrong = rig.by_name["arm left finger 2a"]
    ident = identify(rig, SPEC, fixed={"left_hand_bone": wrong})
    assert ident.bone_of("left_hand_bone") == wrong
    assert ident.slots["left_hand_bone"].origin == "user"


def test_unweighted_leftovers_are_deleted_and_helpers_merged():
    extra = [("unused ARM LEFT IK.L", "root ground", (0.6, 0, 1.4)),          # control rig leftover
             ("unused bip001 xtra07", "arm left shoulder 2", (0.20, 0, 1.41))]  # helper on the upper arm
    rig = synthetic.build(extra=extra)
    # give the helper weights so it must be merged, not deleted
    import numpy as np
    helper = rig.by_name["unused bip001 xtra07"]
    rig.skin.bones[:5, 0] = helper
    rig._accumulate_weights()
    ident = identify(rig, SPEC)
    ik = ident.bones[rig.by_name["unused ARM LEFT IK.L"]]
    assert ik.action == "delete"
    disp = ident.bones[helper]
    assert disp.action == "merge" and disp.slot_id == "left_upper_arm_bone"
    assert np.isfinite(rig.height)


# --------------------------------------------------------------------------- real models

REAL = {
    "E:/day_work/2025money/wish/inase (arbiter)/xps.xps": dict(
        convention="xna_lara", lower="B",
        slots={"lower_body_bone": "unused trash 17", "upper_body2_bone": "spine middle",
               "left_lower_arm_bone": "arm left elbow", "left_toe_bone": "leg left toes"},
        merges={"left_lower_arm_bone": {"unused bip001 l foretwist1", "unused trash 18"}}),
    "E:/mywork/add_on/Purifier (Inase)/xps.xps": dict(
        convention="daz_g8", lower="A",
        slots={"lower_body_bone": "pelvis", "upper_body1_bone": "abdomenUpper", "upper_body2_bone": "chestLower",
               "upper_body3_bone": "chestUpper", "neck1_bone": "neckUpper", "left_ankle_bone": "lFoot",
               "left_toe_bone": "lToe", "left_middle_1": "lMid1"},
        merges={"left_upper_arm_bone": {"lShldrTwist"}, "left_hand_bone": {"lCarpal1", "lCarpal2"}}),
    "E:/day_work/work/gantz/already/(Gantz) Reika Shimohira/xps.xps": dict(
        convention="unreal", lower="A",
        slots={"lower_body_bone": "pelvis", "upper_body2_bone": "spine_03", "upper_body4_bone": "spine_05",
               "left_butt_bone": "Butt.l", "left_eye_bone": None},
        merges={"left_knee_bone": {"calf_twist_01_l", "calf_twist_02_l"}}),
    "E:/day_work/2025money/wish/Cooing Suit(EVE)/#Stellar Blade - Eve (Cooling)/xps.xps": dict(
        convention="xna_lara", lower="B",
        slots={"lower_body_bone": "pelvis alt", "upper_body_bone": "spine lower", "left_butt_bone": "leg left butt"},
        merges={"upper_body_bone": {"spine lower jiggle"}}),
}


@pytest.fixture(scope="module")
def loaded():
    from xps_to_pmx.core.rig.rigdata import RigData
    from xps_to_pmx.core.xps import load_xps
    from xps_to_pmx.core.xps.convert import build_import_data
    cache = {}

    def get(path):
        if path not in cache:
            cache[path] = RigData.from_import_data(build_import_data(load_xps(path)))
        return cache[path]
    return get


@pytest.mark.parametrize("path", [p for p in REAL if os.path.isfile(p)] or
                         [pytest.param("missing", marks=pytest.mark.skip("no sample files"))])
def test_regression_models(path, loaded):
    want = REAL[path]
    rig = loaded(path)
    ident = identify(rig, SPEC)
    assert ident.convention == want["convention"]
    assert ident.lower_body.case == want["lower"]
    assert all(ident.slots[s].mapped for s in REQUIRED), [s for s in REQUIRED if not ident.slots[s].mapped]
    got = _names(rig, ident, want["slots"])
    assert got == want["slots"]
    for slot, expected in want["merges"].items():
        merged = {rig.bones[b].name for b in ident.slots[slot].merges}
        assert expected <= merged, (slot, merged)
    errors = [c for c in check_mapping(rig, SPEC, ident) if c.level == ERROR]
    assert not errors, [c.text for c in errors]


def test_nameless_backwards_model_is_not_mirrored():
    named = synthetic.build()
    ref = identify(named, SPEC)
    anon = synthetic.build(rename={b.name: f"bone_{b.index:03d}" for b in named.bones})
    import numpy as np
    flip = np.array([-1.0, -1.0, 1.0])
    for b in anon.bones:
        b.head, b.tail = b.head * flip, b.tail * flip
    anon.skin.positions[:] = anon.skin.positions * flip.astype(np.float32)
    ident = identify(anon, SPEC)
    for slot in ("left_hand_bone", "left_thigh_bone", "right_upper_arm_bone", "left_index_1"):
        assert ident.bone_of(slot) == ref.bone_of(slot), slot
    assert ident.facing == "+Y"


def test_mislabelled_eye_pair_is_swapped_by_position():
    rig = synthetic.build(rename={"head eyeball left": "head eyeball right",
                                  "head eyeball right": "head eyeball left"})
    ident = identify(rig, SPEC)
    left = ident.bone_of("left_eye_bone")
    assert rig.bones[left].head[0] > 0
    assert any("标反" in n for n in ident.notes)


def test_user_blocked_slot_stays_empty():
    rig = synthetic.build()
    ident = identify(rig, SPEC, fixed={"left_toe_bone": -1})
    m = ident.slots["left_toe_bone"]
    assert m.bone == -1 and m.origin == "user"
    assert ident.slots["right_toe_bone"].bone >= 0
