"""Stage ③ panel: scale, A-pose and normalisation options."""
from __future__ import annotations

import bpy

from .. import props


class XPS2PMX_PT_prepare(bpy.types.Panel):
    bl_label = "③ 预处理"
    bl_idname = "XPS2PMX_PT_prepare"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XPS→PMX"
    bl_parent_id = "XPS2PMX_PT_steps"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        job = props.active_job(context)
        return job is not None and job.armature is not None

    def draw(self, context):
        layout = self.layout
        job = props.active_job(context)
        col = layout.column(align=True)
        col.prop(job, "scale_mode")
        sub = col.row(align=True)
        sub.enabled = job.scale_mode == 'SHOULDER'
        sub.prop(job, "shoulder_target")
        col.separator()
        col.prop(job, "apose_preset")
        row = col.row(align=True)
        row.enabled = job.apose_preset == 'CUSTOM'
        row.prop(job, "apose_upper_deg")
        row.prop(job, "apose_fore_extra_deg")
        col.prop(job, "level_shoulders")
        if job.facing == "+Y":
            layout.label(text="模型背朝前方，执行时会先旋转 180°", icon='ERROR')
        layout.operator("xps2pmx.prepare", text="③ 预处理", icon='MOD_ARMATURE')
        info = job.summary().get("prepare")
        if info:
            box = layout.box()
            box.label(text=f"缩放 ×{info.get('scale_factor', 0):.4f}  肩高 {info.get('shoulder_pmx', 0):.2f}  "
                           f"身高 {info.get('height_pmx', 0):.2f}")
            box.label(text=f"上臂 {info.get('arm_left_deg', 0):.1f}°/{info.get('arm_right_deg', 0):.1f}°  "
                           f"前臂 {info.get('forearm_left_deg', 0):.1f}°/{info.get('forearm_right_deg', 0):.1f}°  "
                           f"拉裂边 {info.get('torn_edges', 0)}")


CLASSES = (XPS2PMX_PT_prepare,)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
