"""Stage ④ planning (core/rig/skeleton.py) and the weight helpers it uses."""
from __future__ import annotations

import math
import os

import numpy as np
import pytest

import synthetic
from xps_to_pmx.core.rig.identify import identify
from xps_to_pmx.core.rig.rigdata import RigData
from xps_to_pmx.core.rig.skeleton import (BuildOptions, ExtraBone, PlannedBone, SkeletonPlan, plan_skeleton,
                                          validate_plan)
from xps_to_pmx.core.spec import load_bone_spec
from xps_to_pmx.core.weights import rules
from xps_to_pmx.core.weights.skin import SkinEditor, changed_rows

SPEC = load_bone_spec()

#: The 18-series standard + semi-standard set (note 11 §4.1) for a rig with eyes and a 3-bone spine.
STANDARD = ["操作中心", "全ての親", "センター", "グルーブ", "腰", "上半身", "上半身2", "首", "頭", "両目", "下半身"]
for _s in "左右":
    STANDARD += [f"{_s}{n}" for n in ("目", "肩P", "肩", "肩C", "腕", "腕捩", "腕捩1", "腕捩2", "腕捩3", "ひじ", "手捩",
                                       "手捩1", "手捩2", "手捩3", "手首", "ダミー", "親指０", "親指１", "親指２",
                                       "人指１", "人指２", "人指３", "足", "ひざ", "足首", "つま先", "足D", "ひざD",
                                       "足首D", "足先EX", "足IK親", "足ＩＫ", "つま先ＩＫ")]
    STANDARD.append(f"腰キャンセル{_s}")


def _plan(rig, options=None):
    ident = identify(rig, SPEC)
    slot_bones = {s: rig.bones[m.bone].name for s, m in ident.slots.items() if m.bone >= 0}
    extra = {rig.bones[i].name: ExtraBone(d.action, d.slot_id, d.category)
             for i, d in ident.bones.items() if d.action in ("keep", "merge")}
    diag = ident.lower_body
    lower = {"case": diag.case, "split_bone": rig.bones[diag.split_bone].name if diag.split_bone >= 0 else ""}
    return plan_skeleton(rig, SPEC, slot_bones, extra, lower, options or BuildOptions())


@pytest.fixture(scope="module")
def plan_a():
    rig = synthetic.build()
    return rig, _plan(rig)


def _b(plan, name) -> PlannedBone:
    b = plan.bone(name)
    assert b is not None, name
    return b


def _col(plan, name):
    i = plan.index()[name]
    return np.where(plan.skin_bones == i, plan.skin_weights, 0.0).sum(axis=1)


# ---------------------------------------------------------------------------
# skin editor and rules

def test_split_conserves_weight_and_compact_caps():
    bones = np.array([[0, 1, -1, -1], [0, 2, 3, 4]], dtype=np.int32)
    weights = np.array([[0.6, 0.4, 0, 0], [0.4, 0.3, 0.2, 0.1]])
    ed = SkinEditor(bones, weights)
    moved = ed.split(0, [(5, np.array([0.5, 0.5])), (6, np.array([0.5, 0.25]))])
    assert moved == pytest.approx(0.6 + 0.3)
    assert np.allclose(ed.totals(), 1.0)
    counts = ed.compact()
    b, w = ed.arrays()
    assert b.shape == (2, 4) and np.allclose(w.sum(axis=1), 1.0)
    assert counts["capped"] == 1          # second vertex had 6 influences
    assert 0 not in b[0]                  # first vertex: 0 fully moved away


def test_split_never_creates_weight():
    ed = SkinEditor(np.array([[0, -1, -1, -1]]), np.array([[1.0, 0, 0, 0]]))
    ed.split(0, [(1, np.array([0.8])), (2, np.array([0.8]))])
    assert ed.totals()[0] == pytest.approx(1.0)
    assert ed.column(0)[0] == pytest.approx(0.0)


def test_compact_merges_duplicates_and_removes_dust():
    ed = SkinEditor(np.array([[3, 3, 1, -1], [7, -1, -1, -1]]), np.array([[0.5, 0.4995, 0.0005, 0], [0.0004, 0, 0, 0]]))
    counts = ed.compact()
    b, w = ed.arrays()
    assert list(b[0]) == [3, -1, -1, -1] and w[0, 0] == pytest.approx(1.0)
    assert b[1, 0] == 7 and w[1, 0] == pytest.approx(1.0)   # all-dust vertex keeps its strongest bone
    assert counts["dust"] == 1


def test_changed_rows_ignores_order():
    a_b = np.array([[1, 2, -1, -1], [3, -1, -1, -1]])
    a_w = np.array([[0.5, 0.5, 0, 0], [1, 0, 0, 0]])
    b_b = np.array([[2, 1, -1, -1], [4, -1, -1, -1]])
    assert list(changed_rows(a_b, a_w, b_b, a_w)) == [1]


@pytest.mark.parametrize("mode", rules.TWIST_MODES)
def test_twist_shares_partition_and_monotone(mode):
    s = np.linspace(-0.5, 1.5, 401)
    sh = rules.twist_shares(s, mode)
    assert np.allclose(sh.sum(axis=1), 1.0) and (sh >= -1e-12).all()
    level = sh @ np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    assert (np.diff(level) >= -1e-12).all()
    assert level[0] == 0.0 and level[-1] == 1.0
    for k, t in enumerate((0.32, 0.52), start=1):   # the sub bones sit where their level dominates
        assert np.argmax(rules.twist_shares(np.array([t]), mode)[0]) == k


def test_toe_ex_share_front_only():
    ankle, ex = np.array([0.0, 0.0, 0.1]), np.array([0.0, -0.1, 0.03])
    pts = np.array([[0, 0.05, 0.05], [0, -0.05, 0.05], [0, -0.1, 0.02], [0, -0.15, 0.02]])
    share = rules.toe_ex_share(pts, ankle, ex)
    assert share[0] == 0 and share[1] == 0 and 0 < share[2] < 1 and share[3] == 1


# ---------------------------------------------------------------------------
# skeleton plan on the synthetic rig

def test_plan_has_the_standard_set_and_is_valid(plan_a):
    _, plan = plan_a
    assert plan.ok, [m.text for m in plan.messages if m.level == "error"]
    names = {b.name for b in plan.bones}
    assert not [n for n in STANDARD if n not in names]
    assert validate_plan(plan, SPEC) == []


def test_control_bone_formulas(plan_a):
    rig, plan = plan_a
    u = rig.height / 20.8
    thigh = np.mean([_b(plan, f"{s}足").head for s in "左右"], axis=0)
    knee = np.mean([_b(plan, f"{s}ひざ").head for s in "左右"], axis=0)
    center = _b(plan, "センター")
    assert center.head == pytest.approx([0, 0, knee[2] + 0.4 * (thigh[2] - knee[2])])
    assert _b(plan, "グルーブ").head[2] == pytest.approx(center.head[2] + 0.0002 * rig.height)
    lower, upper = _b(plan, "下半身"), _b(plan, "上半身")
    assert lower.head == pytest.approx(upper.head - [0, 0, 0.005 * u])
    assert lower.tail == pytest.approx(lower.head - [0, 0, u])
    waist = _b(plan, "腰")
    assert waist.head[2] == pytest.approx(thigh[2] + 0.4 * (lower.head[2] - thigh[2]))
    assert waist.movable is False and _b(plan, "全ての親").head == pytest.approx([0, 0, 0])
    eyes = _b(plan, "両目")
    assert eyes.head[2] > _b(plan, "頭").head[2] and eyes.head[0] == 0


def test_hierarchy_follows_the_spec(plan_a):
    _, plan = plan_a
    expect = {"上半身": "腰", "下半身": "腰", "腰": "グルーブ", "グルーブ": "センター", "センター": "全ての親",
              "左肩": "左肩P", "左肩C": "左肩", "左腕": "左肩C", "左腕捩": "左腕", "左腕捩1": "左腕",
              "左ひじ": "左腕捩", "左手捩": "左ひじ", "左手首": "左手捩", "腰キャンセル左": "下半身",
              "左足": "腰キャンセル左", "左足D": "腰キャンセル左", "左ひざD": "左足D", "左足首D": "左ひざD",
              "左足先EX": "左足首D", "左足IK親": "全ての親", "左足ＩＫ": "左足IK親", "左つま先ＩＫ": "左足ＩＫ",
              "首": "上半身3", "左目": "頭", "両目": "頭"}
    got = {n: _b(plan, n).parent for n in expect}
    assert got == expect


def test_grants_and_transform_order(plan_a):
    _, plan = plan_a
    expect = {"左目": ("両目", 1.0), "左肩C": ("左肩P", -1.0), "左腕捩1": ("左腕捩", 0.25), "左腕捩3": ("左腕捩", 0.75),
              "左手捩2": ("左手捩", 0.5), "腰キャンセル右": ("腰", -1.0), "左足D": ("左足", 1.0),
              "右足首D": ("右足首", 1.0)}
    for name, (parent, rate) in expect.items():
        b = _b(plan, name)
        assert (b.grant_parent, b.grant_rate) == (parent, rate), name
    assert _b(plan, "左足D").transform_order == 1 and _b(plan, "左足先EX").transform_order == 1
    order = [b.name for b in plan.bones]
    assert order.index("左足D") > order.index("左つま先ＩＫ")


def test_twist_and_d_bone_geometry(plan_a):
    _, plan = plan_a
    a, c = _b(plan, "左腕").head, _b(plan, "左ひじ").head
    assert _b(plan, "左腕捩").head == pytest.approx(a + 0.6 * (c - a))
    for k, t in ((1, 0.32), (2, 0.52), (3, 0.72)):
        assert _b(plan, f"左腕捩{k}").head == pytest.approx(a + t * (c - a))
    axis = _b(plan, "左腕捩").fixed_axis
    assert axis == pytest.approx((c - a) / np.linalg.norm(c - a))
    for fk in ("左足", "左ひざ", "左足首"):
        d = _b(plan, fk + "D")
        assert d.head == pytest.approx(_b(plan, fk).head) and d.tail == pytest.approx(_b(plan, fk).tail)
        assert d.roll_like == fk
    ankle, toe = _b(plan, "左足首").head, _b(plan, "左つま先").head
    assert _b(plan, "左足先EX").head == pytest.approx(ankle + (toe - ankle) * 0.6667, abs=1e-6)
    ikp, ik = _b(plan, "左足IK親"), _b(plan, "左足ＩＫ")
    assert ikp.head[2] == 0 and ik.head == pytest.approx(ankle)
    assert _b(plan, "左ひざ").tail == pytest.approx(ankle)       # IK chain tip reaches the target


def test_ik_definitions_and_presets(plan_a):
    rig, plan = plan_a
    ik = _b(plan, "左足ＩＫ").ik
    assert ik.target == "左足首" and [l.bone for l in ik.links] == ["左ひざ", "左足"]
    assert ik.loop == 40 and ik.unit_angle == pytest.approx(2.0, abs=1e-4)
    assert ik.links[0].limit_min[0] == pytest.approx(-math.pi) and ik.links[0].limit_max[0] == pytest.approx(
        math.radians(-0.5))
    assert ik.links[1].limit_min is None
    toe = _b(plan, "左つま先ＩＫ").ik
    assert toe.target == "左つま先" and toe.loop == 3 and toe.unit_angle == pytest.approx(4.0, abs=1e-4)
    s18 = _plan(rig, BuildOptions(ik_preset="S18"))
    assert (_b(s18, "左足ＩＫ").ik.loop, _b(s18, "左つま先ＩＫ").ik.loop) == (40, 80)
    assert _b(s18, "左足ＩＫ").ik.unit_angle == pytest.approx(1.0)


def test_weights_conserved_and_moved_to_d_and_twist(plan_a):
    rig, plan = plan_a
    totals = plan.skin_weights.sum(axis=1)
    assert np.allclose(totals[totals > 0], 1.0, atol=1e-5)
    assert plan.skin_bones.shape[1] == 4
    for fk in ("左足", "左ひざ", "左足首", "右足"):
        assert _col(plan, fk).sum() == 0
    old_thigh = rig.skin.bone_weight_column(rig.by_name["leg left thigh"]).sum()
    assert _col(plan, "左足D").sum() == pytest.approx(old_thigh, rel=1e-3)
    assert _col(plan, "左足先EX").sum() > 0
    old_upper = rig.skin.bone_weight_column(rig.by_name["arm left shoulder 2"]).sum()
    arm_total = sum(_col(plan, n).sum() for n in ("左腕", "左腕捩", "左腕捩1", "左腕捩2", "左腕捩3"))
    assert arm_total == pytest.approx(old_upper, rel=1e-3)
    assert all(_col(plan, f"左腕捩{k}").sum() > 0 for k in (1, 2, 3))
    for control in ("センター", "グルーブ", "腰", "全ての親", "左肩C", "腰キャンセル左", "左足ＩＫ"):
        assert _col(plan, control).sum() == 0, control


@pytest.mark.parametrize("case", ["C", "D"])
def test_lower_body_cases_get_split_weights(case):
    rig = synthetic.build(lower_case=case)
    plan = _plan(rig)
    assert plan.ok
    lower = _col(plan, "下半身")
    upper = _col(plan, "上半身")
    pos = rig.skin.positions
    assert lower.sum() > 0
    thigh_z = _b(plan, "左足").head[2]
    seg = _b(plan, "上半身").head[2] - thigh_z
    high = pos[:, 2] > thigh_z + 1.75 * seg
    assert lower[high].max() == pytest.approx(0.0, abs=1e-6)
    hips = (pos[:, 2] < thigh_z + 0.4 * seg) & (np.abs(pos[:, 0]) < 0.02) & (lower + upper > 0.5)
    assert (lower[hips] > 0.8 * (lower[hips] + upper[hips])).all()


def test_tier_switches():
    rig = synthetic.build()
    plan = _plan(rig, BuildOptions(tier2=False, tier3=False))
    assert plan.ok
    names = {b.name for b in plan.bones}
    for gone in ("左腕捩", "左肩P", "左肩C", "腰キャンセル左", "左ダミー", "左足D", "左足先EX", "操作中心"):
        assert gone not in names
    for kept in ("センター", "グルーブ", "腰", "左足ＩＫ", "左足IK親", "両目"):
        assert kept in names
    assert _b(plan, "左腕").parent == "左肩" and _b(plan, "左ひじ").parent == "左腕"
    assert _b(plan, "左足").parent == "下半身"
    assert _col(plan, "左足").sum() > 0


def test_one_bone_spine_gets_upper_body2_with_weights():
    rig = synthetic.build(drop=("spine middle", "spine upper"))
    plan = _plan(rig)
    assert plan.ok
    ub2 = _b(plan, "上半身2")
    assert ub2.created and _b(plan, "首").parent == "上半身2" and _b(plan, "左肩P").parent == "上半身2"
    ub, neck = _b(plan, "上半身").head, _b(plan, "首").head
    assert ub2.head == pytest.approx(ub + 0.35 * (neck - ub))
    assert _col(plan, "上半身2").sum() > 0


def test_long_non_standard_names_are_shortened():
    extra_rows = [("hair back left very long name 1", "head neck upper", (0.02, 0.05, 1.62)),
                  ("hair back left very long name 2", "hair back left very long name 1", (0.02, 0.07, 1.55)),
                  ("_dummy_thing", "head neck upper", (0.0, 0.0, 1.6)),
                  ("ok_bone", "head neck upper", (0.0, 0.02, 1.6))]
    rig = synthetic.build(extra=extra_rows)
    plan = _plan(rig)
    assert plan.ok
    by_e = {b.name_e: b for b in plan.bones if not b.slot_id}
    a, b2 = by_e["hair back left very long name 1"], by_e["hair back left very long name 2"]
    assert a.name.startswith("髪L") and b2.name.startswith("髪L") and a.name != b2.name
    assert a.name.split("_")[0] == b2.name.split("_")[0]          # same chain number
    assert b2.parent == a.name and a.parent == "頭"
    assert not by_e["_dummy_thing"].name.startswith("_dummy_")
    assert by_e["ok_bone"].name == "ok_bone"
    for b in plan.bones:
        assert len(b.name.encode("cp932")) <= 15


# ---------------------------------------------------------------------------
# counter-examples for the plan validator

def _tiny_plan(order):
    bones = {"A": PlannedBone("A", "a", head=np.zeros(3), tail=np.array([0, 0, 1.0])),
             "B": PlannedBone("B", "b", parent="A", head=np.zeros(3), tail=np.array([0, 0, 1.0]))}
    return SkeletonPlan([bones[n] for n in order])


def test_validator_catches_child_before_parent_and_duplicates():
    assert validate_plan(_tiny_plan("AB"), SPEC) == []
    assert [m.code for m in validate_plan(_tiny_plan("BA"), SPEC)] == ["build.plan_order"]
    dup = _tiny_plan("AB")
    dup.bones[1].name = "A"
    dup.bones[1].parent = ""
    assert "build.plan_duplicate" in [m.code for m in validate_plan(dup, SPEC)]


def test_validator_catches_late_grant_parent_and_bad_ik():
    plan = _tiny_plan("AB")
    plan.bones[0].grant_parent, plan.bones[0].grant_rate = "B", 1.0
    assert "build.plan_order" in [m.code for m in validate_plan(plan, SPEC)]
    from xps_to_pmx.core.rig.skeleton import IkPlan, IkLinkPlan
    plan = _tiny_plan("AB")
    plan.bones[0].ik = IkPlan("Z", [IkLinkPlan("B")], 40, 2.0)
    codes = [m.code for m in validate_plan(plan, SPEC)]
    assert "build.plan_ik" in codes and "build.plan_order" in codes


# ---------------------------------------------------------------------------
# regression models (skipped when the files are not on this machine)

REAL = ["E:/day_work/2025money/wish/inase (arbiter)/xps.xps",
        "E:/mywork/add_on/Purifier (Inase)/xps.xps",
        "E:/day_work/2025money/wish/Cooing Suit(EVE)/#Stellar Blade - Eve (Cooling)/xps.xps",
        "E:/day_work/work/gantz/already/(Gantz) Reika Shimohira/xps.xps"]


@pytest.mark.parametrize("path", [p for p in REAL if os.path.isfile(p)] or
                         [pytest.param("", marks=pytest.mark.skip("no regression models"))])
def test_regression_model_plans(path):
    from xps_to_pmx.core.xps import load_xps
    from xps_to_pmx.core.xps.convert import build_import_data
    rig = RigData.from_import_data(build_import_data(load_xps(path), path))
    plan = _plan(rig)
    assert plan.ok, [m.text for m in plan.messages if m.level == "error"]
    names = {b.name for b in plan.bones}
    missing = [n for n in STANDARD if n not in names and not n.endswith("目")]
    assert not missing
    totals = plan.skin_weights.sum(axis=1)
    assert np.allclose(totals[totals > 0], 1.0, atol=1e-5)
    for fk in ("左足", "右ひざ"):
        assert _col(plan, fk).sum() == 0
    assert _col(plan, "下半身").sum() > 0


# ---------------------------------------------------------------------------
# 下半身 acceptance checks (counter-examples)

def test_lower_body_checks_flag_belly_and_hard_cut():
    from xps_to_pmx.core.checks.lower_body import check_lower_body, lower_body_metrics
    z = np.linspace(0.6, 1.4, 81)
    pos = np.stack([np.zeros_like(z), np.zeros_like(z), z], axis=1)
    t = (z - 0.9) / 0.15
    clean = np.clip(1.0 - (t - 0.5) / 1.25, 0, 1)
    legs = np.clip(-t, 0, 1)
    lower = clean * (1 - legs)
    upper = 1 - lower - legs
    good = lower_body_metrics(pos, lower, upper, legs, 0.9, 1.05, 0.09)
    assert [i.code for i in check_lower_body(good)] == []
    belly = lower.copy()
    belly[t >= 1.75] = 0.5
    codes = [i.code for i in check_lower_body(lower_body_metrics(pos, belly, upper, legs, 0.9, 1.05, 0.09))]
    assert "lower_body.high" in codes
    hard = np.where(t < 0, 0.0, lower)
    hard_legs = np.where(t < 0, 1.0, 0.0)
    codes = [i.code for i in check_lower_body(lower_body_metrics(pos, hard, upper, hard_legs, 0.9, 1.05, 0.09))]
    assert "lower_body.hard_cut" in codes
    assert [i.code for i in check_lower_body({})] == ["lower_body.no_weight"]
