"""Pure pose maths: rotations, arm plan, skinning blend, scale and distortion gate."""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xps_to_pmx.core.pose import (  # noqa: E402
    EXPORT_SCALE, apply, arm_target_direction, blend_matrices, blend_points, distortion, down_angle,
    forward_angle, plan_arm_pose, plan_scale, rotation_between)


@pytest.mark.parametrize("a,b", [((1, 0, 0), (0, 0, -1)), ((1, 0, 0), (1, 0, 0)), ((1, 0, 0), (-1, 0, 0)),
                                 ((0.3, -0.2, 0.9), (-0.5, 0.1, 0.2))])
def test_rotation_between(a, b):
    r = rotation_between(np.array(a), np.array(b))
    out = r @ (np.array(a) / np.linalg.norm(a))
    assert np.allclose(out, np.array(b) / np.linalg.norm(b), atol=1e-9)
    assert np.allclose(r @ r.T, np.eye(3), atol=1e-9) and np.isclose(np.linalg.det(r), 1.0)


def test_angles():
    assert math.isclose(down_angle(np.array([1, 0, -1])), 45.0)
    assert math.isclose(down_angle(np.array([1, 0, 0])), 0.0)
    assert math.isclose(forward_angle(np.array([1, -1, 0])), 45.0)
    d = arm_target_direction(-1.0, 37.5)
    assert d[0] < 0 and math.isclose(down_angle(d), 37.5)


def _t_pose_arm():
    # 0 chest, 1 upper arm, 2 forearm, 3 hand, 4 finger, 5 head (unrelated)
    parents = [-1, 0, 1, 2, 3, 0]
    heads = np.array([[0, 0, 1.3], [0.14, 0, 1.41], [0.35, -0.02, 1.41], [0.56, -0.08, 1.40],
                      [0.62, -0.09, 1.40], [0, 0, 1.6]], float)
    return parents, heads


def test_plan_arm_pose_straight_a_pose():
    parents, heads = _t_pose_arm()
    plan = plan_arm_pose(parents, heads, [("left", 1, 2, 3)], upper_deg=37.5)
    arm = plan.arms[0]
    assert math.isclose(arm.after_upper_deg, 37.5, abs_tol=1e-6)
    assert math.isclose(arm.after_fore_deg, 37.5, abs_tol=1e-6)  # straight arm
    m_hand = plan.transforms[3]
    new = [apply(plan.transforms.get(i, np.eye(4)), heads[i]) for i in range(len(heads))]
    assert np.allclose(new[1], heads[1])                   # shoulder joint is the pivot
    fore = new[3] - new[2]
    assert abs(forward_angle(fore)) < 1e-6                 # forearm back in the frontal plane
    assert 5 not in plan.transforms and 0 not in plan.transforms
    assert np.allclose(m_hand, plan.transforms[4])         # fingers follow the hand


def test_plan_arm_pose_animasa_bent_forearm():
    parents, heads = _t_pose_arm()
    plan = plan_arm_pose(parents, heads, [("left", 1, 2, 3)], upper_deg=29.72, fore_extra_deg=10.56)
    assert math.isclose(plan.arms[0].after_fore_deg, 40.28, abs_tol=1e-6)


def test_already_posed_arm_is_left_alone():
    parents = [-1, 0, 1, 2]
    d = arm_target_direction(1.0, 37.5)
    heads = np.array([[0, 0, 1.3], [0.14, 0, 1.41], [0.14, 0, 1.41] + 0.2 * d, [0.14, 0, 1.41] + 0.4 * d])
    plan = plan_arm_pose(parents, heads, [("left", 1, 2, 3)], upper_deg=37.5)
    assert plan.transforms == {}


def test_blend_matches_rigid_motion_for_single_bone_vertices():
    parents, heads = _t_pose_arm()
    plan = plan_arm_pose(parents, heads, [("left", 1, 2, 3)], upper_deg=37.5)
    pts = np.array([[0.30, 0, 1.41], [0.0, 0, 1.0], [0.25, 0, 1.41]])
    bones = np.array([[1, -1, -1, -1], [0, -1, -1, -1], [1, 2, -1, -1]])
    weights = np.array([[1, 0, 0, 0], [1, 0, 0, 0], [0.5, 0.5, 0, 0]], np.float32)
    mats = blend_matrices(bones, weights, plan.transforms)
    out = blend_points(pts, mats)
    assert np.allclose(out[0], apply(plan.transforms[1], pts[0]))
    assert np.allclose(out[1], pts[1])  # chest vertex untouched
    expected = 0.5 * apply(plan.transforms[1], pts[2]) + 0.5 * apply(plan.transforms[2], pts[2])
    assert np.allclose(out[2], expected)


def test_scale_modes():
    s = plan_scale("SHOULDER", shoulder_z=1.40, ground_z=-0.05, top_z=1.75)
    assert math.isclose(s.shoulder_pmx, 17.0)
    assert math.isclose(s.factor, 17.0 / EXPORT_SCALE / 1.45)
    m = s.matrix()
    assert np.isclose((m @ [0, 0, -0.05, 1])[2], 0.0)       # ground lands on z = 0
    assert math.isclose(plan_scale("FIXED_125", 1.4, 0.0, 1.7).factor, 1.0)
    assert math.isclose(plan_scale("FIXED_10", 1.4, 0.0, 1.7).height_pmx, 17.0)


def test_distortion_gate():
    before = np.array([1.0, 1.0, 1.0, 1.0, 0.01])
    assert distortion(before, before * 2.0, size=2.0)["torn"] == 0          # uniform rescale is fine
    after = before.copy()
    after[4] = 0.2                                                           # 20× and +19 cm
    result = distortion(before, after, size=2.0)
    assert result["torn"] == 1 and result["worst_ratio"] > 3
