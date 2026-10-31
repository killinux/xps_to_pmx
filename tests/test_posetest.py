"""Pose tests (design doc §16): the MMD-style evaluation, each measurement firing and staying silent, views.

Every check has a case that fires and a case that must stay silent (hard constraint 6).
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xps_to_pmx.core.checks import checkup  # noqa: E402
from xps_to_pmx.core.checks import posetest as pt  # noqa: E402
from xps_to_pmx.core.pose import axis_angle  # noqa: E402
from xps_to_pmx.core.spec import load_bone_spec  # noqa: E402

BODY = {s.name_j for s in load_bone_spec().slots if s.name_j}

#: name, parent, head — an MMD skeleton in Blender axes (Z up, facing -Y, left = +X), arms straight out.
BONES = [
    ("全ての親", "", (0, 0, 0)), ("センター", "全ての親", (0, 0, 0.8)),
    ("上半身", "センター", (0, 0, 1.0)), ("上半身2", "上半身", (0, 0, 1.15)), ("首", "上半身2", (0, 0, 1.4)),
    ("頭", "首", (0, 0, 1.5)), ("下半身", "センター", (0, 0, 1.0)),
]
for _p, _s in (("左", 1.0), ("右", -1.0)):
    BONES += [
        (_p + "足", "下半身", (0.09 * _s, 0, 0.9)), (_p + "ひざ", _p + "足", (0.09 * _s, 0, 0.5)),
        (_p + "足首", _p + "ひざ", (0.09 * _s, 0, 0.1)), (_p + "つま先", _p + "足首", (0.09 * _s, -0.12, 0.0)),
        (_p + "肩", "上半身2", (0.03 * _s, 0, 1.36)), (_p + "腕", _p + "肩", (0.15 * _s, 0, 1.36)),
        (_p + "ひじ", _p + "腕", (0.40 * _s, 0, 1.36)), (_p + "手捩", _p + "ひじ", (0.55 * _s, 0, 1.36)),
        (_p + "手首", _p + "手捩", (0.65 * _s, 0, 1.36)), (_p + "中指1", _p + "手首", (0.75 * _s, 0, 1.36)),
    ]
SEGMENTS = [("頭", None, 0.08), ("上半身", "首", 0.12)]
for _p in "左右":
    SEGMENTS += [(_p + "足", _p + "ひざ", 0.06), (_p + "ひざ", _p + "足首", 0.05), (_p + "腕", _p + "ひじ", 0.04),
                 (_p + "ひじ", _p + "手首", 0.035), (_p + "手首", _p + "中指1", 0.03)]


def _heads():
    return {name: np.array(head, float) for name, _, head in BONES}


def _cloud():
    """Cylinders around limbs and trunk, a ball for the head; each vertex owned by its segment's start bone."""
    heads = _heads()
    pts, owner = [], []
    ring = np.linspace(0, 2 * math.pi, 12, endpoint=False)
    for start, end, radius in SEGMENTS:
        a = heads[start]
        if end is None:  # head ball
            for z in np.linspace(0.05, 0.15, 6):
                for t in ring:
                    pts.append(a + np.array([radius * math.cos(t), radius * math.sin(t), z]))
                    owner.append(start)
            continue
        b = heads[end]
        d = (b - a) / np.linalg.norm(b - a)
        u = np.cross(d, [0, 1, 0]) if abs(d[1]) < 0.9 else np.cross(d, [1, 0, 0])
        u /= np.linalg.norm(u)
        v = np.cross(d, u)
        for s in np.linspace(0.02, 0.98, 25):
            for t in ring:
                pts.append(a + (b - a) * s + radius * (math.cos(t) * u + math.sin(t) * v))
                owner.append(start)
    return np.array(pts), owner


def _rig(weights=None, extra_bones=(), grants=None, positions=None, owners=None):
    names = [b[0] for b in BONES] + [b[0] for b in extra_bones]
    index = {n: i for i, n in enumerate(names)}
    bones = []
    for name, parent, head in list(BONES) + list(extra_bones):
        g = (grants or {}).get(name)
        bones.append(pt.PoseBone(name, index.get(parent, -1), np.array(head, float),
                                 index[g[0]] if g else -1, g[1] if g else 0.0))
    pos, own = (positions, owners) if positions is not None else _cloud()
    n = len(pos)
    sb = np.full((n, 4), -1, np.int64)
    sw = np.zeros((n, 4))
    for i, o in enumerate(own):
        pairs = (weights or {}).get(i) or [(o, 1.0)]
        for k, (bone, w) in enumerate(pairs):
            sb[i, k], sw[i, k] = index[bone], w
    return pt.PoseRig(bones, pos, sb, sw, BODY | {"左手捩1", "左手捩2", "左手捩3"})


def _issues(rig, test_id):
    test = pt.find_test(rig, test_id)
    return [i for i in pt.run_tests(rig, [test])]


def _shin_vertices(rig, t0=0.3, t1=0.9):
    knee, ankle = rig.head("左ひざ"), rig.head("左足首")
    t, r = pt.project(rig.positions, knee, ankle)
    return np.nonzero((t >= t0) & (t <= t1) & (r < 0.1) & (rig.positions[:, 0] > 0))[0]


# -- evaluation ---------------------------------------------------------------------------------

def test_fraction_scales_the_angle_and_keeps_the_axis():
    r = axis_angle((1, 0, 0), math.radians(90))
    half = pt.fraction(r, 0.5)
    assert np.allclose(half, axis_angle((1, 0, 0), math.radians(45)))
    assert np.allclose(pt.fraction(r, -1.0), axis_angle((1, 0, 0), math.radians(-90)))
    assert np.allclose(pt.fraction(np.eye(3), 0.3), np.eye(3))


def test_grants_follow_the_source_by_their_rate_and_children_follow_parents():
    extra = [("左手捩2", "左ひじ", (0.5, 0, 1.36))]
    rig = _rig(extra_bones=extra, grants={"左手捩2": ("左手捩", 0.5)})
    fore = rig.head("左手首") - rig.head("左ひじ")
    mats = pt.skin_matrices(rig, {rig.by_name["左手捩"]: axis_angle(fore, math.radians(90))})
    angle = lambda m: math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(m[:3, :3]) - 1) / 2))))  # noqa: E731
    assert abs(angle(mats[rig.by_name["左手捩2"]]) - 45.0) < 1e-6
    assert abs(angle(mats[rig.by_name["左手首"]]) - 90.0) < 1e-6        # child of 手捩
    assert abs(angle(mats[rig.by_name["左ひじ"]])) < 1e-6               # parent: unaffected


def test_deform_normalises_weights_and_keeps_unweighted_vertices():
    rig = _rig()
    rig.skin_weights[0, 0] = 2.0                 # unnormalised single weight: same motion as 1.0
    rig.skin_bones[1, :] = -1                    # unweighted
    mats = pt.skin_matrices(rig, {rig.by_name["頭"]: axis_angle((0, 0, 1), math.radians(60))})
    posed = pt.deform(rig, mats)
    m = mats[rig.by_name["頭"]]
    assert np.allclose(posed[0], m[:3, :3] @ rig.positions[0] + m[:3, 3])
    assert np.allclose(posed[1], rig.positions[1])


# -- follow -------------------------------------------------------------------------------------

def test_clean_model_has_no_issues():
    rig = _rig()
    assert pt.run_tests(rig) == []


def test_shin_vertices_keeping_thigh_weight_lag_in_the_knee_test():
    base = _rig()
    shin = _shin_vertices(base, 0.3, 0.7)
    rig = _rig(weights={int(i): [("左ひざ", 0.6), ("左足", 0.4)] for i in shin})
    issues = [i for i in _issues(rig, "knee_L") if i.kind == "follow"]
    assert len(issues) == 1
    issue = issues[0]
    assert issue.region == "小腿" and issue.expect == "move" and set(issue.vertices) <= set(shin)
    assert list(issue.culprits) == ["左足"]


def test_thigh_vertices_dragged_by_the_knee_are_found():
    base = _rig()
    hip, knee = base.head("左足"), base.head("左ひざ")
    t, r = pt.project(base.positions, hip, knee)
    thigh = np.nonzero((t > 0.15) & (t < 0.55) & (r < 0.1) & (base.positions[:, 0] > 0))[0]
    rig = _rig(weights={int(i): [("左足", 0.5), ("左ひざ", 0.5)] for i in thigh})
    issues = [i for i in _issues(rig, "knee_L") if i.kind == "follow"]
    assert [(i.region, i.expect) for i in issues] == [("大腿", "stay")]


def test_skirt_weighted_vertices_are_not_body_and_stay_silent():
    base = _rig()
    shin = _shin_vertices(base)
    skirt = [("スカート_1", "下半身", (0.09, 0, 0.9))]
    rig = _rig(weights={int(i): [("スカート_1", 1.0)] for i in shin}, extra_bones=skirt)
    assert [i for i in _issues(rig, "knee_L") if i.kind == "follow"] == []


def test_other_side_dragged_by_a_shoulder_needs_enough_vertices():
    base = _rig()
    right = np.nonzero((base.positions[:, 0] < -0.12) & (base.positions[:, 2] > 1.2))[0]
    cape = [("披肩", "左肩", (0.1, 0.1, 1.3))]
    many = _rig(weights={int(i): [("披肩", 1.0)] for i in right[:40]}, extra_bones=cape)
    issues = [i for i in _issues(many, "shrug_L") if i.region == "另一侧"]
    assert len(issues) == 1 and list(issues[0].culprits) == ["披肩"]
    few = _rig(weights={int(i): [("披肩", 1.0)] for i in right[:pt.SIDE_MIN_VERTICES - 5]}, extra_bones=cape)
    assert [i for i in _issues(few, "shrug_L") if i.region == "另一侧"] == []


# -- twist --------------------------------------------------------------------------------------

def _forearm(rig):
    elbow, wrist = rig.head("左ひじ"), rig.head("左手首")
    t, r = pt.project(rig.positions, elbow, wrist)
    return t, (r < 0.1) & (rig.positions[:, 0] > 0.3)


def test_hard_twist_transition_collapses():
    base = _rig()
    t, arm = _forearm(base)
    weights = {int(i): [("左ひじ", 0.5), ("左手首", 0.5)] for i in np.nonzero(arm & (t > 0.5) & (t < 0.95))[0]}
    issues = [i for i in _issues(_rig(weights=weights), "twist_L") if i.kind == "twist"]
    assert len(issues) == 1 and issues[0].worst < pt.TWIST_RATIO and issues[0].region == "左前臂"


def test_stepped_twist_weights_do_not_collapse():
    extra = [("左手捩1", "左ひじ", (0.45, 0, 1.36)), ("左手捩2", "左ひじ", (0.5, 0, 1.36)),
             ("左手捩3", "左ひじ", (0.6, 0, 1.36))]
    grants = {"左手捩1": ("左手捩", 0.25), "左手捩2": ("左手捩", 0.5), "左手捩3": ("左手捩", 0.75)}
    base = _rig(extra_bones=extra, grants=grants)
    t, arm = _forearm(base)
    weights = {}
    for i in np.nonzero(arm)[0]:
        x = t[i]
        steps = ["左ひじ", "左手捩1", "左手捩2", "左手捩3", "左手捩"]
        k = min(int(x * 5), 4)
        frac = x * 5 - k
        nxt = steps[min(k + 1, 4)]
        weights[int(i)] = [(steps[k], 1.0 - frac), (nxt, frac)] if nxt != steps[k] else [(steps[k], 1.0)]
    rig = _rig(weights=weights, extra_bones=extra, grants=grants)
    assert [i for i in _issues(rig, "twist_L") if i.kind == "twist"] == []


# -- cracks -------------------------------------------------------------------------------------

def _with_seam(weights_b):
    pos, own = _cloud()
    base = _rig(positions=pos, owners=own)
    shin = _shin_vertices(base, 0.4, 0.6)[:4]
    pos2 = np.concatenate([pos, pos[shin]])
    own2 = own + [own[i] for i in shin]
    weights = {len(pos) + k: weights_b for k in range(len(shin))}
    return _rig(weights=weights, positions=pos2, owners=own2)


def test_seam_with_different_weights_cracks():
    rig = _with_seam([("左足", 1.0)])           # duplicates of shin vertices weighted to the thigh
    cracks = [i for i in pt.run_tests(rig) if i.kind == "crack"]
    assert len(cracks) == 1 and cracks[0].total >= pt.CRACK_MIN_PAIRS and cracks[0].segment == "shin_L"


def test_seam_with_equal_weights_stays_closed():
    rig = _with_seam([("左ひざ", 1.0)])
    assert [i for i in pt.run_tests(rig) if i.kind == "crack"] == []


# -- tests, views, findings ---------------------------------------------------------------------

def test_tests_exist_only_for_present_bones_and_belly_starts_above_the_hips():
    rig = _rig()
    ids = {t.id for t in pt.build_tests(rig)}
    assert {"knee_L", "knee_R", "elbow_L", "raise_R", "twist_L", "shrug_R", "hip_twist", "waist_bend",
            "head_turn"} <= ids
    assert "armtwist_L" not in ids                     # no 腕捩 in this rig
    lift = 1.0 - 0.9                                   # waist 1.0, hips 0.9 → 2 L = waist + 0.1
    assert abs(pt.belly_start(rig) - max(0.12, lift / 0.4)) < 1e-9


def test_view_frames_the_vertices_in_the_test_pose():
    rig = _rig()
    shin = _shin_vertices(rig)
    test = pt.find_test(rig, "knee_L")
    view = pt.make_view(rig, shin, test)
    posed = pt.view_positions(rig, view)[shin]
    assert view["test"] == "knee_L" and view["vertices"] == sorted(int(v) for v in shin)
    assert np.all(np.abs(posed - np.array(view["focus"])) <= view["size"])
    assert view["dir"] == list(test.view)
    custom = pt.make_view(rig, shin, bone="左ひざ", axis=(1, 0, 0), angle=90)
    assert np.allclose(pt.view_positions(rig, custom), pt.view_positions(rig, view))


def test_issue_finding_texts_and_split_fix_for_a_duplicate():
    base = _rig()
    right = np.nonzero((base.positions[:, 0] < -0.12) & (base.positions[:, 2] > 1.2))[0]
    cape = [("披肩", "左肩", (0.1, 0.1, 1.3))]
    rig = _rig(weights={int(i): [("披肩", 1.0)] for i in right[:40]}, extra_bones=cape)
    issue = next(i for i in _issues(rig, "shrug_L") if i.region == "另一侧")
    dup = [{"bone": "cape back 1", "src": "cape back 1", "twin": "cape back 1.001"}]
    f = pt.issue_finding(rig, issue, {"披肩": "cape back 1"}, dup)
    assert f.code == "pose.follow" and f.level == checkup.WARNING and f.subject == "shrug_L:另一侧"
    assert "左肩上耸 25°" in f.text and "被带着动" in f.text and "cape back 1.001" in f.text
    assert f.fix is not None and f.fix.kind == "split_side" and f.fix.twin == "cape back 1.001"
    assert f.view["test"] == "shrug_L" and len(f.view["vertices"]) == len(issue.vertices)
    plain = pt.issue_finding(rig, issue, {}, [])
    assert plain.fix is None and "需要你看" in plain.text


def test_fixed_findings_keep_their_view():
    view = {"test": "knee_L", "vertices": [1, 2], "focus": [0, 0, 0.5], "size": 0.3, "dir": [1, 0, 0]}
    previous = {"pose.follow:knee_L:小腿": {"level": "warning", "text": "x", "part": "leg_l", "code": "pose.follow",
                                          "view": view}}
    out = checkup.diff_findings(previous, [])
    assert len(out) == 1 and out[0].state == "fixed" and out[0].view == view
