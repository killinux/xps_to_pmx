"""Default disposition of every source bone that is not a slot's primary bone.

Actions: ``merge`` (weights go into a slot), ``keep`` (stays as a non-standard
bone under its nearest kept ancestor: face, hair, cloth, props …), ``delete``
(no weights anywhere below it).  Rules follow Convert_to_MMD5's
``helper_classifier`` adapted to slot ids (research note 10a §2.8).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np

from .rigdata import RigData

HAIR_RE = re.compile(r"hair|髪|ponytail|twintail|pigtail|braid|bangs|fringe|ahoge|アホ毛|もみあげ|おさげ|kami",
                     re.IGNORECASE)
CLOTH_RE = re.compile(r"skirt|スカート|coat|cloak|cape|mantle|shawl|veil|scar[ft]|hanging|drape|apron|robe|frill"
                      r"|sash|ribbon|sleeve|tie\b|necktie|strap|belt|tassel|cloth|dress|suit|jacket|hood|tail",
                      re.IGNORECASE)
BREAST_RE = re.compile(r"boob|breast|bust|pector|oppai|乳|胸", re.IGNORECASE)
BUTT_RE = re.compile(r"butt|glute|hip_?flesh|尻|屁股", re.IGNORECASE)
PROP_RE = re.compile(r"weapon|sword|gun|shield|staff|blade|knife|dagger|bow\b|arrow|spear|axe|prop|wand|book"
                     r"|bag|phone|cup|bottle|accessor|acc\d", re.IGNORECASE)
TWIST_RE = re.compile(r"twist|roll|tw\d|foretwist|uptwist", re.IGNORECASE)
GENITAL_RE = re.compile(r"genital|gens\b|pussy|vagina|labia|clit|penis|dick|testic|scrot|anus|anal", re.IGNORECASE)
#: Limb-end slots that collect their unmapped weighted descendants (carpals, heels …).
LIMB_END_SLOTS = ("hand_bone", "ankle_bone")

LIMB_SEGMENTS = (
    ("upper_arm_bone", "lower_arm_bone"),
    ("lower_arm_bone", "hand_bone"),
    ("shoulder_bone", "upper_arm_bone"),
    ("thigh_bone", "knee_bone"),
    ("knee_bone", "ankle_bone"),
    ("ankle_bone", "toe_bone"),
)
SPINE_SLOTS = ("upper_body_bone", "upper_body1_bone", "upper_body2_bone", "upper_body3_bone", "upper_body4_bone",
               "neck_bone", "neck1_bone")
END_SLOTS = ("toe_bone", "thumb_2", "index_3", "middle_3", "ring_3", "pinky_3")


@dataclass
class Disposition:
    bone: int
    action: str          # map | merge | keep | delete
    slot_id: str         # map/merge target slot
    category: str
    reason: str
    origin: str = "classifier"


def _segment_distance(p: np.ndarray, a: np.ndarray, b: np.ndarray) -> Tuple[float, float, float]:
    ab = b - a
    denom = float(np.dot(ab, ab))
    if denom < 1e-12:
        return 0.0, float(np.linalg.norm(p - a)), 0.0
    t = float(np.dot(p - a, ab)) / denom
    closest = a + np.clip(t, 0.0, 1.0) * ab
    return t, float(np.linalg.norm(p - closest)), float(np.sqrt(denom))


def classify_bones(rig: RigData, slot_bones: Dict[str, int], merged: Dict[int, str],
                   head: int) -> Dict[int, Disposition]:
    """Dispositions for every bone; ``slot_bones`` maps slot → primary bone, ``merged`` bone → slot."""
    out: Dict[int, Disposition] = {}
    primary_slot = {b: s for s, b in slot_bones.items() if b >= 0}
    eps = rig.centre_eps()

    segments = []
    for side in ("left", "right"):
        for a_key, b_key in LIMB_SEGMENTS:
            a, b = slot_bones.get(f"{side}_{a_key}", -1), slot_bones.get(f"{side}_{b_key}", -1)
            if a >= 0 and b >= 0:
                segments.append((f"{side}_{a_key}", side, b, rig.bones[a].head, rig.bones[b].head))
    limb_ends = {slot_bones[f"{side}_{e}"]: f"{side}_{e}" for side in ("left", "right") for e in LIMB_END_SLOTS
                 if slot_bones.get(f"{side}_{e}", -1) >= 0}
    spine = [(s, slot_bones[s]) for s in SPINE_SLOTS if slot_bones.get(s, -1) >= 0]
    ends = {slot_bones[f"{side}_{e}"]: f"{side}_{e}" for side in ("left", "right") for e in END_SLOTS
            if slot_bones.get(f"{side}_{e}", -1) >= 0}

    for b in rig.bones:
        i = b.index
        if i in primary_slot:
            out[i] = Disposition(i, "map", primary_slot[i], "humanoid", "槽位主骨")
            continue
        if i in merged:
            out[i] = Disposition(i, "merge", merged[i], _category_of(b.name), "名称表/诊断指定并入")
            continue
        if not rig.subtree_weighted(i):
            out[i] = Disposition(i, "delete", "", _category_of(b.name, default="unused"), "自身及子孙都没有权重")
            continue
        if not b.weighted:
            out[i] = Disposition(i, "delete", "", _category_of(b.name, default="structure"),
                                 "无权重的结构骨（子骨改挂到上一级保留骨）")
            continue
        name = b.name
        ancestors = rig.ancestors(i)
        end_owner = next((ends[a] for a in ancestors if a in ends), None)
        if end_owner:
            out[i] = Disposition(i, "merge", end_owner, "detail", "手指/脚尖末端的细分骨")
            continue
        under_head = head >= 0 and (head in ancestors)
        if under_head:
            cat = "hair" if HAIR_RE.search(name) else "face"
            out[i] = Disposition(i, "keep", "", cat, "头部下的骨（表情/头发用）")
            continue
        if HAIR_RE.search(name):
            out[i] = Disposition(i, "keep", "", "hair", "头发链")
            continue
        if PROP_RE.search(name):
            out[i] = Disposition(i, "keep", "", "prop", "道具/武器")
            continue
        if BREAST_RE.search(name):
            owner = next((primary_slot[a] for a in ancestors if a in primary_slot
                          and primary_slot[a].endswith("breast_bone")), None)
            if owner:
                out[i] = Disposition(i, "merge", owner, "breast", "胸骨的子骨")
            else:
                out[i] = Disposition(i, "keep", "", "breast", "未映射的胸骨")
            continue
        if CLOTH_RE.search(name):
            out[i] = Disposition(i, "keep", "", "cloth", "衣物链")
            continue
        if GENITAL_RE.search(name):
            out[i] = Disposition(i, "keep", "", "genital", "保留，挂在 下半身 下")
            continue
        if BUTT_RE.search(name):
            out[i] = Disposition(i, "keep", "", "butt", "臀部骨")
            continue
        x = float(b.head[0])
        side_of_bone = "left" if x > eps else "right" if x < -eps else ""
        best = None
        for slot, side, end_bone, a, c in segments:
            if side != side_of_bone or end_bone in ancestors:
                continue  # centred helpers never join a limb; children of the segment end belong to it
            t, dist, length = _segment_distance(b.head, a, c)
            if -0.15 <= t <= 1.15 and dist < 0.35 * max(length, 1e-6):
                if best is None or dist < best[1]:
                    best = (slot, dist)
        if best is not None:
            cat = "twist" if TWIST_RE.search(name) else "helper"
            out[i] = Disposition(i, "merge", best[0], cat, "位于肢体骨段上的辅助/扭转骨")
            continue
        limb_owner = next((limb_ends[a] for a in ancestors if a in limb_ends), None)
        if limb_owner:
            out[i] = Disposition(i, "merge", limb_owner, "helper", "手/脚下的辅助骨（掌骨、脚跟…）")
            continue
        spine_owner = next((primary_slot[a] for a in ancestors if a in primary_slot
                            and primary_slot[a] in SPINE_SLOTS), None)
        if spine_owner and abs(float(b.head[0])) < eps and spine:
            nearest = min(spine, key=lambda sb: abs(float(rig.bones[sb[1]].head[2]) - float(b.head[2])))
            out[i] = Disposition(i, "merge", nearest[0], "helper", "脊柱上的居中辅助骨")
            continue
        if BUTT_RE.search(name):
            out[i] = Disposition(i, "keep", "", "butt", "臀部骨")
            continue
        out[i] = Disposition(i, "keep", "", _category_of(name, default="other"), "未识别的带权重骨，保留原名")
    return out


def _category_of(name: str, default: str = "other") -> str:
    if HAIR_RE.search(name):
        return "hair"
    if BREAST_RE.search(name):
        return "breast"
    if PROP_RE.search(name):
        return "prop"
    if CLOTH_RE.search(name):
        return "cloth"
    if TWIST_RE.search(name):
        return "twist"
    return default
