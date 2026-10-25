"""Operators for stage ④ (MMD skeleton) and stage ⑧ (export)."""
from __future__ import annotations

import os

import bpy
from bpy.props import StringProperty

from .. import props
from ..pipeline import redo, stage_build, stage_export


def _finish(op, res, done_code: str) -> set:
    failures = [m for m in res.messages if m.level == 'error']
    for m in failures[:3]:
        op.report({'ERROR'}, m.text)
    if failures:
        return {'CANCELLED'}
    warnings = [m for m in res.messages if m.level == 'warning']
    done = next((m.text for m in res.messages if m.code == done_code), "完成")
    op.report({'WARNING'} if warnings else {'INFO'}, done + (f"（{len(warnings)} 条警告，见报告）" if warnings else ""))
    return {'FINISHED'}


class XPS2PMX_OT_build(bpy.types.Operator):
    """改名、补骨（三档）、下半身与权重规则、IK、付与、骨序、表示枠、材质参数，并收编为 mmd_tools 模型"""
    bl_idname = "xps2pmx.build"
    bl_label = "④ 生成 MMD 骨架"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        job = props.active_job(context)
        if job is None:
            self.report({'ERROR'}, "没有活动任务：先选中导入的骨架")
            return {'CANCELLED'}
        return _finish(self, stage_build.run(context, job), "build.done")


class XPS2PMX_OT_export(bpy.types.Operator):
    """REST 姿态 ×12.5 导出 PMX 并复制贴图，再读回文件逐项检查，报告写到 PMX 旁边"""
    bl_idname = "xps2pmx.export"
    bl_label = "⑧ 导出 PMX"
    bl_options = {'REGISTER'}

    filepath: StringProperty(subtype='FILE_PATH', default="", options={'SKIP_SAVE'})

    def execute(self, context):
        job = props.active_job(context)
        if job is None:
            self.report({'ERROR'}, "没有活动任务：先选中导入的骨架")
            return {'CANCELLED'}
        return _finish(self, stage_export.run(context, job, self.filepath), "export.done")


class XPS2PMX_OT_open_export_dir(bpy.types.Operator):
    """在资源管理器中打开上次导出的目录"""
    bl_idname = "xps2pmx.open_export_dir"
    bl_label = "打开导出目录"

    def execute(self, context):
        job = props.active_job(context)
        path = job.last_export if job is not None else ""
        if not path or not os.path.isdir(os.path.dirname(path)):
            self.report({'ERROR'}, "还没有导出过")
            return {'CANCELLED'}
        bpy.ops.wm.path_open(filepath=os.path.dirname(path))
        return {'FINISHED'}


class XPS2PMX_OT_redo(bpy.types.Operator):
    """删除本任务生成的对象，重新导入同一个 XPS，保留选项与手改的映射，自动重跑到原来的阶段"""
    bl_idname = "xps2pmx.redo"
    bl_label = "重来"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        job = props.active_job(context)
        if job is None:
            self.report({'ERROR'}, "没有活动任务")
            return {'CANCELLED'}
        res, new = redo.run(context, job)
        if new is not None and new.armature is not None:
            context.view_layer.objects.active = new.armature
        return _finish(self, res, "redo.done")


CLASSES = (XPS2PMX_OT_build, XPS2PMX_OT_export, XPS2PMX_OT_open_export_dir, XPS2PMX_OT_redo)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
