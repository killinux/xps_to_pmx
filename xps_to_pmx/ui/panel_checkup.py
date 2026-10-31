"""「修正单」sub-panel (design doc §15.3, §15.8): every decision that differs from the automatic result."""
from __future__ import annotations

import bpy

from .. import props

ORIGIN_ICONS = {'user': 'GREASEPENCIL', 'csv': 'FILE_TEXT', 'checkup': 'VIEWZOOM', 'file': 'FILE'}
ORIGIN_LABELS = {k: label for k, label, _ in props.FIX_ORIGIN_ITEMS}


def describe(job, item) -> str:
    def slot_name(slot_id: str) -> str:
        slot = job.slot(slot_id)
        return slot.name_j if slot is not None and slot.name_j else slot_id
    return item.to_fix().describe(slot_name)


class XPS2PMX_UL_fixes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        job = data
        row = layout.row(align=True)
        row.prop(item, "enabled", text="")
        tag = ORIGIN_LABELS.get(item.origin, "") + ("·自动" if item.auto else "")
        row.label(text=f"{describe(job, item)}（{tag}）", icon=ORIGIN_ICONS.get(item.origin, 'DOT'))
        op = row.operator("xps2pmx.fix_remove", text="", icon='X')
        op.index = index


class XPS2PMX_PT_fixes(bpy.types.Panel):
    bl_label = "修正单"
    bl_idname = "XPS2PMX_PT_fixes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XPS→PMX"
    bl_parent_id = "XPS2PMX_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return props.active_job(context) is not None

    def draw_header(self, context):
        job = props.active_job(context)
        self.layout.label(text=f"（{sum(1 for f in job.fixes if f.enabled)}/{len(job.fixes)}）")

    def draw(self, context):
        layout = self.layout
        job = props.active_job(context)
        if not job.fixes:
            layout.label(text="还没有修正：手改映射、勾选体检的修正都会记在这里", icon='INFO')
        else:
            layout.template_list("XPS2PMX_UL_fixes", "", job, "fixes", job, "fixes_index", rows=4)
            if 0 <= job.fixes_index < len(job.fixes) and job.fixes[job.fixes_index].note:
                layout.label(text=job.fixes[job.fixes_index].note, icon='INFO')
        row = layout.row(align=True)
        row.operator("xps2pmx.fixes_import", text="导入", icon='IMPORT')
        row.operator("xps2pmx.fixes_export", text="导出", icon='EXPORT')
        layout.label(text="导出 PMX 时自动保存，下次转换同一个 XPS 会自动套用", icon='FILE_TICK')


CLASSES = (XPS2PMX_UL_fixes, XPS2PMX_PT_fixes)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
