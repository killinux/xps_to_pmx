"""⑨ 体检 · 姿势测试 (design doc §16): bend the MMD model into test poses and measure the mesh.

Poses are evaluated the way MMD evaluates them: bone hierarchy, rotation grants (付与) as a
fraction of the grant source's rotation, linear blend skinning.  Blender's constraints are not
used: mmd_tools previews partial grants with TRANSFORM constraints whose result depends on the
bone rolls (on our exports 左手捩2/3 turned 63°/83° instead of 45°/67.5° in Blender, while MMD
is unaffected).  For every test without partial grants this evaluation and Blender's agree to
1e-7 of the model height (2026-10-31).

Three kinds of problems are measured:

* ``follow``: vertices well inside a body part that should turn with the posed bone but lag
  behind, or should stay where they are but get dragged along (wrong weights, broken grants);
* ``twist``: the forearm or upper arm collapsing towards its axis when the twist bone turns;
* ``crack``: vertices that sit on top of each other at rest (seams between meshes, UV splits)
  coming apart.

Body parts are found from the MMD bones: every vertex belongs to the nearest limb or trunk
segment.  Vertices mostly weighted to bones outside the MMD standard skeleton (hair, skirts,
accessories) are left out of the body parts, because they rightly move differently.
Thresholds were calibrated on 10 18-series reference models, the 4 regression models and rouffe.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

import numpy as np

from ..fixes import Fix
from ..pose import axis_angle, rigid
from .checkup import WARNING, Finding

FORWARD = np.array([0.0, -1.0, 0.0])
UP = np.array([0.0, 0.0, 1.0])

# -- thresholds (calibrated 2026-10-31, see the module docstring) --------------------------------
FOLLOW_SHARE = 0.20      # a vertex lags (or is dragged) by at least this share of the posed bone's motion …
FOLLOW_MIN_DEV = 0.010   # … and by at least this much (fraction of the model height);
LEVER_MIN = 0.020        # vertices this close to the pivot (fraction of the height) move too little to judge
FOREIGN_MAX = 0.5        # vertices with at least this share of weight on non-standard bones are not body
FOLLOW_MIN_VERTICES = 10  # a finding needs this many flagged vertices …
FOLLOW_MIN_SHARE = 0.03  # … and this share of the body part's vertices
SIDE_MIN_VERTICES = 20   # the other side has no natural size: a count alone
TWIST_RATIO = 0.72       # collapsed: distance to the axis below this ratio (a 50/50 blend of 0° and 90° gives 0.707)
TWIST_MIN_VERTICES = 10
CRACK_GAP = 0.0015       # rest-coincident vertices this far apart in a pose (fraction of the height) crack
CRACK_MIN_PAIRS = 3
COINCIDENT = 1e-5        # "on top of each other" at rest, fraction of the height
BELLY_LIMIT = 0.035      # belly dragged by the hips: the 18-series reference models reach 3.4 % (Bunny Ultimate 18)
SIDE_MARGIN = 0.05       # the other side starts this far from the centre line (fraction of the height)
MAX_VIEW_VERTICES = 4000


# ---------------------------------------------------------------------------
# rig and evaluation

@dataclass
class PoseBone:
    name: str
    parent: int
    head: np.ndarray
    grant: int = -1          # rotation grant source (付与親), -1 for none
    rate: float = 0.0        # grant rate (付与率)


class PoseRig:
    """Bones with grants and the skin, in armature space (Blender axes: Z up, facing -Y, left = +X)."""

    def __init__(self, bones: Sequence[PoseBone], positions: np.ndarray, skin_bones: np.ndarray,
                 skin_weights: np.ndarray, body_names: Iterable[str]):
        self.bones = list(bones)
        self.by_name = {b.name: i for i, b in enumerate(self.bones)}
        self.positions = np.asarray(positions, float)
        self.skin_bones = np.asarray(skin_bones, np.int64)
        self.skin_weights = np.asarray(skin_weights, float)
        body = set(body_names)
        self.is_body = np.array([b.name in body for b in self.bones], bool)
        n = len(self.positions)
        z = self.positions[:, 2] if n else np.zeros(1)
        self.floor = float(z.min()) if n else 0.0
        self.height = max(float(z.max()) - self.floor, 1e-6) if n else 1.0
        valid = (self.skin_bones >= 0) & (self.skin_weights > 0)
        safe = np.where(valid, self.skin_bones, 0)
        w = np.where(valid, self.skin_weights, 0.0)
        total = w.sum(axis=1)
        foreign = np.where(valid & ~self.is_body[safe], w, 0.0).sum(axis=1) if len(self.bones) else np.zeros(n)
        self.weighted = total > 1e-9
        self.foreign = np.where(self.weighted, foreign / np.maximum(total, 1e-12), 1.0)
        self._pairs: Optional[np.ndarray] = None

    def head(self, name: str) -> Optional[np.ndarray]:
        i = self.by_name.get(name)
        return None if i is None else self.bones[i].head

    def coincident_pairs(self) -> np.ndarray:
        """Index pairs (i < j) of vertices at the same rest position."""
        if self._pairs is None:
            if len(self.positions) < 2:
                self._pairs = np.zeros((0, 2), np.int64)
            else:
                q = np.round(self.positions / (COINCIDENT * self.height)).astype(np.int64)
                order = np.lexsort((q[:, 2], q[:, 1], q[:, 0]))
                qs = q[order]
                same = np.all(qs[1:] == qs[:-1], axis=1)
                self._pairs = np.stack([order[:-1][same], order[1:][same]], axis=1)
        return self._pairs


def fraction(rot: np.ndarray, rate: float) -> np.ndarray:
    """``rate`` times the rotation ``rot`` (same axis, scaled angle; negative rates turn backwards)."""
    c = max(-1.0, min(1.0, (float(np.trace(rot)) - 1.0) / 2.0))
    angle = math.acos(c)
    if angle < 1e-9 or rate == 1.0:
        return np.eye(3) if angle < 1e-9 else rot
    axis = np.array([rot[2, 1] - rot[1, 2], rot[0, 2] - rot[2, 0], rot[1, 0] - rot[0, 1]])
    if np.linalg.norm(axis) < 1e-12:  # 180°: the axis is the eigenvector of the symmetric part with eigenvalue 1
        w, v = np.linalg.eigh((rot + rot.T) / 2.0)
        axis = v[:, int(np.argmax(w))]
    return axis_angle(axis, rate * angle)


def skin_matrices(rig: PoseRig, local: Dict[int, np.ndarray]) -> np.ndarray:
    """Per-bone 4×4 matrices taking rest positions to posed positions; ``local`` = bone → 3×3 rotation."""
    n = len(rig.bones)
    eff: List[Optional[np.ndarray]] = [None] * n
    out: List[Optional[np.ndarray]] = [None] * n

    def rotation(i: int, seen: Set[int]) -> np.ndarray:
        if eff[i] is not None:
            return eff[i]
        rot = local.get(i, np.eye(3))
        b = rig.bones[i]
        if 0 <= b.grant < n and b.grant not in seen and b.rate != 0.0:
            rot = fraction(rotation(b.grant, seen | {i}), b.rate) @ rot
        eff[i] = rot
        return rot

    def matrix(i: int, depth: int) -> np.ndarray:
        if out[i] is not None:
            return out[i]
        p = rig.bones[i].parent
        parent = matrix(p, depth + 1) if 0 <= p < n and depth < n else np.eye(4)
        out[i] = parent @ rigid(rotation(i, {i}), rig.bones[i].head)
        return out[i]

    return np.stack([matrix(i, 0) for i in range(n)]) if n else np.zeros((0, 4, 4))


def deform(rig: PoseRig, mats: np.ndarray) -> np.ndarray:
    """Linear blend skinning with normalised weights; unweighted vertices stay at rest."""
    pos = rig.positions
    out = np.zeros_like(pos)
    total = np.zeros(len(pos))
    for k in range(rig.skin_bones.shape[1]):
        b = rig.skin_bones[:, k]
        w = rig.skin_weights[:, k]
        valid = (b >= 0) & (w > 0)
        if not valid.any():
            continue
        m = mats[np.where(valid, b, 0)]
        p = np.einsum("nij,nj->ni", m[:, :3, :3], pos) + m[:, :3, 3]
        ww = np.where(valid, w, 0.0)
        out += p * ww[:, None]
        total += ww
    moved = total > 1e-12
    out[moved] /= total[moved, None]
    out[~moved] = pos[~moved]
    return out


# ---------------------------------------------------------------------------
# body parts

#: segment id → (start bone, end bone, part); "L"/"R" segments exist for both sides.
LIMBS = {
    "thigh": ("足", "ひざ", "leg"), "shin": ("ひざ", "足首", "leg"), "foot": ("足首", "つま先", "leg"),
    "shoulder": ("肩", "腕", "arm"), "upperarm": ("腕", "ひじ", "arm"), "forearm": ("ひじ", "手首", "arm"),
    "hand": ("手首", "中指1", "arm"),
}
SEGMENT_LABELS = {"thigh": "大腿", "shin": "小腿", "foot": "脚", "shoulder": "肩", "upperarm": "上臂",
                  "forearm": "前臂", "hand": "手", "pelvis": "胯部", "spine": "躯干", "neck": "脖子",
                  "head": "头部"}


@dataclass
class Segment:
    id: str                  # e.g. "shin_L", "spine"
    a: np.ndarray
    b: np.ndarray
    part: str                # checkup part: leg_l, arm_r, trunk, head
    label: str

    @property
    def length(self) -> float:
        return float(np.linalg.norm(self.b - self.a))


def body_segments(rig: PoseRig) -> List[Segment]:
    out = []
    for side, prefix in (("L", "左"), ("R", "右")):
        for sid, (start, end, part) in LIMBS.items():
            a, b = rig.head(prefix + start), rig.head(prefix + end)
            if a is None:
                continue
            if b is None and sid == "hand":
                elbow = rig.head(prefix + "ひじ")
                b = a + (a - elbow) * 0.45 if elbow is not None else None
            if b is None and sid == "foot":
                b = rig.head(prefix + "足先EX")
            if b is None or np.linalg.norm(b - a) < 1e-6:
                continue
            label = ("左" if side == "L" else "右") + SEGMENT_LABELS[sid]
            out.append(Segment(f"{sid}_{side}", a, b, f"{part}_{side.lower()}", label))
    waist, neck, head = rig.head("上半身"), rig.head("首"), rig.head("頭")
    hips = [rig.head(p + "足") for p in "左右"]
    if waist is not None and all(h is not None for h in hips):
        out.append(Segment("pelvis", waist, (hips[0] + hips[1]) / 2.0, "trunk", "胯部"))
    if waist is not None and neck is not None:
        out.append(Segment("spine", waist, neck, "trunk", "躯干"))
    if neck is not None and head is not None:
        out.append(Segment("neck", neck, head, "head", "脖子"))
    if head is not None:
        top = rig.floor + rig.height
        if top - head[2] > 1e-6:
            out.append(Segment("head", head, np.array([head[0], head[1], top]), "head", "头部"))
    return out


def project(points: np.ndarray, a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    ab = b - a
    t = ((points - a) @ ab) / max(float(ab @ ab), 1e-12)
    closest = a + np.clip(t, 0.0, 1.0)[:, None] * ab
    return t, np.linalg.norm(points - closest, axis=1)


@dataclass
class BodyMap:
    """Nearest body segment of every vertex, with the position along it and the distance to it."""

    segments: List[Segment]
    owner: np.ndarray        # (N,) segment index, -1 when there are no segments
    t: np.ndarray
    r: np.ndarray            # distance to the segment / its length
    body: np.ndarray         # (N,) vertex counts as body (not mostly weighted to hair/cloth bones)

    def index(self, sid: str) -> int:
        return next((i for i, s in enumerate(self.segments) if s.id == sid), -1)

    def region(self, sid: str, t0: float, t1: float, rmax: float = 0.45, body_only: bool = True) -> np.ndarray:
        i = self.index(sid)
        if i < 0:
            return np.zeros(len(self.owner), bool)
        m = (self.owner == i) & (self.t >= t0) & (self.t <= t1) & (self.r <= rmax)
        return m & self.body if body_only else m


def body_map(rig: PoseRig) -> BodyMap:
    segs = body_segments(rig)
    n = len(rig.positions)
    if not segs or not n:
        z = np.zeros(n)
        return BodyMap(segs, np.full(n, -1), z, z, np.zeros(n, bool))
    ts, ds = zip(*(project(rig.positions, s.a, s.b) for s in segs))
    d = np.stack(ds, axis=1)
    owner = d.argmin(axis=1)
    rows = np.arange(n)
    t = np.stack(ts, axis=1)[rows, owner]
    lengths = np.array([max(s.length, 1e-9) for s in segs])
    r = d[rows, owner] / lengths[owner]
    body = rig.weighted & (rig.foreign < FOREIGN_MAX)
    return BodyMap(segs, owner, t, r, body)


# ---------------------------------------------------------------------------
# tests

@dataclass
class Region:
    label: str
    expect: str              # "move" (turn with the posed bone) | "stay"
    segments: Tuple[Tuple[str, float, float], ...] = ()   # (segment id, t0, t1)
    other_side: str = ""     # "L" / "R": everything on that side above the waist, cloth included
    limit: float = 0.0       # > 0: an issue here is quiet (measured, not reported) unless it deviates this much


@dataclass
class PoseTest:
    id: str                  # "knee_L"
    label: str               # "左膝弯曲 90°"
    part: str
    bone: str                # MMD bone that is turned
    axis: np.ndarray
    angle: float             # degrees
    regions: List[Region] = field(default_factory=list)
    twist: str = ""          # segment checked for collapse, e.g. "forearm_L"
    view: Tuple[float, float, float] = (0.0, -1.0, 0.0)   # direction the camera looks from (towards the model)

    def rotation(self) -> np.ndarray:
        return axis_angle(self.axis, math.radians(self.angle))


def build_tests(rig: PoseRig) -> List[PoseTest]:
    """The test poses whose bones exist (design doc §16.2)."""
    out: List[PoseTest] = []
    for side, prefix, s in (("L", "左", 1.0), ("R", "右", -1.0)):
        part_leg, part_arm = f"leg_{side.lower()}", f"arm_{side.lower()}"
        other = "R" if side == "L" else "L"
        if all(rig.head(prefix + n) is not None for n in ("足", "ひざ", "足首")):
            out.append(PoseTest(f"knee_{side}", f"{prefix}膝弯曲 90°", part_leg, prefix + "ひざ", np.array([1.0, 0, 0]), 90,
                                [Region("小腿", "move", ((f"shin_{side}", 0.3, 0.9),)),
                                 Region("大腿", "stay", ((f"thigh_{side}", 0.1, 0.6),))],
                                view=(s, 0.0, 0.0)))
        sh, el, wr = (rig.head(prefix + n) for n in ("腕", "ひじ", "手首"))
        if sh is None or el is None or wr is None:
            continue
        fore = (wr - el) / max(float(np.linalg.norm(wr - el)), 1e-9)
        upper = (el - sh) / max(float(np.linalg.norm(el - sh)), 1e-9)
        out.append(PoseTest(f"elbow_{side}", f"{prefix}肘弯曲 90°", part_arm, prefix + "ひじ", np.cross(fore, FORWARD), 90,
                            [Region("前臂", "move", ((f"forearm_{side}", 0.3, 0.9),)),
                             Region("上臂", "stay", ((f"upperarm_{side}", 0.1, 0.6),))],
                            view=(0.0, 0.0, 1.0)))
        out.append(PoseTest(f"raise_{side}", f"{prefix}臂上抬 90°", part_arm, prefix + "腕", np.array([0.0, -s, 0.0]), 90,
                            [Region("手臂", "move", ((f"upperarm_{side}", 0.4, 1.0), (f"forearm_{side}", 0.0, 0.9))),
                             Region("胸口", "stay", (("spine", 0.3, 0.8),)),
                             Region("另一只手臂", "stay", ((f"upperarm_{other}", 0.0, 1.0), (f"forearm_{other}", 0.0, 1.0)))],
                            view=(0.0, -1.0, 0.0)))
        if rig.head(prefix + "手捩") is not None:
            out.append(PoseTest(f"twist_{side}", f"{prefix}手腕扭转 90°", part_arm, prefix + "手捩", fore, 90,
                                [Region("手", "move", ((f"hand_{side}", 0.2, 1.0),)),
                                 Region("上臂", "stay", ((f"upperarm_{side}", 0.2, 0.9),))],
                                twist=f"forearm_{side}", view=(0.0, -1.0, 0.0)))
        if rig.head(prefix + "腕捩") is not None:
            out.append(PoseTest(f"armtwist_{side}", f"{prefix}上臂扭转 90°", part_arm, prefix + "腕捩", upper, 90,
                                [Region("前臂", "move", ((f"forearm_{side}", 0.2, 0.9),)),
                                 Region("胸口", "stay", (("spine", 0.3, 0.8),))],
                                twist=f"upperarm_{side}", view=(0.0, -1.0, 0.0)))
        if rig.head(prefix + "肩") is not None:
            out.append(PoseTest(f"shrug_{side}", f"{prefix}肩上耸 25°", part_arm, prefix + "肩", np.array([0.0, -s, 0.0]), 25,
                                [Region("手臂", "move", ((f"upperarm_{side}", 0.3, 0.9),)),
                                 Region("头部", "stay", (("head", 0.2, 1.0),)),
                                 Region("另一侧", "stay", other_side=other)],
                                view=(0.0, 1.0, 0.0)))
    belly = belly_start(rig)
    if rig.head("下半身") is not None:
        out.append(PoseTest("hip_twist", "下半身扭转 30°", "trunk", "下半身", UP.copy(), 30,
                            [Region("大腿", "move", (("thigh_L", 0.25, 0.75), ("thigh_R", 0.25, 0.75))),
                             Region("腹部", "stay", (("spine", belly, 0.45),), limit=BELLY_LIMIT),
                             Region("胸口", "stay", (("spine", 0.45, 0.85),))],
                            view=(0.0, -1.0, 0.0)))
    if rig.head("上半身") is not None:
        out.append(PoseTest("waist_bend", "上半身前屈 45°", "trunk", "上半身", np.array([1.0, 0, 0]), 45,
                            [Region("腹部", "move", (("spine", belly, 0.5),), limit=BELLY_LIMIT),
                             Region("胸口", "move", (("spine", 0.5, 0.9),)),
                             Region("大腿", "stay", (("thigh_L", 0.2, 0.8), ("thigh_R", 0.2, 0.8)))],
                            view=(1.0, 0.0, 0.0)))
    if rig.head("頭") is not None:
        out.append(PoseTest("head_turn", "头转向 60°", "head", "頭", UP.copy(), 60,
                            [Region("头部", "move", (("head", 0.2, 0.9),)),
                             Region("胸口", "stay", (("spine", 0.3, 0.85),))],
                            view=(0.0, -1.0, 0.0)))
    return out


def belly_start(rig: PoseRig) -> float:
    """Where the belly region starts on the spine (waist → neck): 2 L above the hip joints.

    L is the height from the hip joints (足) to the waist (上半身).  The 18-series reference models put
    下半身 weight up to 1.75 L (lower_body.HIGH_T) and the belly between waist and 1.75 L follows the hips
    on purpose: Bunny, Czern and Emilie drag 250–1700 vertices there in a 30° hip twist (2026-10-31).
    """
    waist, neck = rig.head("上半身"), rig.head("首")
    hips = [rig.head(p + "足") for p in "左右"]
    if waist is None or neck is None or any(h is None for h in hips):
        return 0.3
    lift = waist[2] - (hips[0][2] + hips[1][2]) / 2.0
    return float(np.clip(lift / max(neck[2] - waist[2], 1e-6), 0.12, 0.45))


def find_test(rig: PoseRig, test_id: str) -> Optional[PoseTest]:
    return next((t for t in build_tests(rig) if t.id == test_id), None)


def posed_positions(rig: PoseRig, test: PoseTest) -> np.ndarray:
    i = rig.by_name[test.bone]
    return deform(rig, skin_matrices(rig, {i: test.rotation()}))


# ---------------------------------------------------------------------------
# measurements

@dataclass
class PoseIssue:
    test: PoseTest
    kind: str                # "follow" | "twist" | "crack"
    region: str              # label of the body part
    expect: str = ""         # "move" | "stay" for follow issues
    vertices: np.ndarray = field(default_factory=lambda: np.zeros(0, np.int64))
    total: int = 0           # vertices in the body part
    worst: float = 0.0       # follow: largest deviation, crack: widest gap (model units); twist: smallest ratio
    culprits: Dict[str, float] = field(default_factory=dict)   # bone → share of the weight that misbehaves
    part: str = ""
    segment: str = ""
    quiet: bool = False      # measured but within what the reference models do (see Region.limit)


def region_mask(rig: PoseRig, bm: BodyMap, region: Region) -> np.ndarray:
    if region.other_side:
        s = 1.0 if region.other_side == "L" else -1.0
        waist = rig.head("上半身")
        z0 = waist[2] if waist is not None else rig.floor + 0.5 * rig.height
        return rig.weighted & (rig.positions[:, 0] * s > SIDE_MARGIN * rig.height) & (rig.positions[:, 2] > z0)
    m = np.zeros(len(rig.positions), bool)
    for sid, t0, t1 in region.segments:
        m |= bm.region(sid, t0, t1)
    return m


def follow_issue(rig: PoseRig, test: PoseTest, region: Region, mask: np.ndarray, mats: np.ndarray,
                 posed: np.ndarray) -> Optional[PoseIssue]:
    if not mask.any():
        return None
    moving = mats[rig.by_name[test.bone]]
    idx = np.nonzero(mask)[0]
    p, q = rig.positions[idx], posed[idx]
    full = p @ moving[:3, :3].T + moving[:3, 3]
    expected = full if region.expect == "move" else p
    dev = np.linalg.norm(q - expected, axis=1)
    lever = np.linalg.norm(full - p, axis=1)
    h = rig.height
    judged = lever >= LEVER_MIN * h
    share = np.where(judged, dev / np.maximum(lever, 1e-12), 0.0)
    bad = judged & (share >= FOLLOW_SHARE) & (dev >= FOLLOW_MIN_DEV * h)
    count = int(bad.sum())
    if region.other_side:
        if count < SIDE_MIN_VERTICES:
            return None
    elif count < FOLLOW_MIN_VERTICES or count < FOLLOW_MIN_SHARE * len(idx):
        return None
    flagged = idx[bad]
    worst = float(dev[bad].max())
    return PoseIssue(test, "follow", region.label, region.expect, flagged, len(idx), worst,
                     culprits(rig, flagged, mats, moving if region.expect == "move" else np.eye(4)), test.part,
                     quiet=bool(region.limit) and worst < region.limit * h)


def culprits(rig: PoseRig, vertices: np.ndarray, mats: np.ndarray, expected: np.ndarray) -> Dict[str, float]:
    """Bones whose weight moves the flagged vertices differently from ``expected``, by share of that weight."""
    tally: Dict[int, float] = {}
    p = rig.positions[vertices]
    want = p @ expected[:3, :3].T + expected[:3, 3]
    for k in range(rig.skin_bones.shape[1]):
        b = rig.skin_bones[vertices, k]
        w = rig.skin_weights[vertices, k]
        valid = (b >= 0) & (w > 0)
        if not valid.any():
            continue
        m = mats[np.where(valid, b, 0)]
        got = np.einsum("nij,nj->ni", m[:, :3, :3], p) + m[:, :3, 3]
        off = valid & (np.linalg.norm(got - want, axis=1) > 0.5 * FOLLOW_MIN_DEV * rig.height)
        for bone, weight in zip(b[off], w[off]):
            tally[int(bone)] = tally.get(int(bone), 0.0) + float(weight)
    total = sum(tally.values())
    if total <= 0:
        return {}
    ranked = sorted(tally.items(), key=lambda kv: -kv[1])
    return {rig.bones[i].name: v / total for i, v in ranked if v / total >= 0.05}


def twist_issue(rig: PoseRig, bm: BodyMap, test: PoseTest, posed: np.ndarray) -> Optional[PoseIssue]:
    i = bm.index(test.twist)
    if i < 0:
        return None
    seg = bm.segments[i]
    mask = bm.region(test.twist, 0.4, 1.0, rmax=0.35)
    if not mask.any():
        return None
    u = (seg.b - seg.a) / seg.length

    def radial(points: np.ndarray) -> np.ndarray:
        v = points - seg.a
        return np.linalg.norm(v - np.outer(v @ u, u), axis=1)
    idx = np.nonzero(mask)[0]
    r0, r1 = radial(rig.positions[idx]), radial(posed[idx])
    judged = r0 > 0.4 * float(np.median(r0))
    ratio = np.where(judged, r1 / np.maximum(r0, 1e-12), 1.0)
    bad = judged & (ratio < TWIST_RATIO)
    if int(bad.sum()) < TWIST_MIN_VERTICES:
        return None
    return PoseIssue(test, "twist", seg.label, "", idx[bad], int(judged.sum()), float(ratio[bad].min()), {},
                     test.part, seg.id)


def run_tests(rig: PoseRig, tests: Optional[Sequence[PoseTest]] = None,
              bm: Optional[BodyMap] = None) -> List[PoseIssue]:
    """Pose the model in every test and collect follow, twist and crack issues (quiet ones included)."""
    tests = build_tests(rig) if tests is None else list(tests)
    bm = body_map(rig) if bm is None else bm
    pairs = rig.coincident_pairs()
    gap = np.zeros(len(pairs))
    gap_test: List[Optional[PoseTest]] = [None] * len(pairs)
    out: List[PoseIssue] = []
    for test in tests:
        mats = skin_matrices(rig, {rig.by_name[test.bone]: test.rotation()})
        posed = deform(rig, mats)
        for region in test.regions:
            issue = follow_issue(rig, test, region, region_mask(rig, bm, region), mats, posed)
            if issue is not None:
                out.append(issue)
        if test.twist:
            issue = twist_issue(rig, bm, test, posed)
            if issue is not None:
                out.append(issue)
        if len(pairs):
            g = np.linalg.norm(posed[pairs[:, 0]] - posed[pairs[:, 1]], axis=1)
            wider = g > gap
            gap[wider] = g[wider]
            for k in np.nonzero(wider)[0]:
                gap_test[k] = test
    out += crack_issues(rig, bm, pairs, gap, gap_test)
    return out


def crack_issues(rig: PoseRig, bm: BodyMap, pairs: np.ndarray, gap: np.ndarray,
                 gap_test: Sequence[Optional[PoseTest]]) -> List[PoseIssue]:
    """Seams that open, grouped by the body segment they lie on (each reported with its worst test)."""
    if not len(pairs):
        return []
    bad = np.nonzero(gap > CRACK_GAP * rig.height)[0]
    groups: Dict[int, List[int]] = {}
    for k in bad:
        groups.setdefault(int(bm.owner[pairs[k, 0]]), []).append(int(k))
    out = []
    for seg_index, ks in groups.items():
        if len(ks) < CRACK_MIN_PAIRS:
            continue
        worst = max(ks, key=lambda k: gap[k])
        seg = bm.segments[seg_index] if seg_index >= 0 else None
        verts = np.unique(pairs[ks].reshape(-1))
        test = gap_test[worst]
        out.append(PoseIssue(test, "crack", seg.label if seg else "", "", verts, len(ks), float(gap[worst]), {},
                             seg.part if seg else test.part, seg.id if seg else ""))
    return out


# ---------------------------------------------------------------------------
# views (what 定位 / 看图 show)

def view_rotation(rig: PoseRig, view: Dict) -> Tuple[Optional[int], np.ndarray]:
    """Bone index and rotation of a view: a test pose (``"test"``) or one bone turned (``"bone"``)."""
    if view.get("test"):
        test = find_test(rig, view["test"])
        if test is None or test.bone not in rig.by_name:
            return None, np.eye(3)
        return rig.by_name[test.bone], test.rotation()
    bone = view.get("bone", "")
    if bone not in rig.by_name:
        return None, np.eye(3)
    return rig.by_name[bone], axis_angle(view.get("axis", (0.0, -1.0, 0.0)), math.radians(view.get("angle", 0.0)))


def view_positions(rig: PoseRig, view: Dict) -> np.ndarray:
    """Vertex positions in the view's pose (the rest pose when the view's bone is missing)."""
    bone, rot = view_rotation(rig, view)
    if bone is None:
        return rig.positions.copy()
    return deform(rig, skin_matrices(rig, {bone: rot}))


def make_view(rig: PoseRig, vertices: Sequence[int], test: Optional[PoseTest] = None, bone: str = "",
              axis: Sequence[float] = (0.0, -1.0, 0.0), angle: float = 0.0,
              direction: Optional[Sequence[float]] = None) -> Dict:
    """What 定位 and 看图 show: the pose, the vertices to select or mark, and the framing (armature space).

    The framing is stored so that a later render of the same finding (after a fix) shows the same spot.
    """
    verts = np.unique(np.asarray(vertices, np.int64))
    if len(verts) > MAX_VIEW_VERTICES:
        verts = verts[np.linspace(0, len(verts) - 1, MAX_VIEW_VERTICES).astype(np.int64)]
    if test is not None:
        view: Dict = {"test": test.id}
        look = test.view if direction is None else direction
    else:
        view = {"test": "", "bone": bone, "axis": [float(a) for a in axis], "angle": float(angle)}
        look = direction if direction is not None else (0.0, -1.0, 0.0)
    pts = view_positions(rig, view)[verts] if len(verts) else rig.positions[:0]
    if len(pts):
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        focus = (lo + hi) / 2.0
        size = float(np.clip(1.6 * float((hi - lo).max()) + 0.08 * rig.height, 0.15 * rig.height, rig.height))
    else:
        focus, size = rig.positions.mean(axis=0) if len(rig.positions) else np.zeros(3), rig.height
    view.update({"vertices": [int(v) for v in verts], "focus": [round(float(c), 5) for c in focus],
                 "size": round(size, 5), "dir": [float(c) for c in look]})
    return view


def issue_view(rig: PoseRig, issue: PoseIssue) -> Dict:
    return make_view(rig, issue.vertices, issue.test)


# ---------------------------------------------------------------------------
# findings

def length_text(value: float) -> str:
    return f"{value * 100:.0f} cm" if value >= 0.01 else f"{value * 1000:.0f} mm"


def _names(culprits: Dict[str, float], source_of: Dict[str, str], limit: int = 3) -> str:
    out = []
    for name in list(culprits)[:limit]:
        src = source_of.get(name, "")
        out.append(f"{name}（{src}）" if src and src != name else name)
    return "、".join(out)


def top_bones(rig: PoseRig, vertices: np.ndarray, limit: int = 3) -> Dict[str, float]:
    """Bones carrying most of the weight of ``vertices``, by share."""
    tally: Dict[int, float] = {}
    for k in range(rig.skin_bones.shape[1]):
        b, w = rig.skin_bones[vertices, k], rig.skin_weights[vertices, k]
        for bone, weight in zip(b[(b >= 0) & (w > 0)], w[(b >= 0) & (w > 0)]):
            tally[int(bone)] = tally.get(int(bone), 0.0) + float(weight)
    total = sum(tally.values()) or 1.0
    ranked = sorted(tally.items(), key=lambda kv: -kv[1])[:limit]
    return {rig.bones[i].name: v / total for i, v in ranked}


def issue_finding(rig: PoseRig, issue: PoseIssue, source_of: Dict[str, str], duplicates: Iterable[Dict]):
    """The checkup finding of one issue.  A culprit with a duplicate source name gets the split fix."""
    test, n = issue.test, len(issue.vertices)
    view = issue_view(rig, issue)
    if issue.kind == "follow":
        if issue.expect == "move":
            text = f"{test.label}时，{issue.region}有 {n} 个顶点跟不上，最多差约 {length_text(issue.worst)}"
        else:
            text = f"{test.label}时，{issue.region}有 {n} 个顶点被带着动，最多约 {length_text(issue.worst)}"
        detail = (f"{issue.region}共 {issue.total} 个顶点，其中 {n} 个偏离了这次转动的 {FOLLOW_SHARE:.0%} 以上"
                  if not region_of(test, issue.region).other_side else
                  f"另一侧有 {n} 个顶点偏离了这次转动的 {FOLLOW_SHARE:.0%} 以上")
        fix = None
        by_src = {d.get("src", d["bone"]): d for d in duplicates}
        for name in issue.culprits:
            dup = by_src.get(source_of.get(name, ""))
            if dup is not None:
                fix = Fix("split_side", bone=dup["bone"], src=dup.get("src", dup["bone"]), twin=dup["twin"],
                          finding=f"pose.follow:{test.id}:{issue.region}", origin="checkup", auto=False,
                          note=f"把另一侧的权重拆给 {dup['twin']}")
                text += f"；原因：源文件里有同名骨 {dup['twin']}，权重都挂在了 {name} 上"
                break
        if fix is None and issue.culprits:
            text += f"；它们带着 {_names(issue.culprits, source_of)} 的权重，需要你看"
        return Finding("pose.follow", WARNING, text, issue.part, "", f"{test.id}:{issue.region}", detail, fix,
                       view=view)
    if issue.kind == "twist":
        bones = top_bones(rig, issue.vertices)
        text = (f"{test.label}时，{issue.region}有 {n} 个顶点向骨轴塌陷，最细处只剩 {issue.worst:.0%}（像拧糖纸）")
        detail = (f"塌陷的顶点主要挂在 {_names(bones, source_of)} 上：一部分权重不转、一部分整个转过去，"
                  f"中间没有逐段过渡的扭转权重")
        return Finding("pose.twist", WARNING, text, issue.part, "", test.id, detail, None, view=view)
    text = f"{test.label}时，{issue.region}有 {issue.total} 处接缝裂开，最宽约 {length_text(issue.worst)}"
    detail = "同一位置有两个顶点（网格之间或 UV 接缝），它们的权重不一样，动起来就分开了；多半是源模型如此"
    return Finding("pose.crack", WARNING, text, issue.part, "", issue.segment or test.id, detail, None, view=view)


def region_of(test: PoseTest, label: str) -> Region:
    return next((r for r in test.regions if r.label == label), Region(label, "stay"))
