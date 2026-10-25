"""Operators for stage ② (identification, manual slot edits, checks, CSV)."""
from __future__ import annotations

import os

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .. import props
from ..pipeline import stage_identify


def _report(op, res) -> bool:
    """Report a stage result; returns False only for real failures.

    Mapping-check findings (codes ``mapping.*``) are results shown in the
    panel, not operator failures, so they never raise when called from scripts.
    """
    failures = [m for m in res.messages if m.level == 'error' and not m.code.startswith("mapping.")]
    findings = [m for m in res.messages if m.level == 'error' and m.code.startswith("mapping.")]
    for m in failures[:3]:
        op.report({'ERROR'}, m.text)
    if failures:
        return False
    if findings:
        op.report({'WARNING'}, f"映射检查发现 {len(findings)} 个错误，见面板里的检查结果")
    else:
        summary = next((m.text for m in res.messages if m.code.endswith("summary") or m.code.endswith("ed")), None)
        op.report({'INFO'}, summary or "完成")
    return True


def _job_or_cancel(op, context):
    job = props.active_job(context)
    if job is None:
        op.report({'ERROR'}, "没有活动任务：先选中导入的骨架或 ① 导入 XPS")
    return job


class XPS2PMX_OT_identify(bpy.types.Operator):
    """自动识别骨架：名称表 → 脊柱规则 → 拓扑补缺 → 下半身诊断 → 其余骨分类，然后检查映射"""
    bl_idname = "xps2pmx.identify"
    bl_label = "② 自动识别"
    bl_options = {'REGISTER', 'UNDO'}

    keep_user: BoolProperty(name="保留手动修改", default=True,
                            description="手动指定过的槽位不被自动识别覆盖")

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res = stage_identify.run(context, job, keep_user=self.keep_user)
        return {'FINISHED'} if _report(self, res) else {'CANCELLED'}


class XPS2PMX_OT_check_mapping(bpy.types.Operator):
    """按当前映射（含手动修改）重新运行映射检查"""
    bl_idname = "xps2pmx.check_mapping"
    bl_label = "检查映射"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res = stage_identify.recheck(context, job)
        return {'FINISHED'} if _report(self, res) else {'CANCELLED'}


class XPS2PMX_OT_slot_pick(bpy.types.Operator):
    """用当前选中的骨填这个槽位"""
    bl_idname = "xps2pmx.slot_pick"
    bl_label = "取选中骨"
    bl_options = {'REGISTER', 'UNDO'}

    slot_id: StringProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        arm = job.armature
        name = ""
        if context.active_pose_bone is not None and context.active_object == arm:
            name = context.active_pose_bone.name
        elif context.active_bone is not None and context.active_object == arm:
            name = context.active_bone.name
        elif arm is not None and arm.data.bones.active is not None:
            name = arm.data.bones.active.name
        if not name:
            self.report({'ERROR'}, "先在骨架里选中一根骨")
            return {'CANCELLED'}
        slot = job.slot(self.slot_id)
        if slot is None:
            self.report({'ERROR'}, f"未知槽位 {self.slot_id}（先 ② 自动识别）")
            return {'CANCELLED'}
        slot.bone = name  # update callback marks it as user-edited
        return {'FINISHED'}


class XPS2PMX_OT_slot_clear(bpy.types.Operator):
    """清空这个槽位（缺失时按规则生成，或在检查里报告）"""
    bl_idname = "xps2pmx.slot_clear"
    bl_label = "清空槽位"
    bl_options = {'REGISTER', 'UNDO'}

    slot_id: StringProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        slot = job.slot(self.slot_id) if job else None
        if slot is None:
            return {'CANCELLED'}
        slot.bone = ""
        return {'FINISHED'}


class XPS2PMX_OT_locate_bone(bpy.types.Operator):
    """在视口里选中这根骨"""
    bl_idname = "xps2pmx.locate_bone"
    bl_label = "定位"

    bone: StringProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        arm = job.armature if job else None
        if arm is None or self.bone not in arm.data.bones:
            self.report({'WARNING'}, f"骨架里没有 {self.bone}")
            return {'CANCELLED'}
        if context.mode not in ('OBJECT', 'POSE'):
            bpy.ops.object.mode_set(mode='OBJECT')
        for obj in context.view_layer.objects:
            obj.select_set(False)
        arm.select_set(True)
        context.view_layer.objects.active = arm
        for b in arm.data.bones:
            b.select = False
        bone = arm.data.bones[self.bone]
        bone.hide = False
        bone.select = True
        arm.data.bones.active = bone
        if context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')
        area = next((a for a in context.screen.areas if a.type == 'VIEW_3D'), None) if context.screen else None
        if area is not None:
            region = next((r for r in area.regions if r.type == 'WINDOW'), None)
            with context.temp_override(area=area, region=region):
                bpy.ops.view3d.view_selected()
        return {'FINISHED'}


class XPS2PMX_OT_mapping_export(bpy.types.Operator, ExportHelper):
    """把当前映射（每根源骨一行）导出为 CSV"""
    bl_idname = "xps2pmx.mapping_export"
    bl_label = "导出映射CSV"

    filename_ext = ".csv"
    filter_glob: StringProperty(default="*.csv", options={'HIDDEN'})

    def invoke(self, context, event):
        job = props.active_job(context)
        if job is not None and not self.filepath:
            self.filepath = f"{job.model_name}.mapping.csv"
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res = stage_identify.export_csv(context, job, self.filepath)
        _report(self, res)
        return {'FINISHED'}


class XPS2PMX_OT_mapping_import(bpy.types.Operator, ImportHelper):
    """导入映射 CSV（本插件导出的格式，或“源骨,日文名”两列格式），导入的行标记为手动"""
    bl_idname = "xps2pmx.mapping_import"
    bl_label = "导入映射CSV"

    filename_ext = ".csv"
    filter_glob: StringProperty(default="*.csv;*.txt", options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None or not os.path.isfile(self.filepath):
            return {'CANCELLED'}
        res = stage_identify.import_csv(context, job, self.filepath)
        _report(self, res)
        return {'FINISHED'}


class XPS2PMX_OT_mapping_reset_user(bpy.types.Operator):
    """清除所有手动修改，重新自动识别"""
    bl_idname = "xps2pmx.mapping_reset_user"
    bl_label = "清除手动修改"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res = stage_identify.run(context, job, keep_user=False)
        _report(self, res)
        return {'FINISHED'}


CLASSES = (XPS2PMX_OT_identify, XPS2PMX_OT_check_mapping, XPS2PMX_OT_slot_pick, XPS2PMX_OT_slot_clear,
           XPS2PMX_OT_locate_bone, XPS2PMX_OT_mapping_export, XPS2PMX_OT_mapping_import,
           XPS2PMX_OT_mapping_reset_user)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
