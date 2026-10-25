"""Main sidebar panel (tab "XPS→PMX").  Reads properties and calls operators only."""
from __future__ import annotations

import bpy

from .. import props

LEVEL_ICONS = {'info': 'INFO', 'warning': 'ERROR', 'error': 'CANCEL'}
MAX_REPORT_LINES = 8
NEXT_STEP = {
    "": "下一步：① 导入 XPS",
    "import": "下一步：② 自动识别，核对映射",
    "identify": "下一步：③ 预处理（缩放、A 姿势）",
    "prepare": "下一步：④ 生成 MMD 骨架",
    "build": "下一步：⑧ 导出 PMX（⑤ 表情、⑥ 物理开发中）",
    "export": "已导出：在 MMD 里打开测试",
}


def draw_report(layout, job, stage: str = "") -> None:
    lines = [r for r in job.reports if not stage or r.stage == stage]
    if not lines:
        return
    box = layout.box()
    shown = sorted(lines, key=lambda r: {'error': 0, 'warning': 1, 'info': 2}[r.level])[:MAX_REPORT_LINES]
    for r in shown:
        box.label(text=r.text, icon=LEVEL_ICONS.get(r.level, 'INFO'))
    if len(lines) > len(shown):
        box.label(text=f"…另有 {len(lines) - len(shown)} 条，见报告 JSON")


class XPS2PMX_PT_main(bpy.types.Panel):
    bl_label = "XPS → PMX"
    bl_idname = "XPS2PMX_PT_main"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "XPS→PMX"

    def draw(self, context):
        layout = self.layout
        st = props.state(context)
        row = layout.row(align=True)
        row.prop(st, "xps_path", text="")
        op = row.operator("xps2pmx.import_xps", text="① 导入", icon='IMPORT')
        op.use_panel_path = True

        job = props.active_job(context)
        if job is None:
            layout.label(text="还没有导入任何 XPS 模型", icon='INFO')
            return
        info = job.summary().get("import", {})
        box = layout.box()
        box.label(text=f"{job.model_name}", icon='ARMATURE_DATA')
        if info:
            box.label(text=f"{info.get('bones', 0)} 骨 · {info.get('meshes', 0)} 网格 · "
                           f"{info.get('vertices', 0)} 顶点 · XPS {info.get('version', '')}")
        done = props.STAGE_LABELS.get(job.stage, "—")
        row = box.row()
        row.label(text=f"已完成：{done}")
        row.operator("xps2pmx.redo", text="重来", icon='FILE_REFRESH')
        draw_report(layout, job, stage=job.stage)
        layout.label(text=NEXT_STEP.get(job.stage, ""), icon='FORWARD')


CLASSES = (XPS2PMX_PT_main,)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
