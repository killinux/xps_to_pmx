"""Every mapping check rule fires on a counter-example (hard constraint 6)."""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import synthetic  # noqa: E402
from xps_to_pmx.core.checks.mapping import check_mapping  # noqa: E402
from xps_to_pmx.core.rig.identify import identify  # noqa: E402
from xps_to_pmx.core.spec import load_bone_spec  # noqa: E402

SPEC = load_bone_spec()


def codes(rig, ident):
    return {c.code for c in check_mapping(rig, SPEC, ident)}


def test_clean_rig_has_no_errors_or_warnings():
    rig = synthetic.build()
    items = check_mapping(rig, SPEC, identify(rig, SPEC))
    assert {c.level for c in items} <= {"info"}, [(c.code, c.text) for c in items if c.level != "info"]


def test_required_missing():
    fingers = tuple(f"arm left finger {f}{l}" for f in range(1, 6) for l in "abc")
    rig = synthetic.build(drop=("arm left wrist",) + fingers)
    assert "mapping.required_missing" in codes(rig, identify(rig, SPEC))


def test_wrong_side():
    rig = synthetic.build()
    ident = identify(rig, SPEC, fixed={"left_hand_bone": rig.by_name["arm right wrist"],
                                       "right_hand_bone": rig.by_name["arm left wrist"]})
    assert "mapping.wrong_side" in codes(rig, ident)


def test_hierarchy():
    rig = synthetic.build()
    ident = identify(rig, SPEC, fixed={"left_lower_arm_bone": rig.by_name["leg left knee"]})
    assert "mapping.hierarchy" in codes(rig, ident)


def test_duplicate():
    rig = synthetic.build()
    ident = identify(rig, SPEC)
    ident.slots["right_hand_bone"].bone = ident.slots["left_hand_bone"].bone
    assert "mapping.duplicate" in codes(rig, ident)


def test_asymmetric():
    rig = synthetic.build()
    rig.bones[rig.by_name["arm left elbow"]].head += np.array([0.0, 0.0, 0.1])
    assert "mapping.asymmetric" in codes(rig, identify(rig, SPEC))


def test_limb_ratio_and_joint_position():
    rig = synthetic.build()
    rig.bones[rig.by_name["arm left elbow"]].head = np.array([0.53, 0.0, 1.41])
    found = codes(rig, identify(rig, SPEC))
    assert {"mapping.limb_ratio", "mapping.joint_position"} <= found


def test_no_weights():
    rig = synthetic.build()
    arm = rig.by_name["arm left shoulder 2"]
    rig.skin.weights[rig.skin.bones[:, 0] == arm, 0] = 0.0
    rig._accumulate_weights()
    assert "mapping.no_weights" in codes(rig, identify(rig, SPEC))


def test_control_weighted():
    rig = synthetic.build()
    rig.skin.bones[:3, 0] = rig.by_name["root ground"]  # far from the hips: not absorbed by 下半身
    rig._accumulate_weights()
    assert "mapping.control_weighted" in codes(rig, identify(rig, SPEC))


def test_weighted_hip_root_is_absorbed_into_lower_body():
    rig = synthetic.build()
    hips = rig.by_name["root hips"]
    near = np.where(rig.skin.bones[:, 0] == rig.by_name["pelvis"])[0][:5]
    rig.skin.bones[near, 0] = hips
    rig._accumulate_weights()
    ident = identify(rig, SPEC)
    assert hips in ident.slots["lower_body_bone"].merges
    assert ident.bone_of("center_bone") == -1  # センター will be generated without weights


def test_lower_body_case_messages():
    for case, code in (("A", "mapping.lower_body_A"), ("C", "mapping.lower_body_C"),
                       ("D", "mapping.lower_body_D")):
        rig = synthetic.build(lower_case=case)
        assert code in codes(rig, identify(rig, SPEC))


def test_no_eyes():
    rig = synthetic.build(drop=("head eyeball left", "head eyeball right"))
    assert "mapping.no_eyes" in codes(rig, identify(rig, SPEC))


def test_mapped_bone_deleted():
    rig = synthetic.build()
    ident = identify(rig, SPEC)
    hand = ident.bone_of("left_hand_bone")
    ident.bones[hand].action = "delete"
    assert "mapping.mapped_bone_deleted" in codes(rig, ident)


def test_model_facing_backwards_gives_one_warning_not_side_errors():
    rig = synthetic.build()
    flip = np.array([-1.0, -1.0, 1.0])  # rotate 180° about Z: left side ends up at -X
    for b in rig.bones:
        b.head = b.head * flip
        b.tail = b.tail * flip
    rig.skin.positions[:] = rig.skin.positions * flip.astype(np.float32)
    ident = identify(rig, SPEC)
    found = codes(rig, ident)
    assert ident.facing == "+Y"
    assert "mapping.facing_back" in found and "mapping.wrong_side" not in found


def test_flattened_hierarchy_is_a_warning():
    rig = synthetic.build()
    elbow = rig.by_name["arm left elbow"]
    rig.bones[elbow].parent = rig.by_name["root ground"]  # exporter parented it to the root control
    rebuilt = type(rig)(rig.bones, rig.skin, "flat")
    ident = identify(rebuilt, SPEC)
    found = codes(rebuilt, ident)
    assert "mapping.hierarchy_flat" in found and "mapping.hierarchy" not in found
