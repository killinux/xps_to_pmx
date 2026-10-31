"""「分步模式（高级）」parent panel (design doc §15.8): ① here, ② ③ ④ ⑧ as its sub-panels."""
from __future__ import annotations

import bpy

from .. import props


class XPS2PMX_PT_steps(bpy.types.Panel):
    bl_label = "分步模式（高级）"
    bl_idname = "XPS2PMX_PT_steps"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XPS→PMX"
    bl_parent_id = "XPS2PMX_PT_main"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        op = row.operator("xps2pmx.import_xps", text="① 只导入", icon='IMPORT')
        op.use_panel_path = True
        job = props.active_job(context)
        if job is not None and job.stage in ("import", "identify"):
            layout.label(text="改完映射点主面板的「继续」，或逐步点 ③ ④ ⑧", icon='INFO')


CLASSES = (XPS2PMX_PT_steps,)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
