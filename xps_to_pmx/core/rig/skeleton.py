"""Stage ④ plan: the MMD skeleton built from the prepared rig (design doc §8; no bpy).

Input: a :class:`RigData` snapshot taken after stage ③ (A-pose, standard size,
facing -Y), the slot mapping (slot_id → current bone name), the dispositions of
the other bones and the 下半身 diagnosis.  Output: a :class:`SkeletonPlan` —
every bone of the final PMX in export order with its Blender name (= MMD
name), English name, head / tail, parent, flags, 付与, IK, axes and display
frame, plus the new skin weights — which ``blender/skeleton_apply`` and
``blender/mmdtools_bridge`` execute without making further decisions.

Placement formulas (``u`` = model height / 20.8, one 18-series PMX unit):

* センター  ひざ + 0.40·(足 − ひざ) (height), x = y = 0 (note 11 §13.3)
* グルーブ  センター + 0.0002·H
* 腰        足 + 0.40·(下半身 − 足), depth 0.02·下半身 height behind (plugin_ssb)
* 下半身    head = 上半身 head lowered by 0.005u, tail straight down 1u (note 11 §5.4)
* 上半身2   上半身 → 首 at 0.35 (generated only for a one-bone spine)
* 両目      0.024·H above the top of the head, tail 0.5u forward
* 肩P / 肩C / 腰キャンセル at the head of the bone they parent
* 腕捩 / 手捩 60 %, 捩1/2/3 at 32/52/72 %, fixed axis along the segment
* ダミー    plugin_ssb formula from 手首 and 中指１
* 足IK親    under the ankle on the ground; 足ＩＫ at the ankle, つま先ＩＫ at the toe
* 足D 系    copies of 足/ひざ/足首 (付与 1.0, 変形階層 1); 足先EX at 2/3 足首 → つま先
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from ..result import ERROR, INFO, WARNING, Message
from ..spec.bone_slots import BoneSpec, SlotSpec, mmd_name_problems
from ..weights import rules
from ..weights.skin import SkinEditor
from .rigdata import RigData

UNIT_HEIGHT_PMX = 20.8
SIDES = {"L": "left", "R": "right"}

#: Tier switches (design doc §8.1): tier 1 is always generated.
TIER_ALWAYS = 1

#: Display-tail successors: a mapped bone's tail is pointed at the first present
#: successor (``{s}`` = left / right).  Bones not listed keep their imported tail.
TAIL_TO: Dict[str, Tuple[str, ...]] = {
    "upper_body_bone": ("upper_body1_bone", "upper_body2_bone", "upper_body3_bone", "upper_body4_bone", "neck_bone"),
    "upper_body1_bone": ("upper_body2_bone", "upper_body3_bone", "upper_body4_bone", "neck_bone"),
    "upper_body2_bone": ("upper_body3_bone", "upper_body4_bone", "neck_bone"),
    "upper_body3_bone": ("upper_body4_bone", "neck_bone"),
    "upper_body4_bone": ("neck_bone",),
    "neck_bone": ("neck1_bone", "head_bone"),
    "neck1_bone": ("head_bone",),
    "{s}_shoulder_bone": ("{s}_upper_arm_bone",),
    "{s}_upper_arm_bone": ("{s}_lower_arm_bone",),
    "{s}_lower_arm_bone": ("{s}_hand_bone",),
    "{s}_hand_bone": ("{s}_middle_1",),
    "{s}_thumb_0": ("{s}_thumb_1",),
    "{s}_thumb_1": ("{s}_thumb_2",),
    "{s}_index_1": ("{s}_index_2",),
    "{s}_index_2": ("{s}_index_3",),
    "{s}_middle_1": ("{s}_middle_2",),
    "{s}_middle_2": ("{s}_middle_3",),
    "{s}_ring_1": ("{s}_ring_2",),
    "{s}_ring_2": ("{s}_ring_3",),
    "{s}_pinky_1": ("{s}_pinky_2",),
    "{s}_pinky_2": ("{s}_pinky_3",),
    "{s}_thigh_bone": ("{s}_knee_bone",),
    "{s}_knee_bone": ("{s}_ankle_bone",),
    "{s}_ankle_bone": ("{s}_toe_bone",),
}

#: Non-standard bones: category → (short-name prefix, movable, display frame).
CATEGORY_STYLE: Dict[str, Tuple[str, bool, str]] = {
    "hair": ("髪", False, "髪"),
    "cloth": ("衣", False, "物理"),
    "breast": ("胸", False, "物理"),
    "butt": ("尻", False, "物理"),
    "face": ("顔", True, "その他"),
    "genital": ("陰", True, "その他"),
    "prop": ("物", True, "その他"),
}
DEFAULT_STYLE = ("骨", True, "その他")
#: mmd_tools deletes bones with these prefixes by name (note 08 Q4).
RESERVED_PREFIXES = ("_dummy_", "_shadow_")

#: IK presets (design decision 4): あにまさ values come from bone_slots.csv; "S18" is
#: the 18-series / mmd_tools-default variant (loop 40 / 80, unit angle 1 rad).
IK_PRESETS = ("ANIMASA", "S18")
S18_IK = {"leg_ik": (40, 1.0), "toe_ik": (80, 1.0)}


@dataclass
class BuildOptions:
    tier2: bool = True
    tier3: bool = True
    twist_mode: str = "STEPPED"
    ik_preset: str = "ANIMASA"


@dataclass
class ExtraBone:
    """What stage ② decided for a bone that is not a slot's primary bone."""

    action: str            # keep | merge
    slot_id: str = ""      # merge target
    category: str = "other"


@dataclass
class IkLinkPlan:
    bone: str
    limit_min: Optional[Tuple[float, float, float]] = None   # radians, PMX axes (as in the PMX file)
    limit_max: Optional[Tuple[float, float, float]] = None


@dataclass
class IkPlan:
    target: str
    links: List[IkLinkPlan]
    loop: int
    unit_angle: float      # radians


@dataclass
class PlannedBone:
    name: str                              # Blender bone name = PMX name (name_j)
    name_e: str
    slot_id: str = ""
    source: str = ""                       # current Blender bone name; "" = created
    head: np.ndarray = field(default_factory=lambda: np.zeros(3))
    tail: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.01]))
    roll_like: str = ""                    # copy the roll of this (final-name) bone
    parent: str = ""
    deform: bool = True
    visible: bool = True
    controllable: bool = True
    movable: bool = False
    transform_order: int = 0
    grant_parent: str = ""
    grant_rate: float = 0.0
    fixed_axis: Optional[np.ndarray] = None
    local_x: Optional[np.ndarray] = None
    local_z: Optional[np.ndarray] = None
    ik: Optional[IkPlan] = None
    display_frame: str = ""
    category: str = ""

    @property
    def created(self) -> bool:
        return not self.source


@dataclass
class SkeletonPlan:
    bones: List[PlannedBone]
    skin_bones: Optional[np.ndarray] = None        # (N, 4) indices into ``bones``
    skin_weights: Optional[np.ndarray] = None      # (N, 4)
    messages: List[Message] = field(default_factory=list)
    stats: Dict[str, object] = field(default_factory=dict)

    def index(self) -> Dict[str, int]:
        return {b.name: i for i, b in enumerate(self.bones)}

    def by_slot(self) -> Dict[str, PlannedBone]:
        return {b.slot_id: b for b in self.bones if b.slot_id}

    def bone(self, name: str) -> Optional[PlannedBone]:
        return next((b for b in self.bones if b.name == name), None)

    @property
    def ok(self) -> bool:
        return not any(m.level == ERROR for m in self.messages)


# ---------------------------------------------------------------------------

def _unit(v: np.ndarray, fallback=(0.0, 0.0, 1.0)) -> np.ndarray:
    v = np.asarray(v, float)
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-12 else np.asarray(fallback, float)


def _orthogonal(ref: np.ndarray, x: np.ndarray) -> Optional[np.ndarray]:
    z = np.asarray(ref, float) - np.dot(ref, x) * x
    n = float(np.linalg.norm(z))
    return z / n if n > 1e-6 else None


def name_bytes(name: str) -> int:
    try:
        return len(name.encode("cp932"))
    except UnicodeEncodeError:
        return 999


class _Planner:
    def __init__(self, rig: RigData, spec: BoneSpec, slot_bones: Dict[str, str], extra: Dict[str, ExtraBone],
                 lower: Dict, opt: BuildOptions):
        self.rig = rig
        self.spec = spec
        self.opt = opt
        self.extra = extra
        self.lower = lower or {}
        self.msgs: List[Message] = []
        self.H = rig.height
        self.u = rig.height / UNIT_HEIGHT_PMX
        self.mapped: Dict[str, int] = {}
        for sid, name in slot_bones.items():
            if sid in spec.by_id and name in rig.by_name:
                self.mapped[sid] = rig.by_name[name]
            elif sid in spec.by_id and name:
                self.msg(ERROR, "build.slot_bone_missing", f"{spec[sid].name_j} 映射的骨 {name} 不在骨架里", name)
        self.planned: Dict[str, PlannedBone] = {}
        self.generated: List[str] = []
        self.skipped: Dict[str, str] = {}

    # -- helpers ----------------------------------------------------------------

    def msg(self, level: str, code: str, text: str, target: str = "", **data) -> None:
        self.msgs.append(Message(level, code, text, target, dict(data)))

    def present(self, sid: str) -> bool:
        return sid in self.planned

    def head(self, sid: str) -> Optional[np.ndarray]:
        b = self.planned.get(sid)
        return None if b is None else b.head

    def src_head(self, sid: str) -> Optional[np.ndarray]:
        i = self.mapped.get(sid)
        return None if i is None else self.rig.bones[i].head.copy()

    def side_sid(self, sid: str, base: str) -> str:
        """Same-side slot id: ``side_sid('left_arm_twist_bone', 'upper_arm_bone') → 'left_upper_arm_bone'``."""
        side = SIDES.get(self.spec[sid].side, "")
        return f"{side}_{base}" if side else base

    def tier_enabled(self, s: SlotSpec) -> bool:
        if s.tier <= TIER_ALWAYS:
            return s.tier == TIER_ALWAYS
        return self.opt.tier2 if s.tier == 2 else self.opt.tier3

    def spec_child(self, sid: str) -> Optional[str]:
        """The slot whose *first* parent candidate is ``sid`` and that is present (e.g. 肩C → 腕)."""
        for s in self.spec.ordered():
            if s.parents and s.parents[0] == sid and self.present(s.slot_id):
                return s.slot_id
        return None

    def mean_head(self, base: str) -> Optional[np.ndarray]:
        hs = [self.head(f"{side}_{base}") for side in ("left", "right")]
        hs = [h for h in hs if h is not None]
        return np.mean(hs, axis=0) if hs else None

    def new_bone(self, sid: str, head, tail, **kw) -> PlannedBone:
        s = self.spec[sid]
        b = PlannedBone(name=s.name_j, name_e=s.name_e, slot_id=sid, head=np.asarray(head, float),
                        tail=np.asarray(tail, float), **kw)
        self.planned[sid] = b
        if sid not in self.mapped:
            self.generated.append(sid)
        return b

    def weight_column(self, bone_index: int) -> np.ndarray:
        return self.rig.skin.bone_weight_column(bone_index)

    def top_of(self, sid: str) -> float:
        """Highest point of the mesh weighted (≥0.5) to the slot's bone; rig top otherwise."""
        i = self.mapped.get(sid)
        if i is not None and self.rig.skin is not None and self.rig.skin.count:
            col = self.weight_column(i)
            strong = col >= 0.5
            if strong.any():
                return float(self.rig.skin.positions[strong, 2].max())
        return float(self.rig.floor + self.H)

    # -- plan -----------------------------------------------------------------

    def run(self, slot_bones: Dict[str, str]) -> SkeletonPlan:
        for s in self.spec.ordered():
            if s.slot_id in self.mapped:
                b = self.rig.bones[self.mapped[s.slot_id]]
                self.new_bone(s.slot_id, b.head.copy(), b.tail.copy(), source=b.name)
        for s in self.spec.ordered():
            if s.required and s.slot_id not in self.mapped:
                self.msg(ERROR, "build.required_missing", f"必需骨 {s.name_j} 没有映射", s.slot_id)
        if any(m.level == ERROR for m in self.msgs):
            return SkeletonPlan([], messages=self.msgs)

        for recipe in RECIPE_ORDER:
            for s in self.spec.ordered():
                if s.recipe != recipe:
                    continue
                fn = RECIPES[recipe]
                if s.slot_id in self.mapped:
                    if recipe in NORMALISED_RECIPES:
                        fn(self, s, True)
                    continue
                if not self.tier_enabled(s):
                    self.skipped[s.slot_id] = "tier off"
                    continue
                reason = fn(self, s, False)
                if reason:
                    self.skipped[s.slot_id] = reason
        self._tails()
        self._spec_relations()
        extras = self._non_spec()
        bones = self._order(extras)
        plan = SkeletonPlan(bones, messages=self.msgs)
        self._axes(plan)
        self._weights(plan)
        plan.stats.update({"bones": len(bones), "generated": [self.spec[s].name_j for s in self.generated],
                           "skipped": {self.spec[s].name_j: r for s, r in self.skipped.items()
                                       if r != "tier off" and self.spec[s].tier > 0},
                           "non_standard": len(extras)})
        validate_plan(plan, self.spec)
        return plan

    # -- tails, parents, grants, IK ----------------------------------------------

    def _tails(self) -> None:
        for key, successors in TAIL_TO.items():
            for side in ("left", "right") if "{s}" in key else ("",):
                sid = key.format(s=side)
                b = self.planned.get(sid)
                if b is None or b.created:
                    continue
                for succ in successors:
                    h = self.head(succ.format(s=side))
                    if h is not None and np.linalg.norm(h - b.head) > 1e-4:
                        b.tail = h.copy()
                        break
        head = self.planned.get("head_bone")
        if head is not None:
            top = self.top_of("head_bone")
            head.tail = head.head + np.array([0.0, 0.0, max(0.5 * (top - head.head[2]), 0.25 * self.u)])

    def _spec_relations(self) -> None:
        for sid, b in self.planned.items():
            s = self.spec[sid]
            parent = self.spec.first_existing_parent(sid, self.present)
            b.parent = self.planned[parent].name if parent else ""
            b.deform, b.visible = s.deform, s.visible
            b.controllable, b.movable = s.controllable, s.movable
            b.transform_order = s.transform_order
            b.display_frame = s.display_frame
            if s.grant_parent:
                if self.present(s.grant_parent):
                    b.grant_parent = self.planned[s.grant_parent].name
                    b.grant_rate = float(s.grant_rate)
                else:
                    self.msg(WARNING, "build.grant_dropped",
                             f"{s.name_j} 的付与源 {self.spec[s.grant_parent].name_j} 不存在，付与已省略", s.name_j)
            if s.ik_target:
                self._ik(b, s)

    def _ik(self, b: PlannedBone, s: SlotSpec) -> None:
        needed = [s.ik_target] + [link.slot_id for link in s.ik_links]
        missing = [n for n in needed if not self.present(n)]
        if missing:
            self.msg(WARNING, "build.ik_dropped",
                     f"{s.name_j} 缺 {', '.join(self.spec[m].name_j for m in missing)}，不生成 IK", s.name_j)
            return
        loop, unit_deg = int(s.ik_loop), float(s.ik_unit_deg)
        unit = math.radians(unit_deg)
        if self.opt.ik_preset == "S18" and s.recipe in S18_IK:
            loop, unit = S18_IK[s.recipe]
        links = []
        for link in s.ik_links:
            lb = self.planned[link.slot_id]
            if link.limited:
                links.append(IkLinkPlan(lb.name, (math.radians(link.limit_min_deg), 0.0, 0.0),
                                        (math.radians(link.limit_max_deg), 0.0, 0.0)))
            else:
                links.append(IkLinkPlan(lb.name))
        b.ik = IkPlan(self.planned[s.ik_target].name, links, loop, unit)

    # -- non-standard bones -----------------------------------------------------

    def _non_spec(self) -> List[PlannedBone]:
        rig = self.rig
        primary = set(self.mapped.values())
        merged: Dict[int, str] = {}
        kept: List[int] = []
        for b in rig.bones:
            if b.index in primary:
                continue
            info = self.extra.get(b.name, ExtraBone("keep"))
            if info.action == "merge" and info.slot_id:
                merged[b.index] = info.slot_id
            else:
                kept.append(b.index)
        self.merged_bones = merged
        slot_of = {i: sid for sid, i in self.mapped.items()}
        final_of: Dict[int, str] = {}
        for i, sid in slot_of.items():
            final_of[i] = self.planned[sid].name
        names_taken: Set[str] = {b.name for b in self.planned.values()}
        out: List[PlannedBone] = []
        ub2 = self.planned.get("upper_body2_bone")
        ub = self.planned.get("upper_body_bone")
        ub2_generated = ub2 is not None and ub2.created
        root_name = self.planned["all_parents_bone"].name if self.present("all_parents_bone") else ""

        kept_set = set(kept)
        for i in kept:
            b = rig.bones[i]
            info = self.extra.get(b.name, ExtraBone("keep"))
            style = CATEGORY_STYLE.get(info.category, DEFAULT_STYLE)
            pb = PlannedBone(name="", name_e=b.src_name or b.name, source=b.name, head=b.head.copy(),
                             tail=b.tail.copy(), deform=b.weighted, visible=True, controllable=True,
                             movable=style[1], display_frame=style[2], category=info.category)
            parent = b.parent
            while parent >= 0 and parent not in kept_set and parent not in slot_of:
                parent = rig.bones[parent].parent
            pb.parent = parent  # temporarily the rig index (resolved below)
            out.append(pb)
        index_of = {pb.source: n for n, pb in enumerate(out)}
        # names
        for pb in out:
            src = pb.source
            ok = (not mmd_name_problems_short(src) and src not in names_taken
                  and not src.startswith(RESERVED_PREFIXES))
            if ok:
                pb.name = src
                names_taken.add(src)
        self._short_names(out, names_taken)
        for pb in out:
            final_of[rig.by_name[pb.source]] = pb.name
        for pb in out:
            p = pb.parent
            if p < 0:
                pb.parent = root_name
            else:
                pb.parent = final_of[p]
                if ub2_generated and ub is not None and pb.parent == ub.name and pb.head[2] >= ub2.head[2]:
                    pb.parent = ub2.name
        if merged:
            self.msg(INFO, "build.pending_merged",
                     f"{len(merged)} 根骨并入 ④ 生成的槽位：" + ", ".join(rig.bones[i].name for i in list(merged)[:5]))
        return out

    def _short_names(self, out: List[PlannedBone], taken: Set[str]) -> None:
        rig = self.rig
        pending = [pb for pb in out if not pb.name]
        if not pending:
            return
        eps = rig.centre_eps()
        counters: Dict[Tuple[str, str], int] = {}
        chain_of: Dict[str, Tuple[str, str, int]] = {}
        category = {pb.source: pb.category for pb in pending}
        for pb in out:
            if pb.name:
                continue
            b = rig.bones[rig.by_name[pb.source]]
            prefix = CATEGORY_STYLE.get(pb.category, DEFAULT_STYLE)[0]
            x = float(b.head[0])
            side = "L" if x > eps else ("R" if x < -eps else "")
            # chain root: walk up while the parent is also being renamed and has the same category
            depth, cur = 0, b
            while cur.parent >= 0:
                par = rig.bones[cur.parent]
                if category.get(par.name) != pb.category:
                    break
                cur, depth = par, depth + 1
            key = (prefix, side)
            if cur.name not in chain_of:
                counters[key] = counters.get(key, 0) + 1
                chain_of[cur.name] = (prefix, side, counters[key])
            prefix, side, chain = chain_of[cur.name]
            base = f"{prefix}{side}{chain}_{depth + 1}"
            name, k = base, 0
            while name in taken or name_bytes(name) > 15:
                k += 1
                name = f"{base}{chr(ord('a') + (k - 1) % 26)}{(k - 1) // 26 or ''}"
            pb.name = name
            taken.add(name)
        self.msg(INFO, "build.renamed_long",
                 f"{len(pending)} 根非标准骨名字超长或含 cp932 外字符，改用短名（原名放英文名）",
                 renamed={pb.name_e: pb.name for pb in pending[:50]})

    # -- order --------------------------------------------------------------------

    def _order(self, extras: List[PlannedBone]) -> List[PlannedBone]:
        spec_bones = [self.planned[s.slot_id] for s in self.spec.ordered() if s.slot_id in self.planned]
        early = [b for b in spec_bones if b.transform_order == 0]
        late = [b for b in spec_bones if b.transform_order != 0]
        children: Dict[str, List[PlannedBone]] = {}
        for pb in extras:
            children.setdefault(pb.parent, []).append(pb)
        ordered_extras: List[PlannedBone] = []
        placed: Set[str] = set()

        def visit(name: str) -> None:
            for c in children.get(name, ()):
                if c.name in placed:
                    continue
                placed.add(c.name)
                ordered_extras.append(c)
                visit(c.name)

        for b in early + late:
            visit(b.name)
        for pb in extras:  # parents among themselves only (should not happen)
            if pb.name not in placed:
                placed.add(pb.name)
                ordered_extras.append(pb)
                visit(pb.name)
        return early + ordered_extras + late

    # -- axes ---------------------------------------------------------------------

    def _axes(self, plan: SkeletonPlan) -> None:
        by_slot = plan.by_slot()
        back = np.array([0.0, 1.0, 0.0])
        for sid, b in by_slot.items():
            s = self.spec[sid]
            if s.recipe == "twist":
                continue
            if not ((s.group == "arm" and s.row_type == "symmetric") or s.group == "finger"):
                continue
            x = _unit(b.tail - b.head)
            ref = back
            if "thumb" in sid:
                index = by_slot.get(self.side_sid(sid, "index_1"))
                thumb0 = by_slot.get(self.side_sid(sid, "thumb_0")) or b
                if index is not None:
                    ref = _unit(thumb0.head - index.head)
            z = _orthogonal(ref, x)
            if z is None:
                z = _orthogonal(np.array([0.0, 0.0, 1.0]), x)
            if z is not None:
                b.local_x, b.local_z = x, z

    # -- weights ------------------------------------------------------------------

    def _weights(self, plan: SkeletonPlan) -> None:
        rig = self.rig
        if rig.skin is None or not rig.skin.count:
            self.msg(WARNING, "build.no_skin", "没有蒙皮网格，跳过权重")
            return
        idx = plan.index()
        by_slot = plan.by_slot()
        mapping: Dict[int, int] = {}
        for sid, i in self.mapped.items():
            mapping[i] = idx[self.planned[sid].name]
        for pb in plan.bones:
            if pb.source and not pb.slot_id:
                mapping[rig.by_name[pb.source]] = idx[pb.name]
        unresolved = []
        for i, sid in self.merged_bones.items():
            target = sid if sid in by_slot else self.spec.first_existing_parent(sid, lambda p: p in by_slot)
            if target is None:
                unresolved.append(rig.bones[i].name)
                continue
            mapping[i] = idx[by_slot[target].name]
        for b in rig.bones:  # anything left (should not happen): nearest planned ancestor
            if b.index in mapping:
                continue
            p = b.parent
            while p >= 0 and p not in mapping:
                p = rig.bones[p].parent
            if p >= 0:
                mapping[b.index] = mapping[p]
            else:
                unresolved.append(b.name)
        for b in rig.bones:
            mapping.setdefault(b.index, -1)
        if unresolved:
            self.msg(WARNING, "build.weights_unresolved", f"{len(unresolved)} 根骨的权重找不到去处："
                                                           + ", ".join(unresolved[:5]))
        ed = SkinEditor(rig.skin.bones, rig.skin.weights)
        ed.remap(mapping)
        pos = rig.skin.positions.astype(np.float64)
        stats: Dict[str, object] = {}

        def bi(sid: str) -> Optional[int]:
            b = by_slot.get(sid)
            return None if b is None else idx[b.name]

        # 下半身 construction (design doc §6): case C splits the bone that also covers the belly
        # (S(t) stays / goes to 下半身, the rest to 上半身); case D splits the lowest spine bone.
        lb = by_slot.get("lower_body_bone")
        ub_i = bi("upper_body_bone")
        case = self.lower.get("case", "")
        if lb is not None:
            lb_i = idx[lb.name]
            split_name = self.lower.get("split_bone", "")
            src = None
            if case == "C" and split_name in rig.by_name:
                src = mapping.get(rig.by_name[split_name])
            elif case == "D" and (lb.created or float(ed.column(lb_i).sum()) < 1.0):
                src = ub_i
            if src is not None and src >= 0:
                thigh_z = float(np.mean([by_slot[f"{s}_thigh_bone"].head[2] for s in ("left", "right")]))
                seg = float(by_slot["upper_body_bone"].head[2]) - thigh_z
                seg = seg if seg > 0.01 * self.H else 0.03 * self.H
                share = rules.lower_body_share(pos, thigh_z, seg)
                src_bone = plan.bones[src]
                if src == lb_i:
                    moved = ed.split(lb_i, [(ub_i, 1.0 - share)])
                    what = f"下半身 自身覆盖下腹，按高度把 Σ{moved:.1f} 移给 上半身"
                elif src == ub_i or (src_bone.deform and src_bone.slot_id):
                    moved = ed.split(src, [(lb_i, share)])
                    what = f"从 {src_bone.name} 按高度切出 Σ{moved:.1f} 给 下半身"
                else:  # control / helper bone: everything leaves it
                    moved = ed.split(src, [(lb_i, share), (ub_i, 1.0 - share)])
                    what = f"把 {src_bone.name} 的权重 Σ{moved:.1f} 按高度分给 下半身 / 上半身"
                stats["lower_body_from"] = src_bone.name
                stats["lower_body_moved"] = round(moved, 2)
                self.msg(INFO, "build.lower_body_split", f"下半身（情形{case}）：{what}", lb.name)
            elif lb.created:
                self.msg(WARNING, "build.lower_body_unweighted",
                         f"下半身 是生成的，但诊断（情形{case or '?'}）没有可切分的骨，下半身 暂无权重", lb.name)

        # 上半身2 (generated for a one-bone spine)
        ub2 = by_slot.get("upper_body2_bone")
        if ub2 is not None and ub2.created and ub_i is not None:
            neck = by_slot.get("neck_bone") or by_slot.get("head_bone")
            share = rules.upper_body2_share(pos, ub2.head, neck.head)
            moved = ed.split(ub_i, [(idx[ub2.name], share)])
            stats["upper_body2_weight"] = round(moved, 2)

        # twist bones
        twist_done = []
        for s in self.spec.ordered():
            if s.recipe != "twist" or s.slot_id not in by_slot or not by_slot[s.slot_id].created:
                continue
            seg_start, seg_end = self._twist_segment(s.slot_id)
            subs = [t.slot_id for t in self.spec.ordered() if t.recipe == "twist_sub" and t.grant_parent == s.slot_id]
            subs.sort(key=lambda t: self.spec[t].grant_rate or 0.0)
            if seg_start is None or seg_end is None or len(subs) != 3 or not all(t in by_slot for t in subs):
                self.msg(WARNING, "build.twist_weights_skipped", f"{s.name_j} 的分段不全，未切分扭转权重", s.name_j)
                continue
            base = bi(seg_start)
            shares = rules.twist_segment_shares(pos, by_slot[seg_start].head, by_slot[seg_end].head,
                                                self.opt.twist_mode)
            parts = [(bi(t), shares[:, k + 1]) for k, t in enumerate(subs)] + [(bi(s.slot_id), shares[:, 4])]
            moved = ed.split(base, parts)
            twist_done.append(s.name_j)
            stats[f"twist_{s.slot_id}"] = round(moved, 2)

        # D bones: all FK leg weights move to the D copies
        for s in self.spec.ordered():
            if s.recipe != "d_bone" or s.slot_id not in by_slot:
                continue
            src_sid = s.recipe_args.get("source", "")
            if src_sid in by_slot:
                stats[f"d_{s.slot_id}"] = round(ed.transfer(bi(src_sid), bi(s.slot_id)), 2)

        # 足先EX takes the front of 足首(D)
        for s in self.spec.ordered():
            if s.recipe != "toe_ex" or s.slot_id not in by_slot:
                continue
            parent_sid = self.spec.first_existing_parent(s.slot_id, lambda p: p in by_slot)
            ankle_sid = self.side_sid(s.slot_id, "ankle_bone")
            if parent_sid is None or ankle_sid not in by_slot:
                continue
            share = rules.toe_ex_share(pos, by_slot[ankle_sid].head, by_slot[s.slot_id].head)
            stats[f"toe_ex_{s.slot_id}"] = round(ed.split(bi(parent_sid), [(bi(s.slot_id), share)]), 2)

        # weights left on bones that must not deform → nearest deforming ancestor
        moved_total, moved_from = 0.0, []
        for i, pb in enumerate(plan.bones):
            if pb.deform or not pb.slot_id:
                continue
            col = ed.column(i)
            if not (col > 0).any():
                continue
            target = self._deform_ancestor(plan, i)
            if target is None:
                continue
            moved_total += ed.transfer(i, target)
            moved_from.append(pb.name)
        if moved_from:
            self.msg(WARNING, "build.control_weights_moved",
                     f"控制骨 {', '.join(moved_from[:5])} 上有权重（Σ{moved_total:.1f}），已移到最近的变形父骨")

        before = ed.totals()
        counts = ed.compact()
        plan.skin_bones, plan.skin_weights = ed.arrays()
        stats.update({"vertices": ed.count, "capped_vertices": counts["capped"], "dust_vertices": counts["dust"],
                      "unweighted_vertices": int((before <= 0).sum()), "twist": twist_done})
        if counts["capped"]:
            self.msg(INFO, "build.influences_capped",
                     f"{counts['capped']} 个顶点切分后超过 4 个影响骨，已去掉最小的并归一化")
        if stats["unweighted_vertices"]:
            self.msg(WARNING, "build.unweighted_vertices",
                     f"{stats['unweighted_vertices']} 个顶点没有任何权重（导出后会绑到第 0 根骨）")
        plan.stats.update(stats)

    def _twist_segment(self, twist_sid: str) -> Tuple[Optional[str], Optional[str]]:
        start = self.spec.first_existing_parent(twist_sid, self.present)
        end = self.spec_child(twist_sid)
        return start, end

    def _deform_ancestor(self, plan: SkeletonPlan, i: int) -> Optional[int]:
        idx = plan.index()
        cur = plan.bones[i]
        seen = set()
        while cur.parent and cur.parent not in seen:
            seen.add(cur.parent)
            j = idx[cur.parent]
            if plan.bones[j].deform:
                return j
            cur = plan.bones[j]
        lb = plan.by_slot().get("lower_body_bone")
        return idx[lb.name] if lb is not None else None


def mmd_name_problems_short(name: str) -> List[str]:
    """Name problems that force a non-standard bone to be renamed (cp932 and the 15-byte VMD limit)."""
    problems = []
    try:
        if len(name.encode("cp932")) > 15:
            problems.append("too long")
    except UnicodeEncodeError:
        problems.append("not cp932")
    if not name.strip():
        problems.append("empty")
    return problems


# ---------------------------------------------------------------------------
# recipes: fn(planner, slot, mapped) -> "" on success / reason it was skipped.
# For mapped slots only the NORMALISED_RECIPES run (control bones always sit at
# their formula position).

def _r_origin(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    length = (2.0 if s.slot_id == "all_parents_bone" else 1.0) * p.u
    if mapped:
        b = p.planned[s.slot_id]
        b.head, b.tail = np.zeros(3), np.array([0.0, 0.0, length])
    else:
        p.new_bone(s.slot_id, np.zeros(3), [0.0, 0.0, length])
    return ""


def _r_lower_body(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    ub = p.head("upper_body_bone")
    if ub is None or p.mean_head("thigh_bone") is None:
        return "缺 上半身 或 足"
    head = ub - np.array([0.0, 0.0, 0.005 * p.u])
    tail = head - np.array([0.0, 0.0, 1.0 * p.u])
    if mapped:
        b = p.planned[s.slot_id]
        b.head, b.tail = head, tail
    else:
        p.new_bone(s.slot_id, head, tail)
    return ""


def _r_center(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    thigh, knee = p.mean_head("thigh_bone"), p.mean_head("knee_bone")
    if thigh is None or knee is None:
        return "缺 足 或 ひざ"
    ratio = s.arg("ratio", 0.40)
    head = np.array([0.0, 0.0, knee[2] + ratio * (thigh[2] - knee[2])])
    tail = head - np.array([0.0, 0.0, 1.0 * p.u])
    if mapped:
        b = p.planned[s.slot_id]
        b.head, b.tail = head, tail
    else:
        p.new_bone(s.slot_id, head, tail)
    return ""


def _r_groove(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    center = p.head("center_bone")
    if center is None:
        return "缺 センター"
    head = center + np.array([0.0, 0.0, s.arg("offset_h", 0.0002) * p.H])
    tail = head + np.array([0.0, 0.0, 1.4 * p.u])
    if mapped:
        b = p.planned[s.slot_id]
        b.head, b.tail = head, tail
    else:
        p.new_bone(s.slot_id, head, tail)
    return ""


def _r_waist(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    lower, thigh = p.head("lower_body_bone"), p.mean_head("thigh_bone")
    if lower is None or thigh is None:
        return "缺 下半身 或 足"
    ratio = s.arg("ratio", 0.40)
    z = thigh[2] + ratio * (lower[2] - thigh[2])
    head = np.array([0.0, 0.02 * lower[2], z])
    tail = head + 0.8 * (lower - head)
    if np.linalg.norm(tail - head) < 0.2 * p.u:
        tail = head + np.array([0.0, 0.0, 0.5 * p.u])
    if mapped:
        b = p.planned[s.slot_id]
        b.head, b.tail = head, tail
    else:
        p.new_bone(s.slot_id, head, tail)
    return ""


def _r_upper_body2(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    if any(p.present(x) for x in ("upper_body1_bone", "upper_body3_bone", "upper_body4_bone")):
        return "脊柱已有多节"
    ub = p.head("upper_body_bone")
    neck = p.head("neck_bone") if p.present("neck_bone") else p.head("head_bone")
    if ub is None or neck is None:
        return "缺 上半身 或 首"
    origin = ub + s.arg("t", 0.35) * (neck - ub)
    p.new_bone(s.slot_id, origin, origin + 0.8 * (neck - origin))
    return ""


def _r_neck(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    head = p.head("head_bone")
    below = next((p.head(x) for x in ("upper_body4_bone", "upper_body3_bone", "upper_body2_bone",
                                       "upper_body1_bone", "upper_body_bone") if p.present(x)), None)
    if head is None or below is None:
        return "缺 頭 或 脊柱"
    pos = below + 0.7 * (head - below)
    p.new_bone(s.slot_id, pos, head.copy())
    p.msg(WARNING, "build.neck_generated", "源骨架没有颈骨，已生成 首（无权重）", s.name_j)
    return ""


def _r_eyes(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    if not (p.present("left_eye_bone") or p.present("right_eye_bone")):
        return "没有眼骨"
    top = p.top_of("head_bone")
    head = np.array([0.0, 0.0, top + s.arg("above_h", 0.024) * p.H])
    p.new_bone(s.slot_id, head, head + np.array([0.0, -0.5 * p.u, 0.0]))
    for eye in ("left_eye_bone", "right_eye_bone"):
        b = p.planned.get(eye)
        if b is not None and not b.created:  # same orientation as 両目 → no shadow bones needed
            b.tail = b.head + np.array([0.0, -0.5 * p.u, 0.0])
    return ""


def _r_at_child(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    """肩P / 肩C / 腰キャンセル: a helper at the head of the bone it parents."""
    child = p.spec_child(s.slot_id)
    if child is None:
        return "子骨不存在"
    head = p.head(child).copy()
    if s.recipe == "shoulder_p":
        tail = head + np.array([0.0, 0.0, 0.6 * p.u])
    elif s.recipe == "shoulder_c":
        parent = p.spec.first_existing_parent(s.slot_id, p.present)
        direction = _unit(head - p.head(parent)) if parent else np.array([1.0, 0.0, 0.0])
        tail = head + 0.5 * p.u * direction
    else:
        tail = head - np.array([0.0, 0.0, 0.5 * p.u])
    p.new_bone(s.slot_id, head, tail)
    return ""


def _r_twist(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    start = p.spec.first_existing_parent(s.slot_id, p.present)
    end = p.spec_child(s.slot_id)
    if start is None or end is None:
        return "缺上下段骨"
    if any(p.present(t.slot_id) for t in p.spec if t.grant_parent == s.slot_id and t.slot_id in p.mapped):
        return "源骨架已有捩骨"
    a, c = p.head(start), p.head(end)
    axis = _unit(c - a)
    length = float(np.linalg.norm(c - a))
    head = a + s.arg("t", 0.60) * (c - a)
    b = p.new_bone(s.slot_id, head, head + axis * 0.15 * length)
    b.fixed_axis = axis
    return ""


def _r_twist_sub(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    twist = p.planned.get(s.grant_parent)
    if twist is None:
        return "主捩骨不存在"
    start = p.spec.first_existing_parent(s.grant_parent, p.present)
    end = p.spec_child(s.grant_parent)
    a, c = p.head(start), p.head(end)
    axis = _unit(c - a)
    length = float(np.linalg.norm(c - a))
    head = a + s.arg("t", 0.5) * (c - a)
    p.new_bone(s.slot_id, head, head + axis * 0.1 * length, roll_like=twist.name)
    return ""


def _r_dummy(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    hand = p.head(p.side_sid(s.slot_id, "hand_bone"))
    if hand is None:
        return "缺 手首"
    mid = p.head(p.side_sid(s.slot_id, "middle_1"))
    if mid is None:
        hb = p.planned[p.side_sid(s.slot_id, "hand_bone")]
        mid = hb.tail.copy()
    m = np.array([(hand[0] + mid[0]) / 2, hand[1], (hand[2] + mid[2]) / 2])
    n = _unit(np.array([mid[0] - hand[0], mid[2] - hand[2]]), fallback=(1.0, 0.0))
    r2 = (n[1], -n[0]) if s.side == "L" else (-n[1], n[0])
    r = np.array([r2[0], 0.0, r2[1]])
    head = m + 0.25 * p.u * r
    p.new_bone(s.slot_id, head, head + 1.2 * p.u * r)
    return ""


def _r_thumb0(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    child = p.spec_child(s.slot_id)
    hand = p.head(p.side_sid(s.slot_id, "hand_bone"))
    if child is None or hand is None:
        return "缺 親指１ 或 手首"
    head = hand + s.arg("t", 2.0 / 3.0) * (p.head(child) - hand)
    p.new_bone(s.slot_id, head, p.head(child).copy())
    p.msg(INFO, "build.thumb0_unweighted", f"{s.name_j} 是生成的，没有权重", s.name_j)
    return ""


def _r_toe(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    ankle_sid = p.side_sid(s.slot_id, "ankle_bone")
    ankle = p.head(ankle_sid)
    if ankle is None:
        return "缺 足首"
    i = p.mapped.get(ankle_sid)
    head = None
    if i is not None and p.rig.skin is not None:
        col = p.weight_column(i)
        pts = p.rig.skin.positions[col >= 0.5].astype(float)
        if len(pts):
            front = float(pts[:, 1].min())
            sel = pts[pts[:, 1] <= ankle[1] - 0.5 * (ankle[1] - front)]
            if len(sel):
                head = np.array([ankle[0], float(sel[:, 1].mean()), float(sel[:, 2].mean())])
    if head is None:
        head = ankle + np.array([0.0, -2.0 * p.u, -ankle[2] * 0.8])
    p.new_bone(s.slot_id, head, head + np.array([0.0, -1.0 * p.u, 0.0]))
    p.msg(INFO, "build.toe_generated", f"{s.name_j} 是生成的（源骨架没有脚趾骨），没有权重", s.name_j)
    return ""


def _r_leg_ik(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    target = p.head(s.ik_target)
    if target is None:
        return "缺 IK 目标"
    if s.recipe == "leg_ik":
        tail = target + np.array([0.0, 1.5 * p.u, 0.0])
    else:
        tail = target - np.array([0.0, 0.0, 1.0 * p.u])
    p.new_bone(s.slot_id, target.copy(), tail)
    return ""


def _r_leg_ik_parent(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    child = p.spec_child(s.slot_id)
    if child is None:
        return "缺 足ＩＫ"
    c = p.head(child)
    head = np.array([c[0], c[1], 0.0])
    tail = c.copy() if c[2] > 0.1 * p.u else head + np.array([0.0, 0.0, 0.5 * p.u])
    p.new_bone(s.slot_id, head, tail)
    return ""


def _r_d_bone(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    src = s.recipe_args.get("source", "")
    b = p.planned.get(src)
    if b is None:
        return "缺源骨"
    p.new_bone(s.slot_id, b.head.copy(), b.tail.copy(), roll_like=b.name)
    return ""


def _r_toe_ex(p: _Planner, s: SlotSpec, mapped: bool) -> str:
    ankle = p.head(p.side_sid(s.slot_id, "ankle_bone"))
    toe = p.head(p.side_sid(s.slot_id, "toe_bone"))
    if ankle is None or toe is None:
        return "缺 足首 或 つま先"
    head = ankle + s.arg("t", 2.0 / 3.0) * (toe - ankle)
    p.new_bone(s.slot_id, head, head + np.array([0.0, -1.0 * p.u, 0.0]))
    return ""


RECIPES: Dict[str, Callable[[_Planner, SlotSpec, bool], str]] = {
    "origin": _r_origin,
    "lower_body": _r_lower_body,
    "center": _r_center,
    "groove": _r_groove,
    "waist": _r_waist,
    "upper_body2": _r_upper_body2,
    "spine_chain": lambda p, s, m: "只来自源骨",
    "neck": _r_neck,
    "eyes": _r_eyes,
    "shoulder_p": _r_at_child,
    "shoulder_c": _r_at_child,
    "waist_cancel": _r_at_child,
    "twist": _r_twist,
    "twist_sub": _r_twist_sub,
    "dummy": _r_dummy,
    "thumb0": _r_thumb0,
    "toe": _r_toe,
    "leg_ik": _r_leg_ik,
    "toe_ik": _r_leg_ik,
    "leg_ik_parent": _r_leg_ik_parent,
    "d_bone": _r_d_bone,
    "toe_ex": _r_toe_ex,
}
#: Evaluation order (dependencies: 腰 needs 下半身, 足IK親 needs 足ＩＫ, D bones need their FK bones …).
RECIPE_ORDER = ("origin", "lower_body", "center", "groove", "waist", "neck", "upper_body2", "spine_chain", "eyes",
                "shoulder_p", "shoulder_c", "twist", "twist_sub", "dummy", "thumb0", "waist_cancel", "toe",
                "leg_ik", "toe_ik", "leg_ik_parent", "d_bone", "toe_ex")
#: Recipes that also re-place a *mapped* bone (control bones always sit at their formula position).
NORMALISED_RECIPES = frozenset({"origin", "lower_body", "center", "groove", "waist"})


# ---------------------------------------------------------------------------

def plan_skeleton(rig: RigData, spec: BoneSpec, slot_bones: Dict[str, str],
                  extra: Optional[Dict[str, ExtraBone]] = None, lower: Optional[Dict] = None,
                  options: Optional[BuildOptions] = None) -> SkeletonPlan:
    """Plan the MMD skeleton; see the module docstring.  ``slot_bones``: slot_id → current bone name."""
    options = options or BuildOptions()
    if options.twist_mode not in rules.TWIST_MODES:
        raise ValueError(f"unknown twist mode {options.twist_mode!r}")
    if options.ik_preset not in IK_PRESETS:
        raise ValueError(f"unknown IK preset {options.ik_preset!r}")
    planner = _Planner(rig, spec, {k: v for k, v in slot_bones.items() if v}, extra or {}, lower or {}, options)
    return planner.run(slot_bones)


def validate_plan(plan: SkeletonPlan, spec: BoneSpec) -> List[Message]:
    """Structural invariants of a plan (appended to ``plan.messages`` as errors)."""
    found: List[Message] = []

    def err(code: str, text: str, target: str = "") -> None:
        found.append(Message(ERROR, code, text, target))

    names: Dict[str, int] = {}
    for i, b in enumerate(plan.bones):
        if b.name in names:
            err("build.plan_duplicate", f"骨名重复：{b.name}", b.name)
        names[b.name] = i
        problems = mmd_name_problems(b.name) if b.slot_id else mmd_name_problems_short(b.name)
        if problems:
            err("build.plan_name", f"骨名 {b.name} 不合规：{'; '.join(problems)}", b.name)
        if b.name.startswith(RESERVED_PREFIXES):
            err("build.plan_name", f"骨名 {b.name} 用了 mmd_tools 保留前缀", b.name)
        if float(np.linalg.norm(b.tail - b.head)) < 1e-5:
            err("build.plan_zero_length", f"{b.name} 长度为 0", b.name)

    def rank(name: str) -> Tuple[int, int]:
        j = names[name]
        return plan.bones[j].transform_order, j

    for i, b in enumerate(plan.bones):
        me = (b.transform_order, i)
        if b.parent:
            if b.parent not in names:
                err("build.plan_parent", f"{b.name} 的父骨 {b.parent} 不存在", b.name)
            elif names[b.parent] >= i:
                err("build.plan_order", f"{b.name} 排在父骨 {b.parent} 之前", b.name)
        if b.grant_parent:
            if b.grant_parent not in names or b.grant_parent == b.name:
                err("build.plan_grant", f"{b.name} 的付与源 {b.grant_parent} 无效", b.name)
            elif rank(b.grant_parent) >= me:
                err("build.plan_order", f"{b.name} 的付与源 {b.grant_parent} 排在它之后", b.name)
        if b.ik is not None:
            for ref in [b.ik.target] + [link.bone for link in b.ik.links]:
                if ref not in names:
                    err("build.plan_ik", f"{b.name} 的 IK 引用了不存在的 {ref}", b.name)
                elif rank(ref) >= me:
                    err("build.plan_order", f"IK 链骨 {ref} 排在 {b.name} 之后", b.name)
    if plan.skin_weights is not None:
        w = plan.skin_weights
        total = w.sum(axis=1)
        bad = (total > 0) & (np.abs(total - 1.0) > 1e-4)
        if bad.any():
            err("build.plan_weights", f"{int(bad.sum())} 个顶点的权重和不为 1")
        if plan.skin_bones.shape[1] > 4:
            err("build.plan_weights", "影响骨超过 4 个")
    plan.messages.extend(found)
    return found
