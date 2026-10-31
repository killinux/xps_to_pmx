"""Stage ④ / ⑧ panels: MMD skeleton options and PMX export."""
from __future__ import annotations

import bpy

from .. import props

BUILT = props.BUILT_STAGES


class XPS2PMX_PT_build(bpy.types.Panel):
    bl_label = "④ 生成 MMD 骨架"
    bl_idname = "XPS2PMX_PT_build"
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
        built = job.stage in BUILT
        col = layout.column(align=True)
        col.enabled = not built
        row = col.row(align=True)
        row.prop(job, "gen_tier2")
        row.prop(job, "gen_tier3")
        col.prop(job, "twist_mode")
        col.prop(job, "ik_preset")
        row = layout.row()
        row.enabled = not built
        row.operator("xps2pmx.build", text="④ 生成 MMD 骨架", icon='OUTLINER_OB_ARMATURE')
        info = job.summary().get("build")
        if info:
            plan = info.get("plan", {})
            box = layout.box()
            box.label(text=f"{info.get('bones', 0)} 根骨：生成 {info.get('created', 0)}、改名 {info.get('renamed', 0)}、"
                           f"并入 {info.get('deleted', 0)}")
            box.label(text=f"重写权重 {info.get('weights_rewritten', 0)} 顶点；超 4 影响 {plan.get('capped_vertices', 0)}；"
                           f"无权重 {plan.get('unweighted_vertices', 0)}")
        if built:
            layout.label(text="已生成；要换这些选项：主面板「分步重做」后再生成", icon='INFO')


class XPS2PMX_PT_export(bpy.types.Panel):
    bl_label = "⑧ 导出 PMX"
    bl_idname = "XPS2PMX_PT_export"
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
        layout.prop(job, "export_path", text="")
        row = layout.row(align=True)
        row.enabled = job.stage in BUILT
        row.operator("xps2pmx.export", text="⑧ 导出 PMX", icon='EXPORT')
        row.operator("xps2pmx.open_export_dir", text="", icon='FILEBROWSER')
        info = job.summary().get("export")
        if info:
            box = layout.box()
            box.label(text=info.get("path", ""))
            box.label(text=f"{info.get('bones', 0)} 骨 · {info.get('vertices', 0)} 顶点 · {info.get('materials', 0)} 材质 · "
                           f"身高 {info.get('height_pmx', 0):.2f}")


CLASSES = (XPS2PMX_PT_build, XPS2PMX_PT_export)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
