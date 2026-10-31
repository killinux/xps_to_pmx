"""⑨ 体检 (design doc §15.5–§15.6): symptom checks on the MMD model, findings, and the before/after diff.

Symptom checks look at the final weights after ④:

* ``checkup.joint_leak``: around the knees and elbows, vertices of one segment that
  still carry the other segment's weight (they get dragged when the joint bends).
  The stored ② analysis traces the leak back to merged source bones.
* ``checkup.side_leak``: a bone that sits on one side but moves vertices on the
  other side.  Duplicate source names are the known cause.

Everything the stages reported (② checks, ①③④⑧ messages) is turned into
findings too, so the report is one list.  Thresholds were calibrated on the
regression models, the 18-series reference models and rouffe (2026-10-31).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from ..fixes import Fix
from ..rig.limbs import project
from ..spec import BoneSpec

ERROR = "error"
WARNING = "warning"
INFO = "info"

PARTS = ("head", "hair", "trunk", "arm_l", "arm_r", "leg_l", "leg_r", "other", "global")
PART_LABELS = {"head": "头部", "hair": "头发", "trunk": "躯干", "arm_l": "左臂", "arm_r": "右臂", "leg_l": "左腿",
               "leg_r": "右腿", "other": "衣物与其他", "global": "整体"}
STATE_LABELS = {"new": "新出现", "remaining": "仍存在", "fixed": "已修复", "auto_fixed": "已自动修正"}

# -- joint leak --------------------------------------------------------------------
LEAK_WEIGHT = 0.10          # a vertex leaks when it carries at least this much of the other segment …
MIX_WEIGHT = 0.05           # … and also some weight of its own segment (a blend left by a wrong merge),
PURE_FROM = 0.30            # … or lies at least this far (fraction of its segment) from the joint.
#   Vertices owned only by the other segment right next to the joint are left out: on Bunny Ultimate 18 a
#   band just below each knee (t 0.16–0.21) is weighted 100 % to the thigh on purpose; rouffe's wrong
#   merges leave blends that reach t 0.6 (2026-10-31).
DOWN_RANGE = (0.15, 0.90)   # lower segment, as fraction of its length from the joint
UP_RANGE = (0.10, 0.85)     # upper segment, from its start
RADIUS = 0.35               # max distance from the bone axis, fraction of the segment length
LEAK_MIN_VERTICES = 20      # findings need at least this many leaking vertices …
LEAK_MIN_SHARE = 0.05       # … and this share of the region's vertices
TRACE_MIN_SHARE = 0.5       # a merged bone is named as the cause when ≥ this share of it lies across the joint

# -- side leak -----------------------------------------------------------------------
SIDE_MARGIN = 0.02          # centre band ignored on both sides, fraction of model height
SIDE_SHARE = 0.05           # share of a bone's weight on the wrong side
SIDE_MIN_VERTICES = 20

JOINTS = {
    # name: (upper slots, lower slots, start slot, joint slot, end slot)
    "knee": (("thigh_bone", "leg_d_bone"), ("knee_bone", "knee_d_bone"), "thigh_bone", "knee_bone", "ankle_bone"),
    "elbow": (("upper_arm_bone", "arm_twist_bone", "arm_twist1_bone", "arm_twist2_bone", "arm_twist3_bone"),
              ("lower_arm_bone", "wrist_twist_bone", "wrist_twist1_bone", "wrist_twist2_bone", "wrist_twist3_bone"),
              "upper_arm_bone", "lower_arm_bone", "hand_bone"),
}
JOINT_LABELS = {"knee": ("膝", "大腿", "小腿"), "elbow": ("肘", "上臂", "前臂")}


@dataclass
class Finding:
    code: str
    level: str
    text: str
    part: str = "global"
    target: str = ""          # a bone that exists in the current Blender model (for 定位)
    subject: str = ""         # what the finding is about; part of the key
    detail: str = ""
    fix: Optional[Fix] = None
    state: str = "new"        # new | remaining | fixed | auto_fixed

    @property
    def key(self) -> str:
        return f"{self.code}:{self.subject}" if self.subject else self.code


# ---------------------------------------------------------------------------
# parts

def part_of_slot(spec: BoneSpec, slot_id: str) -> str:
    s = spec.get(slot_id)
    if s is None:
        return "global"
    if s.group in ("arm", "finger"):
        return "arm_l" if s.side == "L" else "arm_r" if s.side == "R" else "trunk"
    if s.group in ("leg", "dbone"):
        return "leg_l" if s.side == "L" else "leg_r" if s.side == "R" else "trunk"
    if s.group == "eye" or slot_id in ("head_bone", "neck_bone", "neck1_bone"):
        return "head"
    return "trunk"


def part_of_category(category: str) -> str:
    if category == "hair":
        return "hair"
    if category == "face":
        return "head"
    return "other"


# ---------------------------------------------------------------------------
# joint leak

@dataclass
class JointSpec:
    side: str                 # "left" | "right"
    joint: str                # "knee" | "elbow"
    upper: List[str]          # MMD names of the upper segment's deform bones
    lower: List[str]          # MMD names of the lower segment's deform bones
    a: np.ndarray             # upper segment start
    j: np.ndarray             # the joint
    e: np.ndarray             # lower segment end
    upper_slot: str = ""      # e.g. "left_thigh_bone": where wrongly merged helpers went
    lower_slot: str = ""      # e.g. "left_knee_bone"


@dataclass
class JointLeak:
    spec: JointSpec
    down: int = 0             # lower-segment vertices carrying upper weight
    down_region: int = 0
    down_max: float = 0.0
    up: int = 0               # upper-segment vertices carrying lower weight
    up_region: int = 0
    up_max: float = 0.0

    def direction_flags(self) -> Tuple[bool, bool]:
        def bad(n: int, region: int) -> bool:
            return n >= LEAK_MIN_VERTICES and region > 0 and n / region >= LEAK_MIN_SHARE
        return bad(self.down, self.down_region), bad(self.up, self.up_region)


def joint_specs(spec: BoneSpec, heads: Dict[str, np.ndarray]) -> List[JointSpec]:
    """Knee and elbow definitions for the bones present in ``heads`` (MMD name → head position)."""
    out = []
    for side in ("left", "right"):
        for joint, (upper, lower, start, mid, end) in JOINTS.items():
            names = {k: spec[f"{side}_{k}"].name_j for k in (start, mid, end)}
            if not all(n in heads for n in names.values()):
                continue
            up = [spec[f"{side}_{k}"].name_j for k in upper if spec.get(f"{side}_{k}") is not None]
            lo = [spec[f"{side}_{k}"].name_j for k in lower if spec.get(f"{side}_{k}") is not None]
            out.append(JointSpec(side, joint, [n for n in up if n in heads], [n for n in lo if n in heads],
                                 heads[names[start]], heads[names[mid]], heads[names[end]],
                                 f"{side}_{start}", f"{side}_{mid}"))
    return out


def joint_leaks(positions: np.ndarray, column: Callable[[Sequence[str]], np.ndarray],
                joints: Iterable[JointSpec]) -> List[JointLeak]:
    """``column(names)`` returns the summed per-vertex weight of those bones."""
    pts = np.asarray(positions, float)
    out = []
    for js in joints:
        leak = JointLeak(js)
        upper_w, lower_w = column(js.upper), column(js.lower)
        t_d, r_d = project(pts, js.j, js.e)
        len_d = float(np.linalg.norm(js.e - js.j))
        region = (t_d >= DOWN_RANGE[0]) & (t_d <= DOWN_RANGE[1]) & (r_d <= RADIUS * len_d)
        bad = region & (upper_w >= LEAK_WEIGHT) & ((lower_w >= MIX_WEIGHT) | (t_d >= PURE_FROM))
        leak.down, leak.down_region = int(bad.sum()), int(region.sum())
        leak.down_max = float(upper_w[bad].max()) if bad.any() else 0.0
        t_u, r_u = project(pts, js.a, js.j)
        len_u = float(np.linalg.norm(js.j - js.a))
        region = (t_u >= UP_RANGE[0]) & (t_u <= UP_RANGE[1]) & (r_u <= RADIUS * len_u)
        bad = region & (lower_w >= LEAK_WEIGHT) & ((upper_w >= MIX_WEIGHT) | (t_u <= 1.0 - PURE_FROM))
        leak.up, leak.up_region = int(bad.sum()), int(region.sum())
        leak.up_max = float(lower_w[bad].max()) if bad.any() else 0.0
        out.append(leak)
    return out


def joint_findings(leaks: Iterable[JointLeak], spec: BoneSpec, analysis: Iterable[Dict],
                   user_decided: Iterable[str]) -> List[Finding]:
    """Findings for leaking joints, naming merged source bones that explain them.

    ``analysis`` rows come from ② (:meth:`cause.MergeAnalysis.as_dict`): bone, slot (merge target),
    fractions per segment slot.
    """
    decided = set(user_decided)
    rows = list(analysis)
    out = []
    for leak in leaks:
        js = leak.spec
        down, up = leak.direction_flags()
        label, upper_label, lower_label = JOINT_LABELS[js.joint]
        side = "左" if js.side == "left" else "右"
        part = ("leg_" if js.joint == "knee" else "arm_") + ("l" if js.side == "left" else "r")
        for flagged, direction in ((down, "down"), (up, "up")):
            if not flagged:
                continue
            if direction == "down":
                n, region, wmax = leak.down, leak.down_region, leak.down_max
                where, carried, wrong_slot, right_slot = lower_label, upper_label, js.upper_slot, js.lower_slot
            else:
                n, region, wmax = leak.up, leak.up_region, leak.up_max
                where, carried, wrong_slot, right_slot = upper_label, lower_label, js.lower_slot, js.upper_slot
            culprits = [r for r in rows if r["slot"] == wrong_slot
                        and r.get("fractions", {}).get(right_slot, 0.0) >= TRACE_MIN_SHARE]
            text = f"{side}{label}：{where}上 {n} 个顶点还带着{carried}的权重，弯{label}时会被{carried}扯着走"
            detail = (f"{where}中段 {region} 个顶点里有 {n} 个（{n / max(region, 1):.0%}）带 ≥{LEAK_WEIGHT:.0%} 的"
                      f"{carried}权重，最大 {wmax:.2f}")
            subject = f"{js.side}_{js.joint}_{direction}"
            target = spec[right_slot].name_j
            if culprits:
                for r in culprits:
                    share = r["fractions"][right_slot]
                    fix = Fix("bone", bone=r["bone"], src=r.get("src", r["bone"]), action="merge",
                              slot_id=right_slot, finding=f"checkup.joint_leak:{subject}", origin="checkup",
                              auto=False, note=f"{share:.0%} 的明确权重在{spec[right_slot].name_j}段")
                    why = "（你手动指定过这根骨）" if f"bone:{r['bone']}" in decided else ""
                    out.append(Finding("checkup.joint_leak", ERROR,
                                       f"{text}；原因：{r['bone']} 并入了 {spec[wrong_slot].name_j}{why}",
                                       part, target, f"{subject}:{r['bone']}", detail, fix))
            else:
                out.append(Finding("checkup.joint_leak", WARNING,
                                   f"{text}；不是并入造成的，源模型的权重本身越过了关节，需要你看",
                                   part, target, subject, detail))
    return out


# ---------------------------------------------------------------------------
# side leak

@dataclass
class SideLeak:
    bone: str
    side: float               # +1 left (x > 0), -1 right
    share: float
    vertices: int


def side_leaks(names: Sequence[str], heads: np.ndarray, positions: np.ndarray,
               column: Callable[[int], np.ndarray], height: float) -> List[SideLeak]:
    """Bones off the centre line that carry weight on the other side (``column(i)`` = weight of bone i)."""
    eps = SIDE_MARGIN * height
    x = np.asarray(positions, float)[:, 0]
    out = []
    for i, name in enumerate(names):
        hx = float(heads[i][0])
        if abs(hx) <= eps:
            continue
        w = column(i)
        total = float(w.sum())
        if total <= 0:
            continue
        side = 1.0 if hx > 0 else -1.0
        wrong = (x * side < -eps) & (w > 0)
        share = float(w[wrong].sum()) / total
        if share > SIDE_SHARE and int(wrong.sum()) >= SIDE_MIN_VERTICES:
            out.append(SideLeak(name, side, share, int(wrong.sum())))
    return out


def side_findings(leaks: Iterable[SideLeak], source_of: Dict[str, str], duplicates: Iterable[Dict],
                  part_of: Callable[[str], str]) -> List[Finding]:
    """``source_of``: MMD bone name → original XPS name (its English name); ``duplicates`` rows from ②."""
    by_src = {d.get("src", d["bone"]): d for d in duplicates}
    out = []
    for leak in leaks:
        side, other = ("左", "右") if leak.side > 0 else ("右", "左")
        text = f"{leak.bone} 在{side}侧，却带着{other}侧 {leak.vertices} 个顶点；动它时{other}侧也会跟着动"
        detail = f"{leak.share:.0%} 的权重在{other}侧（中线两侧各 {SIDE_MARGIN:.0%} 身高以外）"
        dup = by_src.get(source_of.get(leak.bone, ""))
        if dup is not None:
            fix = Fix("split_side", bone=dup["bone"], src=dup.get("src", dup["bone"]), twin=dup["twin"],
                      finding=f"checkup.side_leak:{leak.bone}", origin="checkup", auto=False,
                      note=f"把{other}侧的权重拆给 {dup['twin']}")
            out.append(Finding("checkup.side_leak", WARNING,
                               f"{text}；原因：源文件里有同名骨 {dup['twin']}，权重都挂在了这一根上",
                               part_of(leak.bone), leak.bone, leak.bone, detail, fix))
        else:
            out.append(Finding("checkup.side_leak", INFO, f"{text}；可能是跨中线的衣物或饰品，需要你看",
                               part_of(leak.bone), leak.bone, leak.bone, detail))
    return out


# ---------------------------------------------------------------------------
# before / after

def diff_findings(previous: Dict[str, Dict], current: List[Finding]) -> List[Finding]:
    """Mark ``current`` findings new / remaining and append the previous ones that are gone as fixed.

    ``previous`` maps finding key → {"level", "text", "part", "code"} of the last checkup.
    Findings already marked auto_fixed keep that state.
    """
    keys = set()
    for f in current:
        keys.add(f.key)
        if f.state != "auto_fixed":
            f.state = "remaining" if f.key in previous else "new"
    gone = []
    for key, old in previous.items():
        if key in keys or old.get("state") == "fixed" or old.get("level") == INFO:
            continue
        gone.append(Finding(old.get("code", key.split(":", 1)[0]), INFO, old.get("text", key), old.get("part", "global"),
                            "", key.split(":", 1)[1] if ":" in key else "", "", None, "fixed"))
    return current + gone


def sort_findings(findings: List[Finding]) -> List[Finding]:
    level = {ERROR: 0, WARNING: 1, INFO: 2}
    state = {"new": 0, "remaining": 1, "auto_fixed": 2, "fixed": 3}
    return sorted(findings, key=lambda f: (state.get(f.state, 9) >= 2, level.get(f.level, 9),
                                           PARTS.index(f.part) if f.part in PARTS else 99, state.get(f.state, 9)))


def summarize(findings: Iterable[Dict]) -> Dict[str, int]:
    out = {ERROR: 0, WARNING: 0, INFO: 0, "fixed": 0, "auto_fixed": 0}
    for f in findings:
        if f.get("state") == "fixed":
            out["fixed"] += 1
        elif f.get("state") == "auto_fixed":
            out["auto_fixed"] += 1
        else:
            out[f.get("level", INFO)] += 1
    return out

