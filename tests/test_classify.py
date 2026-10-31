"""Classifier rules added in M4.5 (design doc §15.7): limb helpers by weight, face/hair names, cloth chains."""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import synthetic  # noqa: E402
from xps_to_pmx.core.rig.classify import has_face_word, name_tokens  # noqa: E402
from xps_to_pmx.core.rig.identify import identify  # noqa: E402
from xps_to_pmx.core.rig.limbs import limb_segments, segment_mass  # noqa: E402
from xps_to_pmx.core.spec import load_bone_spec  # noqa: E402

SPEC = load_bone_spec()
KNEE = (0.083, 0, 0.55)


def _move_weights(rig, from_bone, to_bone, t_range):
    """Give ``to_bone`` the weights of ``from_bone``'s vertices whose position along it lies in ``t_range``."""
    src = rig.by_name[from_bone]
    a, c = rig.bones[src].head, rig.bones[src].tail
    t = (rig.skin.positions - a) @ (c - a) / float((c - a) @ (c - a))
    sel = (rig.skin.bones[:, 0] == src) & (t >= t_range[0]) & (t <= t_range[1])
    rig.skin.bones[sel, 0] = rig.by_name[to_bone]
    rig._accumulate_weights()
    return int(sel.sum())


def test_calf_twist_on_the_knee_merges_into_the_knee_by_weight():
    # head on the knee, parent = thigh, weights on the upper shin: the head rule alone picks 足
    rig = synthetic.build(extra=[("unused bip001 lcalftwist", "leg left thigh", KNEE)])
    assert _move_weights(rig, "leg left knee", "unused bip001 lcalftwist", (0.2, 0.6)) > 10
    ident = identify(rig, SPEC)
    disp = ident.bones[rig.by_name["unused bip001 lcalftwist"]]
    assert disp.action == "merge" and disp.slot_id == "left_knee_bone", disp
    assert "按权重所在段并入" in disp.reason


def test_helper_straddling_the_knee_keeps_the_head_rule():
    rig = synthetic.build(extra=[("unused knee_l", "leg left thigh", KNEE)])
    # weights only in the joint zones on both sides of the knee
    _move_weights(rig, "leg left knee", "unused knee_l", (0.0, 0.08))
    _move_weights(rig, "leg left thigh", "unused knee_l", (0.92, 1.0))
    ident = identify(rig, SPEC)
    sb = ident.slot_bones()
    mass = segment_mass(rig, rig.by_name["unused knee_l"], limb_segments(rig, sb, "left"))
    assert mass is not None and mass.decisive < 0.5 and mass.clear_owner() is None
    assert ident.bones[rig.by_name["unused knee_l"]].slot_id == "left_thigh_bone"


def test_upper_arm_twist_stays_on_the_upper_arm():
    rig = synthetic.build(extra=[("unused bip001 luparmtwist", "arm left shoulder 2", (0.20, 0, 1.41))])
    _move_weights(rig, "arm left shoulder 2", "unused bip001 luparmtwist", (0.2, 0.8))
    ident = identify(rig, SPEC)
    assert ident.bones[rig.by_name["unused bip001 luparmtwist"]].slot_id == "left_upper_arm_bone"


def test_name_tokens_and_face_words():
    assert name_tokens("head hair lip upper") == ["head", "hair", "lip", "upper"]
    assert name_tokens("lLipUpperInner") == ["l", "lip", "upper", "inner"]
    assert has_face_word("head hair lip lower left") and has_face_word("lLipUpper") and has_face_word("下唇")
    assert not has_face_word("hairclip left") and not has_face_word("lipstick bottle")


def _head_rig(extra):
    return synthetic.build(extra=extra)


def test_hair_named_mouth_bones_are_face_but_hair_chains_stay_hair():
    extra = [
        ("head hair lip lower", "head neck upper", (0.0, -0.085, 1.55)),       # both words, in the mouth zone
        ("head hair upper middle", "head neck upper", (0.0, -0.086, 1.56)),    # hair word only, in the zone
        ("head hair front 1", "head neck upper", (0.0, -0.09, 1.66)),          # bangs above the eyes
        ("head hair front 2", "head hair front 1", (0.0, -0.09, 1.56)),        # its chain reaches the mouth
        ("head hair left 2", "head neck upper", (0.06, -0.06, 1.55)),          # beside the face
        ("head hair eyelid cover", "head neck upper", (0.0, -0.09, 1.65)),     # both words, above the eyes
    ]
    rig = _head_rig(extra)
    ident = identify(rig, SPEC)
    cat = {n: ident.bones[rig.by_name[n]].category for n, _, _ in extra}
    assert cat == {"head hair lip lower": "face", "head hair upper middle": "face", "head hair front 1": "hair",
                   "head hair front 2": "hair", "head hair left 2": "hair", "head hair eyelid cover": "hair"}, cat


def test_without_eyes_the_old_rule_applies():
    rig = synthetic.build(drop=("head eyeball left", "head eyeball right"),
                          extra=[("head hair upper middle", "head neck upper", (0.0, -0.086, 1.56))])
    ident = identify(rig, SPEC)
    assert ident.bones[rig.by_name["head hair upper middle"]].category == "hair"


def test_shawl_fringe_is_cloth_and_plain_bangs_are_hair():
    extra = [("shawl back 1", "spine upper", (0.0, 0.08, 1.38)),
             ("shawl fringe back 1", "shawl back 1", (0.0, 0.10, 1.25)),
             ("bangs side 1", "spine upper", (0.10, -0.02, 1.45))]
    rig = synthetic.build(extra=extra)
    ident = identify(rig, SPEC)
    cat = {n: ident.bones[rig.by_name[n]].category for n, _, _ in extra}
    assert cat == {"shawl back 1": "cloth", "shawl fringe back 1": "cloth", "bangs side 1": "hair"}, cat


def test_unnamed_bones_on_a_cloth_chain_are_cloth():
    extra = [("cape 1", "spine upper", (0.0, 0.10, 1.38)),
             ("bone_23", "cape 1", (0.0, 0.12, 1.20)),
             ("bone_24", "bone_23", (0.0, 0.13, 1.00)),
             ("bone_99", "spine upper", (0.0, 0.10, 1.30))]
    rig = synthetic.build(extra=extra)
    ident = identify(rig, SPEC)
    cat = {n: ident.bones[rig.by_name[n]].category for n, _, _ in extra}
    assert cat["bone_23"] == "cloth" and cat["bone_24"] == "cloth", cat
    assert cat["bone_99"] != "cloth", cat
    assert np.isfinite(rig.height)
