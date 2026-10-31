"""Default disposition of every source bone that is not a slot's primary bone.

Actions: ``merge`` (weights go into a slot), ``keep`` (stays as a non-standard
bone under its nearest kept ancestor: face, hair, cloth, props …), ``delete``
(no weights anywhere below it).  Rules follow Convert_to_MMD5's
``helper_classifier`` adapted to slot ids (research note 10a §2.8).

Limb helpers (design doc §15.7): the head position picks the candidate
segment, the weights decide when they clearly lie in another segment of the
same limb (a calf twist bone whose head sits on the knee but whose weights
cover the shin belongs to ひざ, not to 足).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from .limbs import limb_segments, segment_mass
from .rigdata import RigData

HAIR_RE = re.compile(r"hair|髪|ponytail|twintail|pigtail|braid|ahoge|アホ毛|もみあげ|おさげ|kami", re.IGNORECASE)
#: Hair words that also name cloth parts (a shawl's fringe): hair unless the name also has a cloth word.
HAIR_AMBIGUOUS_RE = re.compile(r"bangs|fringe", re.IGNORECASE)
CLOTH_RE = re.compile(r"skirt|スカート|coat|cloak|cape|mantle|shawl|veil|scar[ft]|hanging|drape|apron|robe|frill"
                      r"|sash|ribbon|sleeve|tie\b|necktie|strap|belt|tassel|cloth|dress|suit|jacket|hood|tail",
                      re.IGNORECASE)
BREAST_RE = re.compile(r"boob|breast|bust|pector|oppai|乳|胸", re.IGNORECASE)
BUTT_RE = re.compile(r"butt|glute|hip_?flesh|尻|屁股", re.IGNORECASE)
#: Substring match ("weapons", "xgun", "headphones" are props).  No "bow" (it is in "elbow") and no
#: "blade" (in "shoulderblade"): 2026-10-31 those turned ~160 elbow / scapula helpers into props.
PROP_RE = re.compile(r"weapon|sword|gun|shield|staff|knife|dagger|arrow|spear|axe|prop|wand|book"
                     r"|bag|phone|cup|bottle|accessor|acc\d", re.IGNORECASE)
#: "bow" as a whole word is a ribbon bow (cloth) in this corpus; a weapon bow is caught by PROP_RE
#: ("weapon").  The look-arounds only refuse lower-case letters, so "Bow3a" and "skirt_bow" match.
RIBBON_BOW_RE = re.compile(r"(?<![a-z])(?i:bow)(?![a-z])")
TWIST_RE = re.compile(r"twist|roll|tw\d|foretwist|uptwist", re.IGNORECASE)
GENITAL_RE = re.compile(r"genital|gens\b|pussy|vagina|labia|clit|penis|dick|testic|scrot|anus|anal", re.IGNORECASE)
#: Face words, matched as whole name tokens ("lip" in "head hair lip upper", not in "hairclip").
FACE_TOKENS = frozenset(("lip", "lips", "mouth", "jaw", "tongue", "teeth", "tooth", "eyelid", "eyebrow", "brow",
                         "lash", "eyelash", "cheek", "nose", "nostril", "chin"))
FACE_CJK_RE = re.compile(r"口|唇|舌|歯|眉|頬|鼻|顎")
_TOKEN_RE = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+")
#: Limb-end slots that collect their unmapped weighted descendants (carpals, heels …).
LIMB_END_SLOTS = ("hand_bone", "ankle_bone")

SPINE_SLOTS = ("upper_body_bone", "upper_body1_bone", "upper_body2_bone", "upper_body3_bone", "upper_body4_bone",
               "neck_bone", "neck1_bone")
END_SLOTS = ("toe_bone", "thumb_2", "index_3", "middle_3", "ring_3", "pinky_3")
EYE_SLOTS = ("left_eye_bone", "right_eye_bone")
#: Kept chains whose unrecognised descendants stay on the chain instead of joining a limb or the spine.
CHAIN_CATEGORIES = ("hair", "cloth", "breast", "butt", "prop", "genital")
CHAIN_LABELS = {"hair": "头发", "cloth": "衣物", "breast": "胸部", "butt": "臀部", "prop": "道具", "genital": "生殖器"}


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


def name_tokens(name: str) -> List[str]:
    """Lower-case word tokens of a bone name, splitting on separators and camelCase."""
    return [t.lower() for t in _TOKEN_RE.findall(name)]


def has_face_word(name: str) -> bool:
    return bool(FACE_TOKENS.intersection(name_tokens(name)) or FACE_CJK_RE.search(name))


class _FaceZone:
    """Mouth region, scaled by the distance between the eyes ``e`` (needs both eye slots).

    Below the eyes by 0.15e–2e, within 0.6e of the face's centre line, and not more
    than 0.3e behind the eyes.  Hair strands hanging beside or in front of the face
    stay outside it (checked on rouffe, whose upper lip bones are named "head hair upper …").
    """

    def __init__(self, rig: RigData, slot_bones: Dict[str, int], facing: str):
        eyes = [slot_bones.get(s, -1) for s in EYE_SLOTS]
        self.ok = all(e >= 0 for e in eyes)
        if not self.ok:
            return
        heads = np.array([rig.bones[e].head for e in eyes], float)
        self.e = float(abs(heads[0, 0] - heads[1, 0]))
        self.ok = self.e > 1e-4
        self.centre = heads.mean(axis=0)
        self.front = -1.0 if facing != "+Y" else 1.0      # models face -Y

    def contains(self, p: np.ndarray) -> bool:
        if not self.ok:
            return False
        dz = float(p[2]) - float(self.centre[2])
        behind = (float(p[1]) - float(self.centre[1])) * -self.front
        return (-2.0 * self.e < dz < -0.15 * self.e and abs(float(p[0]) - float(self.centre[0])) < 0.6 * self.e
                and behind < 0.3 * self.e)


def classify_bones(rig: RigData, slot_bones: Dict[str, int], merged: Dict[int, str],
                   head: int, facing: str = "-Y") -> Dict[int, Disposition]:
    """Dispositions for every bone; ``slot_bones`` maps slot → primary bone, ``merged`` bone → slot."""
    out: Dict[int, Disposition] = {}
    primary_slot = {b: s for s, b in slot_bones.items() if b >= 0}
    eps = rig.centre_eps()

    segments = {side: limb_segments(rig, slot_bones, side) for side in ("left", "right")}
    limb_ends = {slot_bones[f"{side}_{e}"]: f"{side}_{e}" for side in ("left", "right") for e in LIMB_END_SLOTS
                 if slot_bones.get(f"{side}_{e}", -1) >= 0}
    spine = [(s, slot_bones[s]) for s in SPINE_SLOTS if slot_bones.get(s, -1) >= 0]
    ends = {slot_bones[f"{side}_{e}"]: f"{side}_{e}" for side in ("left", "right") for e in END_SLOTS
            if slot_bones.get(f"{side}_{e}", -1) >= 0}
    face_zone = _FaceZone(rig, slot_bones, facing)

    # parents first, so a bone can see what happened to its ancestors
    for b in sorted(rig.bones, key=lambda bone: len(rig.ancestors(bone.index))):
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
            out[i] = _head_disposition(i, name, b.head, face_zone)
            continue
        if _is_hair(name):
            out[i] = Disposition(i, "keep", "", "hair", "头发链")
            continue
        if PROP_RE.search(name):
            out[i] = Disposition(i, "keep", "", "prop", "道具/武器")
            continue
        if BREAST_RE.search(name) and not RIBBON_BOW_RE.search(name):  # a bow on the chest is cloth
            owner = next((primary_slot[a] for a in ancestors if a in primary_slot
                          and primary_slot[a].endswith("breast_bone")), None)
            if owner:
                out[i] = Disposition(i, "merge", owner, "breast", "胸骨的子骨")
            else:
                out[i] = Disposition(i, "keep", "", "breast", "未映射的胸骨")
            continue
        if _is_cloth(name):
            out[i] = Disposition(i, "keep", "", "cloth", "衣物链")
            continue
        if GENITAL_RE.search(name):
            out[i] = Disposition(i, "keep", "", "genital", "保留，挂在 下半身 下")
            continue
        if BUTT_RE.search(name):
            out[i] = Disposition(i, "keep", "", "butt", "臀部骨")
            continue
        chain = _kept_chain(ancestors, out, primary_slot)
        if chain is not None:
            out[i] = Disposition(i, "keep", "", chain, f"未识别的带权重骨，挂在保留的{CHAIN_LABELS[chain]}链下")
            continue
        limb = _limb_disposition(rig, i, name, ancestors, segments, eps)
        if limb is not None:
            out[i] = limb
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
        out[i] = Disposition(i, "keep", "", _category_of(name, default="other"), "未识别的带权重骨，保留原名")
    _mouth_bones_named_hair(rig, out, head, face_zone)
    return out


def _head_disposition(i: int, name: str, head_pos: np.ndarray, face_zone: _FaceZone) -> Disposition:
    hair = bool(HAIR_RE.search(name) or HAIR_AMBIGUOUS_RE.search(name))
    face = has_face_word(name)
    if hair and face:
        if face_zone.contains(head_pos):
            return Disposition(i, "keep", "", "face", "头部下的骨：名字像头发也像脸，位置在嘴部，按脸部处理")
        return Disposition(i, "keep", "", "hair", "头部下的骨：名字像头发也像脸，位置不在嘴部，按头发处理")
    return Disposition(i, "keep", "", "hair" if hair else "face", "头部下的骨（表情/头发用）")


def _limb_disposition(rig: RigData, i: int, name: str, ancestors: List[int], segments, eps: float
                      ) -> Optional[Disposition]:
    b = rig.bones[i]
    x = float(b.head[0])
    side = "left" if x > eps else "right" if x < -eps else ""
    if not side:
        return None  # centred helpers never join a limb
    # children of a segment's end bone belong to that end, never to the segment itself
    allowed = [s for s in segments[side] if s.end_bone not in ancestors]
    best = None
    for s in allowed:
        t, dist, length = _segment_distance(b.head, s.a, s.c)
        if -0.15 <= t <= 1.15 and dist < 0.35 * max(length, 1e-6):
            if best is None or dist < best[1]:
                best = (s.slot, dist)
    if best is None:
        return None
    slot = best[0]
    reason = "位于肢体骨段上的辅助/扭转骨"
    mass = segment_mass(rig, i, allowed)
    owner = mass.clear_owner() if mass is not None else None
    if owner is not None and owner != slot:
        reason = (f"肢体辅助骨：头在 {slot} 段，但 {mass.fractions[owner]:.0%} 的明确权重在 {owner} 段，"
                  f"按权重所在段并入")
        slot = owner
    return Disposition(i, "merge", slot, "twist" if TWIST_RE.search(name) else "helper", reason)


def _mouth_bones_named_hair(rig: RigData, out: Dict[int, Disposition], head: int, face_zone: _FaceZone) -> None:
    """Bones named hair that sit in the mouth region and do not continue a hair chain are face bones."""
    for i, d in out.items():
        if d.action != "keep" or d.category != "hair" or head < 0 or head not in rig.ancestors(i):
            continue
        parent = rig.bones[i].parent
        if parent in out and out[parent].category == "hair":
            continue  # e.g. long bangs hanging in front of the mouth
        if face_zone.contains(rig.bones[i].head):
            d.category = "face"
            d.reason = "名字像头发，但位置在嘴部且不在头发链上，按脸部处理"


def _kept_chain(ancestors: List[int], out: Dict[int, Disposition], primary_slot: Dict[int, str]) -> Optional[str]:
    """Category of the nearest kept ancestor when it is a chain category and no slot bone lies in between."""
    for a in ancestors:
        if a in primary_slot:
            return None
        d = out.get(a)
        if d is not None and d.action == "keep":
            return d.category if d.category in CHAIN_CATEGORIES else None
    return None


def _is_cloth(name: str) -> bool:
    return bool(CLOTH_RE.search(name) or RIBBON_BOW_RE.search(name))


def _is_hair(name: str) -> bool:
    return bool(HAIR_RE.search(name) or (HAIR_AMBIGUOUS_RE.search(name) and not _is_cloth(name)))


def _category_of(name: str, default: str = "other") -> str:
    if _is_hair(name):
        return "hair"
    if BREAST_RE.search(name) and not RIBBON_BOW_RE.search(name):
        return "breast"
    if PROP_RE.search(name):
        return "prop"
    if _is_cloth(name):
        return "cloth"
    if TWIST_RE.search(name):
        return "twist"
    return default
