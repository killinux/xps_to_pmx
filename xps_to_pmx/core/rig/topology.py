"""Name-independent skeleton identification from hierarchy, positions and weights.

Used to fill slots the alias table did not resolve and to cross-check the
alias results (design doc §5.3, approach adapted from Convert_to_MMD5's
``skeleton_identifier``).  Only bones whose subtree carries weights count, so
leftover control rigs (``unused ARM LEFT IK.L`` …) are ignored.

Blender coordinates: Z up, model faces -Y, the character's left is +X.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from .rigdata import RigData

_EYE_RE = re.compile(r"eye|目", re.IGNORECASE)
_NOT_EYE_RE = re.compile(r"lid|brow|lash|socket|眉|瞼|まぶた", re.IGNORECASE)
_BREAST_RE = re.compile(r"boob|breast|bust|pector|oppai|乳|胸", re.IGNORECASE)

FINGERS = ("index", "middle", "ring", "pinky")
#: An arm chain reaches at least this fraction of the model height sideways (steep A-poses ≈ 0.2).
ARM_REACH = 0.15


@dataclass
class TopologyResult:
    slots: Dict[str, int] = field(default_factory=dict)
    reasons: Dict[str, str] = field(default_factory=dict)
    merges: Dict[str, List[int]] = field(default_factory=dict)
    leg_fork: int = -1
    arm_fork: int = -1
    spine_chain: List[int] = field(default_factory=list)
    neck_chain: List[int] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def put(self, slot: str, bone: Optional[int], reason: str) -> None:
        if bone is not None and bone >= 0:
            self.slots[slot] = bone
            self.reasons[slot] = reason


def identify_topology(rig: RigData) -> TopologyResult:
    res = TopologyResult()
    if not len(rig):
        res.notes.append("no bones")
        return res
    res.leg_fork = find_leg_fork(rig)
    res.arm_fork = find_arm_fork(rig)
    if res.leg_fork < 0:
        res.notes.append("leg fork not found")
    if res.arm_fork < 0:
        res.notes.append("arm fork (chest) not found")
    if res.leg_fork >= 0:
        _assign_legs(rig, res)
        _assign_root_and_center(rig, res)
    facing_back = _toes_point_backwards(rig, res)
    if res.leg_fork >= 0 and res.arm_fork >= 0:
        res.spine_chain = spine_chain(rig, res.leg_fork, res.arm_fork)
    if res.arm_fork >= 0:
        res.neck_chain = neck_chain(rig, res.arm_fork)
        _assign_neck_head(rig, res)
        _assign_arms(rig, res)
        _assign_breasts(rig, res)
    if res.spine_chain:
        neck = res.slots.get("neck_bone", res.slots.get("head_bone", -1))
        for slot, bone in assign_spine(rig, res.spine_chain, neck).items():
            res.put(slot, bone, "spine chain by position (上半身2 nearest to 0.35 of 上半身→首)")
    head = res.slots.get("head_bone", -1)
    if head >= 0:
        _assign_eyes(rig, res, head)
    if facing_back:
        _swap_sides(res)
        res.notes.append("toes point to +Y: model faces backwards, left/right swapped")
    return res


def _toes_point_backwards(rig: RigData, res: TopologyResult) -> bool:
    """Toes in front of the ankles should be at -Y; if they sit at +Y the model faces +Y."""
    votes = []
    for side in ("left", "right"):
        ankle, toe = res.slots.get(f"{side}_ankle_bone"), res.slots.get(f"{side}_toe_bone")
        if ankle is not None and toe is not None:
            votes.append(float(rig.bones[toe].head[1] - rig.bones[ankle].head[1]))
    return bool(votes) and sum(votes) > 0


def _swap_sides(res: TopologyResult) -> None:
    def swap(key: str) -> str:
        if key.startswith("left_"):
            return "right_" + key[5:]
        if key.startswith("right_"):
            return "left_" + key[6:]
        return key

    res.slots = {swap(k): v for k, v in res.slots.items()}
    res.reasons = {swap(k): v for k, v in res.reasons.items()}
    res.merges = {swap(k): v for k, v in res.merges.items()}


# ---------------------------------------------------------------------------
# helpers

def _significant_children(rig: RigData, index: int) -> List[int]:
    return [c for c in rig.bones[index].children if rig.subtree_weighted(c)]


def _subtree_heads(rig: RigData, index: int) -> np.ndarray:
    return rig.heads(rig.subtree(index))


def _depth(rig: RigData, index: int) -> int:
    return len(rig.ancestors(index))


def _drop_coincident(rig: RigData, chain: List[int], tol: float) -> List[int]:
    """Remove chain bones whose head coincides with the previous kept bone (zero-length helpers).

    The ancestor is kept (``lFoot`` rather than its coincident child ``lMetatarsals``).
    """
    out: List[int] = []
    for b in chain:
        if out and np.linalg.norm(rig.bones[b].head - rig.bones[out[-1]].head) < tol:
            continue
        out.append(b)
    return out


def _dropped(chain: List[int], kept: List[int]) -> List[int]:
    keep = set(kept)
    return [b for b in chain if b not in keep]


# ---------------------------------------------------------------------------
# forks

def find_leg_fork(rig: RigData) -> int:
    """Deepest bone with one weighted child chain reaching the floor on each side."""
    eps = rig.centre_eps()
    floor_band = rig.floor + 0.15 * rig.height
    best, best_depth = -1, -1
    for b in rig.bones:
        left = right = False
        for c in _significant_children(rig, b.index):
            pts = _subtree_heads(rig, c)
            if pts[:, 2].min() > floor_band or pts[:, 2].max() - pts[:, 2].min() < 0.3 * rig.height:
                continue
            mean_x = float(pts[:, 0].mean())
            if mean_x > eps:
                left = True
            elif mean_x < -eps:
                right = True
        if left and right:
            d = _depth(rig, b.index)
            if d > best_depth:
                best, best_depth = b.index, d
    return best


def find_arm_fork(rig: RigData) -> int:
    """Deepest bone with a weighted child chain reaching far sideways on each side, above the legs."""
    eps = rig.centre_eps()
    best, best_depth = -1, -1
    for b in rig.bones:
        left = right = False
        for c in _significant_children(rig, b.index):
            pts = _subtree_heads(rig, c)
            if pts[:, 2].min() < rig.floor + 0.4 * rig.height:
                continue
            if pts[:, 0].max() > ARM_REACH * rig.height and pts[:, 0].mean() > eps:
                left = True
            if pts[:, 0].min() < -ARM_REACH * rig.height and pts[:, 0].mean() < -eps:
                right = True
        if left and right:
            d = _depth(rig, b.index)
            if d > best_depth:
                best, best_depth = b.index, d
    return best


# ---------------------------------------------------------------------------
# legs, root, centre

def _leg_chain(rig: RigData, start: int) -> Tuple[List[int], List[int]]:
    chain, cur = [start], start
    while True:
        kids = _significant_children(rig, cur)
        if not kids:
            break
        cur = min(kids, key=lambda c: (float(_subtree_heads(rig, c)[:, 2].min()), -len(rig.subtree(c))))
        chain.append(cur)
    kept = _drop_coincident(rig, chain, 0.004 * rig.height)
    return kept, _dropped(chain, kept)


def _assign_legs(rig: RigData, res: TopologyResult) -> None:
    eps = rig.centre_eps()
    for c in _significant_children(rig, res.leg_fork):
        pts = _subtree_heads(rig, c)
        if pts[:, 2].min() > rig.floor + 0.15 * rig.height:
            continue
        side = "left" if pts[:, 0].mean() > eps else "right" if pts[:, 0].mean() < -eps else ""
        if not side or f"{side}_thigh_bone" in res.slots:
            continue
        chain, coincident = _leg_chain(rig, c)
        if len(chain) < 3:
            res.notes.append(f"{side} leg chain too short")
            continue
        thigh = chain[0]
        ankle_pos = _ankle_position(rig, chain)
        ankle = chain[ankle_pos]
        mid_z = (float(rig.bones[thigh].head[2]) + float(rig.bones[ankle].head[2])) / 2
        between = chain[1:ankle_pos]
        knee = min(between, key=lambda b: abs(float(rig.bones[b].head[2]) - mid_z)) if between else -1
        toe = _toe_bone(rig, chain[ankle_pos + 1:], ankle)
        res.put(f"{side}_thigh_bone", thigh, "leg chain from the leg fork")
        res.put(f"{side}_knee_bone", knee, "leg chain bone nearest mid height")
        res.put(f"{side}_ankle_bone", ankle, "leg chain bone nearest 7% height")
        res.put(f"{side}_toe_bone", toe, "first leg chain bone forward of the ankle")
        extra = [b for b in between if b != knee]
        if extra:
            res.merges.setdefault(f"{side}_thigh_bone", []).extend(extra)
        if toe >= 0:
            mid_foot = chain[ankle_pos + 1:chain.index(toe)]
            if mid_foot:
                res.merges.setdefault(f"{side}_ankle_bone", []).extend(mid_foot)
        for b in coincident:  # zero-length helpers merge into the bone they sit on
            owner = max((k for k in chain if rig.is_ancestor(k, b)), key=lambda k: _depth(rig, k), default=-1)
            slot = {thigh: "thigh", knee: "knee", ankle: "ankle", toe: "toe"}.get(owner)
            if slot:
                res.merges.setdefault(f"{side}_{slot}_bone", []).append(b)


def _ankle_position(rig: RigData, chain: List[int]) -> int:
    """First chain bone (after the thigh) whose head is in the lowest 12% of the model.

    Robust to soles below the floor (DAZ conversions) where "nearest to 7%"
    picks coincident helpers.  Falls back to the bone nearest 7% height.
    """
    low = rig.floor + 0.12 * rig.height
    for i in range(2, len(chain)):
        if float(rig.bones[chain[i]].head[2]) <= low:
            return i
    target = rig.floor + 0.07 * rig.height
    return min(range(1, len(chain)), key=lambda i: abs(float(rig.bones[chain[i]].head[2]) - target))


def _toe_bone(rig: RigData, after_ankle: List[int], ankle: int) -> int:
    """First chain bone after the ankle that lies at least 35% of the way to the most forward point.

    That is the ball of the foot (DAZ ``lToe`` rather than ``lMetatarsals`` or
    a toe phalanx); bones before it belong to the ankle.
    """
    if not after_ankle:
        return -1
    ankle_y = float(rig.bones[ankle].head[1])
    ys = np.concatenate([_subtree_heads(rig, b)[:, 1] for b in after_ankle])
    # the foot extends towards -Y normally, towards +Y when the model faces backwards
    sign = -1.0 if (ys.min() - ankle_y) < -(ys.max() - ankle_y) else 1.0
    span = float(np.max((ys - ankle_y) * sign))
    if span < 0.02 * rig.height:  # nothing in front of the ankle
        return -1
    for b in after_ankle:
        if (float(rig.bones[b].head[1]) - ankle_y) * sign / span >= 0.35:
            return b
    return -1


def _assign_root_and_center(rig: RigData, res: TopologyResult) -> None:
    eps = rig.centre_eps()
    fork = res.leg_fork
    fork_bone = rig.bones[fork]
    chain = rig.ancestors(fork)
    roots = [a for a in chain if abs(float(rig.bones[a].head[0])) < eps]
    if roots:
        top = roots[-1]
        if rig.rel_z(top) < 0.05:
            res.put("all_parents_bone", top, "hierarchy root at the floor")
    # centre: unweighted centred ancestor near hip height, else none (generated)
    hip_z = float(fork_bone.head[2])
    for a in chain:
        b = rig.bones[a]
        if abs(float(b.head[0])) < eps and not b.weighted and abs(float(b.head[2]) - hip_z) < 0.1 * rig.height:
            res.put("center_bone", a, "unweighted centred bone at hip height above the leg fork")
            break
    if fork_bone.weighted and abs(float(fork_bone.head[0])) < eps:
        res.put("lower_body_bone", fork, "weighted centred leg fork (diagnosis decides)")


# ---------------------------------------------------------------------------
# spine, neck, head

def spine_chain(rig: RigData, leg_fork: int, arm_fork: int) -> List[int]:
    lca = rig.lca(leg_fork, arm_fork)
    if lca < 0:
        return []
    chain = rig.path_down(lca, arm_fork)
    return _drop_coincident(rig, chain, 0.004 * rig.height)


def neck_chain(rig: RigData, arm_fork: int, max_len: int = 5) -> List[int]:
    eps = rig.centre_eps()
    chain, cur = [], arm_fork
    for _ in range(max_len):
        kids = [c for c in _significant_children(rig, cur) if abs(float(rig.bones[c].head[0])) < eps
                and rig.bones[c].head[2] > rig.bones[arm_fork].head[2] - 0.01 * rig.height]
        if not kids:
            break
        cur = max(kids, key=lambda c: (len(rig.subtree(c)), float(rig.bones[c].head[2])))
        chain.append(cur)
        if len(_significant_children(rig, cur)) >= 3:
            break
    return chain


def _assign_neck_head(rig: RigData, res: TopologyResult) -> None:
    chain = res.neck_chain
    if not chain:
        res.notes.append("neck/head chain not found")
        return
    head = max(chain, key=lambda b: (len(_significant_children(rig, b)), chain.index(b)))
    res.put("head_bone", head, "neck chain bone with most children")
    pre = chain[: chain.index(head)]
    if pre:
        res.put("neck_bone", pre[0], "first centred bone above the chest")
    if len(pre) >= 2 and rig.bones[pre[1]].weighted:
        res.put("neck1_bone", pre[1], "second neck chain bone (weighted)")


def assign_spine(rig: RigData, chain: List[int], neck: int) -> Dict[str, int]:
    """上半身 = first; 上半身2 = bone nearest 0.35 of 上半身→首; below → 上半身1; above → 上半身3/4."""
    out: Dict[str, int] = {}
    if not chain:
        return out
    out["upper_body_bone"] = chain[0]
    rest = chain[1:]
    if not rest:
        return out
    z0 = float(rig.bones[chain[0]].head[2])
    if neck >= 0:
        z1 = float(rig.bones[neck].head[2])
    else:
        z1 = float(rig.bones[chain[-1]].tail[2])
    target = z0 + 0.35 * (z1 - z0)
    k = min(range(len(rest)), key=lambda i: abs(float(rig.bones[rest[i]].head[2]) - target))
    out["upper_body2_bone"] = rest[k]
    below, above = rest[:k], rest[k + 1:]
    if below:
        out["upper_body1_bone"] = below[-1]
    for slot, bone in zip(("upper_body3_bone", "upper_body4_bone"), above):
        out[slot] = bone
    return out


# ---------------------------------------------------------------------------
# arms, hands, fingers

def _arm_chain(rig: RigData, start: int, origin: np.ndarray) -> List[int]:
    chain, cur = [start], start
    if _finger_chains(rig, cur, probe=True) >= 3:
        return chain
    while True:
        kids = _significant_children(rig, cur)
        if not kids:
            break
        cur = max(kids, key=lambda c: float(np.linalg.norm(_subtree_heads(rig, c) - origin, axis=1).max()))
        chain.append(cur)
        if _finger_chains(rig, cur, probe=True) >= 3:
            break
    return chain


def _single_chain(rig: RigData, start: int) -> List[int]:
    chain, cur = [start], start
    while True:
        kids = _significant_children(rig, cur)
        if not kids:
            break
        cur = max(kids, key=lambda c: len(rig.subtree(c)))
        chain.append(cur)
    return chain


#: Finger chains stay within this fraction of the model height from the hand head …
FINGER_REACH = 0.12
#: … or within this fraction of the bone segment leading to the hand (forearm), for short models.
FINGER_REACH_OF_PARENT = 0.85


def _finger_chains(rig: RigData, hand: int, probe: bool = False):
    """Child chains of >= 2 bones that stay close to ``hand`` (fingers, not sleeves or a forearm)."""
    head = rig.bones[hand].head
    parent = rig.bones[hand].parent
    parent_len = float(np.linalg.norm(head - rig.bones[parent].head)) if parent >= 0 else 0.0
    limit = max(FINGER_REACH * rig.height, FINGER_REACH_OF_PARENT * parent_len)
    chains = []
    for c in _significant_children(rig, hand):
        chain = _single_chain(rig, c)
        if len(chain) < 2:
            continue
        if float(np.linalg.norm(rig.heads(chain) - head, axis=1).max()) > limit:
            continue
        chains.append(chain)
    return len(chains) if probe else chains


def _assign_arms(rig: RigData, res: TopologyResult) -> None:
    eps = rig.centre_eps()
    fork = rig.bones[res.arm_fork]
    for c in _significant_children(rig, res.arm_fork):
        pts = _subtree_heads(rig, c)
        if pts[:, 2].min() < rig.floor + 0.4 * rig.height:
            continue
        if pts[:, 0].max() > ARM_REACH * rig.height and pts[:, 0].mean() > eps:
            side = "left"
        elif pts[:, 0].min() < -ARM_REACH * rig.height and pts[:, 0].mean() < -eps:
            side = "right"
        else:
            continue
        if f"{side}_hand_bone" in res.slots:
            continue
        chain = _arm_chain(rig, c, fork.head)
        hand = chain[-1]
        if _finger_chains(rig, hand, probe=True) < 3:
            res.notes.append(f"{side} hand (bone with >=3 finger chains) not found")
            continue
        pre = _drop_coincident(rig, chain[:-1], 0.004 * rig.height)
        res.put(f"{side}_hand_bone", hand, "first arm chain bone with >=3 finger chains")
        if len(pre) >= 3:
            res.put(f"{side}_shoulder_bone", pre[0], "arm chain bone 1")
            res.put(f"{side}_upper_arm_bone", pre[1], "arm chain bone 2")
            res.put(f"{side}_lower_arm_bone", pre[-1], "last arm chain bone before the hand")
            if len(pre) > 3:
                res.merges.setdefault(f"{side}_upper_arm_bone", []).extend(pre[2:-1])
        elif len(pre) == 2:
            res.put(f"{side}_upper_arm_bone", pre[0], "arm chain bone 1 (no shoulder)")
            res.put(f"{side}_lower_arm_bone", pre[1], "arm chain bone 2")
            res.notes.append(f"{side} shoulder not found")
        _assign_fingers(rig, res, side, hand)


def _assign_fingers(rig: RigData, res: TopologyResult, side: str, hand: int) -> None:
    chains = _finger_chains(rig, hand)
    if not chains:
        return
    chains = [ch[1:] if len(ch) >= 4 else ch for ch in chains]  # drop metacarpals
    hand_head = rig.bones[hand].head
    dirs = []
    for ch in chains:
        d = rig.bones[ch[0]].head - hand_head
        n = float(np.linalg.norm(d))
        dirs.append(d / n if n > 1e-9 else d)
    mean_dir = np.mean(dirs, axis=0)
    thumb_i = min(range(len(chains)), key=lambda i: float(np.dot(dirs[i], mean_dir)))
    thumb = chains[thumb_i]
    names = ("thumb_0", "thumb_1", "thumb_2") if len(thumb) >= 3 else ("thumb_1", "thumb_2")
    for slot, b in zip(names, thumb):
        res.put(f"{side}_{slot}", b, "thumb: finger chain deviating most from the mean direction")
    others = [ch for i, ch in enumerate(chains) if i != thumb_i]
    # order index → pinky by how far each finger root lies towards the thumb side of the palm
    axis = mean_dir / (np.linalg.norm(mean_dir) or 1.0)
    thumb_side = rig.bones[thumb[0]].head - hand_head
    thumb_side = thumb_side - axis * float(np.dot(thumb_side, axis))
    thumb_side = thumb_side / (np.linalg.norm(thumb_side) or 1.0)
    others.sort(key=lambda ch: -float(np.dot(rig.bones[ch[0]].head - hand_head, thumb_side)))
    for finger, ch in zip(FINGERS, others):
        for k, b in enumerate(ch[:3], start=1):
            res.put(f"{side}_{finger}_{k}", b, f"{finger}: finger chains ordered by distance from the thumb")


# ---------------------------------------------------------------------------
# eyes, breasts

def _mirror_pairs(rig: RigData, candidates: List[int], tol: float) -> List[Tuple[int, int]]:
    lefts = [b for b in candidates if rig.bones[b].head[0] > tol]
    rights = [b for b in candidates if rig.bones[b].head[0] < -tol]
    pairs = []
    for left in lefts:
        lh = rig.bones[left].head
        for right in rights:
            rh = rig.bones[right].head
            if abs(lh[0] + rh[0]) < tol and abs(lh[1] - rh[1]) < tol and abs(lh[2] - rh[2]) < tol:
                pairs.append((left, right))
    return pairs


def _assign_eyes(rig: RigData, res: TopologyResult, head: int) -> None:
    tol = 0.01 * rig.height
    near = []
    for c in rig.bones[head].children:
        near.append(c)
        near.extend(rig.bones[c].children)
    cands = [b for b in near if rig.bones[b].weighted]
    pairs = _mirror_pairs(rig, cands, tol)
    if not pairs:
        return

    def named(pair):
        return all(_EYE_RE.search(rig.bones[b].name) and not _NOT_EYE_RE.search(rig.bones[b].name)
                   for b in pair)

    pairs = [p for p in pairs if named(p)]
    if not pairs:
        res.notes.append("no eye bones (no mirrored pair with an eye-like name under the head)")
        return
    best = max(pairs, key=lambda p: float(rig.bones[p[0]].head[2] + rig.bones[p[1]].head[2]))
    res.put("left_eye_bone", best[0], "mirrored weighted pair near the head, eye-like name")
    res.put("right_eye_bone", best[1], "mirrored weighted pair near the head, eye-like name")


def _assign_breasts(rig: RigData, res: TopologyResult) -> None:
    tol = 0.015 * rig.height
    owners = list(res.spine_chain) or [res.arm_fork]
    taken = set(res.slots.values())
    cands = []
    for o in owners:
        for c in rig.bones[o].children:
            if c in taken or not rig.subtree_weighted(c):
                continue
            b = rig.bones[c]
            if abs(float(b.head[0])) < rig.centre_eps():
                continue
            if _BREAST_RE.search(b.name) and len(rig.subtree(c)) <= 6:
                cands.append(c)
    pairs = _mirror_pairs(rig, cands, tol)
    if pairs:
        for side, top in zip(("left", "right"), pairs[0]):
            primary = top
            while not rig.bones[primary].weighted and len(_significant_children(rig, primary)) == 1:
                primary = _significant_children(rig, primary)[0]  # skip unweighted wrapper bones
            res.put(f"{side}_breast_bone", primary, "mirrored chest child with a breast-like name")
            extra = [d for d in rig.subtree(primary) if d != primary and rig.bones[d].weighted]
            if extra:
                res.merges.setdefault(f"{side}_breast_bone", []).extend(extra)
