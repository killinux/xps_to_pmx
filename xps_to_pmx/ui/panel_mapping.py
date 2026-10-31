"""Stage ② panel: Convert-to-MMD style slot rows, 下半身 diagnosis, checks and the other bones.

Reads job properties only and calls operators (layer rule).
"""
from __future__ import annotations

from collections import OrderedDict

import bpy

from .. import props

BUILT_STAGES = props.BUILT_STAGES

LEVEL_ICONS = {'info': 'INFO', 'warning': 'ERROR', 'error': 'CANCEL'}
ACTION_ICONS = {'map': 'BONE_DATA', 'merge': 'AUTOMERGE_ON', 'keep': 'PINNED', 'delete': 'TRASH'}
FINGERS = (("thumb", "親指"), ("index", "人指"), ("middle", "中指"), ("ring", "薬指"), ("pinky", "小指"))


def _slot_status(job):
    worst = {}
    rank = {'error': 2, 'warning': 1, 'info': 0}
    for c in job.checks:
        if c.slot_id and rank[c.level] > rank.get(worst.get(c.slot_id), -1):
            worst[c.slot_id] = c.level
    return worst


def _icon(slot, status):
    level = status.get(slot.name)
    if level == 'error':
        return 'CANCEL'
    if level == 'warning':
        return 'ERROR'
    if not slot.bone:
        if slot.required:
            return 'CANCEL'
        return 'ADD' if slot.tier > 0 else 'DOT'
    if slot.origin == 'user':
        return 'GREASEPENCIL'
    return 'CHECKMARK'


def _slot_widget(layout, arm, slot, status):
    row = layout.row(align=True)
    row.label(text="", icon=_icon(slot, status))
    op = row.operator("xps2pmx.slot_pick", text="", icon='EYEDROPPER')
    op.slot_id = slot.name
    row.prop_search(slot, "bone", arm.data, "bones", text="")


def _label(slot):
    return slot.name_j + ("*" if slot.required else "")


def _base(name_j):
    for prefix in ("左", "右"):
        if name_j.startswith(prefix):
            return name_j[1:]
    return name_j.replace("左", "").replace("右", "")


def draw_single(layout, arm, slot, status):
    split = layout.split(factor=0.24, align=True)
    split.label(text=_label(slot))
    _slot_widget(split, arm, slot, status)


def draw_symmetric(layout, arm, left, right, status):
    split = layout.split(factor=0.16, align=True)
    split.label(text=_base(left.name_j) + ("*" if left.required else ""))
    halves = split.split(factor=0.5, align=True)
    _slot_widget(halves, arm, left, status)
    if right is not None:
        _slot_widget(halves, arm, right, status)
    else:
        halves.label(text="")


def draw_finger(layout, arm, label, slots, status):
    split = layout.split(factor=0.16, align=True)
    split.label(text=label)
    cols = split.split(factor=1 / 3, align=True)
    _slot_widget(cols, arm, slots[0], status)
    rest = cols.split(factor=0.5, align=True)
    for s in slots[1:3]:
        _slot_widget(rest, arm, s, status)


class XPS2PMX_UL_checks(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.text, icon=LEVEL_ICONS.get(item.level, 'INFO'))
        if item.target:
            op = row.operator("xps2pmx.locate_bone", text="", icon='VIEWZOOM')
            op.bone = item.target


class XPS2PMX_UL_bones(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        job = data
        row = layout.row(align=True)
        split = row.split(factor=0.42, align=True)
        label = item.name if not item.src or item.src == item.name else f"{item.name}（{item.src}）"
        split.label(text=label, icon=ACTION_ICONS.get(item.action, 'BONE_DATA'))
        right = split.split(factor=0.36, align=True)
        right.prop(item, "action", text="")
        if item.action in ('merge', 'map'):
            right.prop_search(item, "slot_id", job, "slots", text="")
        else:
            right.label(text=item.category)
        op = row.operator("xps2pmx.locate_bone", text="", icon='VIEWZOOM')
        op.bone = item.name

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        mode = data.bones_filter
        flags = []
        for it in items:
            if mode == 'ALL':
                ok = True
            elif mode == 'UNMAPPED':
                ok = it.action != 'map'
            else:
                ok = it.action == mode
            if ok and self.filter_name:
                ok = self.filter_name.lower() in (it.name + " " + it.src + " " + it.category).lower()
            flags.append(self.bitflag_filter_item if ok else 0)
        return flags, []


class XPS2PMX_PT_mapping(bpy.types.Panel):
    bl_label = "② 骨骼映射"
    bl_idname = "XPS2PMX_PT_mapping"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XPS→PMX"
    bl_parent_id = "XPS2PMX_PT_steps"

    @classmethod
    def poll(cls, context):
        job = props.active_job(context)
        return job is not None and job.armature is not None

    def draw(self, context):
        layout = self.layout
        st = props.state(context)
        job = props.active_job(context)
        arm = job.armature
        if job.stage in BUILT_STAGES:
            layout.label(text="MMD 骨架已生成：下面是生成时用的源骨映射（只读）", icon='LOCKED')
            layout.label(text="要改映射：点主面板的「分步重做」（从头导入并停在 ②）")
            layout = layout.column()
            layout.enabled = False

        row = layout.row(align=True)
        row.operator("xps2pmx.identify", text="② 自动识别", icon='VIEWZOOM')
        row.operator("xps2pmx.check_mapping", text="检查映射", icon='CHECKMARK')
        row = layout.row(align=True)
        row.label(text=f"约定：{job.convention or '—'}")
        sub = row.row(align=True)
        sub.enabled = bool(job.bones)  # the CSV is matched against the identified bones
        sub.operator("xps2pmx.mapping_import", text="", icon='IMPORT')
        row.operator("xps2pmx.mapping_export", text="", icon='EXPORT')
        row.operator("xps2pmx.mapping_reset_user", text="", icon='LOOP_BACK')
        if st.mapping_dirty:
            layout.label(text="映射已手动修改，点“检查映射”重新检查", icon='ERROR')
        if not job.slots:
            layout.label(text="点“② 自动识别”开始", icon='INFO')
            return

        status = _slot_status(job)
        slots = job.slot_map()
        ordered = list(job.slots)

        box = layout.box()
        box.label(text="躯干与控制骨（○ = 将生成）")
        col = box.column(align=True)
        for s in ordered:
            if s.group in ("control", "trunk") and s.row_type == "single":
                draw_single(col, arm, s, status)

        box = layout.box()
        header = box.split(factor=0.16)
        header.label(text="")
        halves = header.split(factor=0.5)
        halves.label(text="左")
        halves.label(text="右")
        col = box.column(align=True)
        for s in ordered:
            if s.row_type == "symmetric" and s.side == "L":
                draw_symmetric(col, arm, s, slots.get(s.mirror), status)

        box = layout.box()
        box.label(text="手指")
        col = box.column(align=True)
        for side, side_label in (("left", "左"), ("right", "右")):
            for key, label in FINGERS:
                names = ([f"{side}_thumb_0", f"{side}_thumb_1", f"{side}_thumb_2"] if key == "thumb"
                         else [f"{side}_{key}_{i}" for i in (1, 2, 3)])
                row_slots = [slots[n] for n in names if n in slots]
                if len(row_slots) == 3:
                    draw_finger(col, arm, side_label + label, row_slots, status)

        lb = job.lower_body()
        if lb:
            box = layout.box()
            box.label(text=f"下半身诊断：情形{lb.get('case') or '?'}", icon='MOD_ARMATURE')
            text = lb.get("text", "")
            for i in range(0, len(text), 34):
                box.label(text=text[i:i + 34])

        layout.label(text=f"检查结果（{len(job.checks)}）")
        layout.template_list("XPS2PMX_UL_checks", "", job, "checks", job, "checks_index", rows=4)

        row = layout.row()
        row.label(text="其余骨骼")
        row.prop(job, "bones_filter", text="")
        layout.template_list("XPS2PMX_UL_bones", "", job, "bones", job, "bones_index", rows=6)
        if 0 <= job.bones_index < len(job.bones):
            plan = job.bones[job.bones_index]
            layout.label(text=f"{plan.name}：{plan.reason}", icon='INFO')


CLASSES = (XPS2PMX_UL_checks, XPS2PMX_UL_bones, XPS2PMX_PT_mapping)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
