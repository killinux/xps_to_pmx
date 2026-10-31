"""Checkup (design doc §15.5): cause checks on synthetic rigs, symptom checks on synthetic skins, the diff.

Every check has a case that fires and a case that must stay silent (hard constraint 6).
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import synthetic  # noqa: E402
from xps_to_pmx.core.checks import cause, checkup  # noqa: E402
from xps_to_pmx.core.rig.classify import Disposition  # noqa: E402
from xps_to_pmx.core.rig.identify import identify  # noqa: E402
from xps_to_pmx.core.rig.rigdata import RigBone, RigData, SkinData  # noqa: E402
from xps_to_pmx.core.spec import load_bone_spec  # noqa: E402

SPEC = load_bone_spec()
KNEE = (0.083, 0, 0.55)


def _twist_rig():
    rig = synthetic.build(extra=[("unused bip001 lcalftwist", "leg left thigh", KNEE)])
    knee = rig.by_name["leg left knee"]
    a, c = rig.bones[knee].head, rig.bones[knee].tail
    t = (rig.skin.positions - a) @ (c - a) / float((c - a) @ (c - a))
    sel = (rig.skin.bones[:, 0] == knee) & (t >= 0.2) & (t <= 0.6)
    rig.skin.bones[sel, 0] = rig.by_name["unused bip001 lcalftwist"]
    rig._accumulate_weights()
    return rig


def _force_merge(ident, rig, bone, slot):
    i = rig.by_name[bone]
    ident.bones[i] = Disposition(i, "merge", slot, "twist", "test")


# -- merge segment -------------------------------------------------------------------

def test_merge_segment_fires_for_a_wrong_merge_and_suggests_the_owner():
    rig = _twist_rig()
    ident = identify(rig, SPEC)
    _force_merge(ident, rig, "unused bip001 lcalftwist", "left_thigh_bone")   # what the old classifier did
    analysis = cause.merge_analysis(rig, ident.slot_bones(), ident.bones)
    items = cause.check_merge_segments(rig, SPEC, analysis, set())
    assert [i.code for i in items] == ["mapping.merge_segment"]
    fix = items[0].fix
    assert fix.kind == "bone" and fix.slot_id == "left_knee_bone" and fix.auto and fix.action == "merge"
    assert "左ひざ" in items[0].text


def test_merge_segment_is_silent_for_the_right_merge_and_manual_when_user_decided():
    rig = _twist_rig()
    ident = identify(rig, SPEC)          # the classifier already merges it into the knee
    analysis = cause.merge_analysis(rig, ident.slot_bones(), ident.bones)
    assert not cause.check_merge_segments(rig, SPEC, analysis, set())
    _force_merge(ident, rig, "unused bip001 lcalftwist", "left_thigh_bone")
    analysis = cause.merge_analysis(rig, ident.slot_bones(), ident.bones)
    items = cause.check_merge_segments(rig, SPEC, analysis, {"bone:unused bip001 lcalftwist"})
    assert len(items) == 1 and not items[0].fix.auto and "手动指定" in items[0].text


# -- duplicate names -----------------------------------------------------------------

def _duplicate_rig(split=False):
    """Two bones named "cape side 1": the left copy carries the weights of both sides."""
    bones = [RigBone(0, "root", -1, np.array([0, 0, 0.0]), np.array([0, 0, 1.0])),
             RigBone(1, "cape side 1", 0, np.array([0.15, 0.1, 1.3]), np.array([0.15, 0.1, 1.0]), "cape side 1"),
             RigBone(2, "cape side 1.001", 0, np.array([-0.15, 0.1, 1.3]), np.array([-0.15, 0.1, 1.0]),
                     "cape side 1"),
             RigBone(3, "body", 0, np.array([0, 0, 1.0]), np.array([0, 0, 1.6]))]
    rng = np.random.default_rng(1)
    cape = np.column_stack([rng.uniform(-0.25, 0.25, 200), np.full(200, 0.1), rng.uniform(1.0, 1.3, 200)])
    body = np.column_stack([np.zeros(50), np.zeros(50), np.linspace(0.0, 1.7, 50)])
    pos = np.concatenate([cape, body]).astype(np.float32)
    b = np.full((250, 4), -1, np.int32)
    w = np.zeros((250, 4), np.float32)
    b[:200, 0] = 1
    if split:
        b[:200, 0] = np.where(cape[:, 0] < 0, 2, 1)
    b[200:, 0] = 3
    w[:, 0] = 1.0
    return RigData(bones, SkinData(pos, b, w))


def test_duplicate_name_found_with_a_split_fix():
    rig = _duplicate_rig()
    pairs = cause.find_duplicates(rig)
    assert len(pairs) == 1
    p = pairs[0]
    assert (rig.bones[p.bone].name, rig.bones[p.twin].name, p.twin_side) == ("cape side 1", "cape side 1.001", -1.0)
    assert 0.3 < p.share < 0.6
    items = cause.check_duplicates(rig, pairs)
    assert items[0].fix.kind == "split_side" and not items[0].fix.auto and items[0].fix.twin == "cape side 1.001"


def test_duplicate_name_silent_once_split():
    assert cause.find_duplicates(_duplicate_rig(split=True)) == []


# -- joint leak ----------------------------------------------------------------------

def _leg(leak_down: float, n: int = 400):
    """A straight leg along -Z: thigh 0.95→0.55, shin 0.55→0.12; returns positions and a column function."""
    z = np.linspace(0.12, 0.95, n)
    pos = np.column_stack([np.full(n, 0.08), np.zeros(n), z])
    upper = np.where(z >= 0.55, 1.0, 0.0)
    shin = (z < 0.55 - 0.15 * 0.43) & (z > 0.55 - 0.6 * 0.43)
    upper = np.where(shin, leak_down, upper)
    lower = 1.0 - upper
    cols = {"左足": upper, "左ひざ": lower}

    def column(names):
        return sum((cols[n] for n in names if n in cols), np.zeros(n))
    js = checkup.JointSpec("left", "knee", ["左足"], ["左ひざ"], np.array([0.08, 0, 0.95]),
                           np.array([0.08, 0, 0.55]), np.array([0.08, 0, 0.12]), "left_thigh_bone", "left_knee_bone")
    return pos, column, js


def test_joint_leak_fires_and_traces_the_merged_bone():
    pos, column, js = _leg(leak_down=0.8)
    leaks = checkup.joint_leaks(pos, column, [js])
    assert leaks[0].direction_flags() == (True, False)
    analysis = [{"bone": "unused bip001 lcalftwist", "slot": "left_thigh_bone",
                 "fractions": {"left_thigh_bone": 0.0, "left_knee_bone": 1.0}}]
    found = checkup.joint_findings(leaks, SPEC, analysis, [])
    assert len(found) == 1 and found[0].level == checkup.ERROR and found[0].part == "leg_l"
    assert found[0].fix.slot_id == "left_knee_bone" and found[0].fix.bone == "unused bip001 lcalftwist"


def test_joint_leak_without_a_cause_asks_for_a_look_and_clean_leg_is_silent():
    pos, column, js = _leg(leak_down=0.8)
    found = checkup.joint_findings(checkup.joint_leaks(pos, column, [js]), SPEC, [], [])
    assert len(found) == 1 and found[0].fix is None and found[0].level == checkup.WARNING
    pos, column, js = _leg(leak_down=0.0)
    assert checkup.joint_leaks(pos, column, [js])[0].direction_flags() == (False, False)


def test_joint_specs_from_mmd_heads():
    heads = {SPEC[f"left_{k}"].name_j: np.array([0.1, 0, z]) for k, z in
             (("thigh_bone", 0.95), ("knee_bone", 0.55), ("ankle_bone", 0.12), ("leg_d_bone", 0.95))}
    js = checkup.joint_specs(SPEC, heads)
    assert len(js) == 1 and js[0].joint == "knee" and js[0].upper == ["左足", "左足D"]


# -- side leak -----------------------------------------------------------------------

def test_side_leak_fires_and_uses_the_duplicate_as_the_cause():
    rng = np.random.default_rng(2)
    pos = np.column_stack([rng.uniform(-0.3, 0.3, 300), np.zeros(300), rng.uniform(1.0, 1.3, 300)])
    cols = [np.ones(300), np.where(pos[:, 0] > 0, 1.0, 0.0)]       # bone 0 crosses, bone 1 stays left
    heads = np.array([[0.15, 0, 1.3], [0.15, 0, 1.2]])
    leaks = checkup.side_leaks(["衣L1_1", "衣L2_1"], heads, pos, lambda i: cols[i], 1.7)
    assert [l.bone for l in leaks] == ["衣L1_1"]
    dups = [{"bone": "cape side 1", "twin": "cape side 1.001", "src": "cape side 1"}]
    found = checkup.side_findings(leaks, {"衣L1_1": "cape side 1"}, dups, lambda b: "other")
    assert found[0].fix.kind == "split_side" and found[0].level == checkup.WARNING
    found = checkup.side_findings(leaks, {}, dups, lambda b: "other")
    assert found[0].fix is None and found[0].level == checkup.INFO


# -- diff ----------------------------------------------------------------------------

def test_diff_marks_new_remaining_and_fixed():
    prev = {"checkup.joint_leak:left_knee_down:x": {"level": "error", "text": "膝", "part": "leg_l",
                                                    "code": "checkup.joint_leak"},
            "checkup.side_leak:衣L1_1": {"level": "warning", "text": "披肩", "part": "other",
                                         "code": "checkup.side_leak"}}
    cur = [checkup.Finding("checkup.side_leak", "warning", "披肩", "other", "衣L1_1", "衣L1_1"),
           checkup.Finding("checkup.joint_leak", "warning", "肘", "arm_r", "右ひじ", "right_elbow_down")]
    out = checkup.diff_findings(prev, cur)
    states = {f.key: f.state for f in out}
    assert states == {"checkup.side_leak:衣L1_1": "remaining", "checkup.joint_leak:right_elbow_down": "new",
                      "checkup.joint_leak:left_knee_down:x": "fixed"}
    assert checkup.summarize([{"level": f.level, "state": f.state} for f in out]) == \
        {"error": 0, "warning": 2, "info": 0, "fixed": 1, "auto_fixed": 0}


def test_band_owned_by_the_thigh_just_below_the_knee_is_not_a_leak():
    """Like the band under each knee of Bunny Ultimate 18: 100 % thigh, right below the joint, on purpose."""
    n = 400
    z = np.linspace(0.12, 0.95, n)
    pos = np.column_stack([np.full(n, 0.08), np.zeros(n), z])
    t = (0.55 - z) / 0.43                       # along the shin from the knee
    band = (t >= 0.16) & (t <= 0.21)
    upper = np.where((z >= 0.55) | band, 1.0, 0.0)
    cols = {"左足": upper, "左ひざ": 1.0 - upper}

    def column(names):
        return sum((cols[nm] for nm in names if nm in cols), np.zeros(n))
    js = checkup.JointSpec("left", "knee", ["左足"], ["左ひざ"], np.array([0.08, 0, 0.95]),
                           np.array([0.08, 0, 0.55]), np.array([0.08, 0, 0.12]))
    leak = checkup.joint_leaks(pos, column, [js])[0]
    assert leak.down == 0 and leak.direction_flags() == (False, False)


def test_merge_segment_ignores_cloth_merged_into_a_limb():
    rig = _twist_rig()
    ident = identify(rig, SPEC)
    i = rig.by_name["unused bip001 lcalftwist"]
    ident.bones[i] = Disposition(i, "merge", "left_thigh_bone", "cloth", "test: a skirt piece")
    analysis = cause.merge_analysis(rig, ident.slot_bones(), ident.bones)
    assert all(a.bone != i for a in analysis)
    assert not cause.check_merge_segments(rig, SPEC, analysis, set())


def test_twin_parent_moves_to_the_namesake_on_its_side():
    from xps_to_pmx.core.weights.split import twin_parent
    namesakes = [("shawl back right 1", 0.081), ("shawl back right 1.001", -0.081)]
    # rouffe: the right "shawl back right 2" hangs from the left "shawl back right 1"
    assert twin_parent(-0.138, "shawl back right 1", 0.081, namesakes, 0.017) == "shawl back right 1.001"
    # already on its own side, on the centre line, or without a namesake there: nothing changes
    assert twin_parent(-0.138, "shawl back right 1.001", -0.081, namesakes, 0.017) is None
    assert twin_parent(-0.138, "spine upper", 0.0, [("spine upper", 0.0)], 0.017) is None
    assert twin_parent(-0.138, "arm left shoulder 1", 0.05, [("arm left shoulder 1", 0.05)], 0.017) is None
