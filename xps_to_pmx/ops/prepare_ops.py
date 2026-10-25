"""Operators for stage ③ (preprocessing)."""
from __future__ import annotations

import bpy

from .. import props
from ..pipeline import stage_prepare


class XPS2PMX_OT_prepare(bpy.types.Operator):
    """按处置表合并辅助骨、删除无权重骨；修正朝向；缩放并贴地；手臂转到 A 姿势并烘焙为静止姿态"""
    bl_idname = "xps2pmx.prepare"
    bl_label = "③ 预处理"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        job = props.active_job(context)
        if job is None:
            self.report({'ERROR'}, "没有活动任务：先选中导入的骨架")
            return {'CANCELLED'}
        res = stage_prepare.run(context, job)
        failures = [m for m in res.messages if m.level == 'error']
        for m in failures[:3]:
            self.report({'ERROR'}, m.text)
        if failures:
            return {'CANCELLED'}
        done = next((m.text for m in res.messages if m.code == "prepare.done"), "完成")
        self.report({'INFO'}, done)
        return {'FINISHED'}


CLASSES = (XPS2PMX_OT_prepare,)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
