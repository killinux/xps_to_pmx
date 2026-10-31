"""Operators for the one-click flow, the checkup report and the fix list (design doc §15)."""
from __future__ import annotations

import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty
from bpy_extras.io_utils import ExportHelper, ImportHelper

from .. import props
from ..pipeline import fixlist, runner, views


def _activate(context, job) -> None:
    if job is not None and job.armature is not None:
        for obj in context.view_layer.objects:
            obj.select_set(False)
        context.view_layer.objects.active = job.armature
        job.armature.select_set(True)


def _finish(op, res) -> set:
    errors = [m for m in res.messages if m.level == 'error']
    for m in errors[-3:]:
        op.report({'ERROR'}, m.text)
    if errors:
        return {'CANCELLED'}
    done = next((m.text for m in res.messages if m.code in ("run.done", "run.at_identify")), "完成")
    warnings = [m for m in res.messages if m.level == 'warning']
    op.report({'WARNING'} if warnings else {'INFO'}, done)
    return {'FINISHED'}


def _job_or_cancel(op, context):
    job = props.active_job(context)
    if job is None:
        op.report({'ERROR'}, "没有活动任务：先选中模型或一键转换")
    return job


class XPS2PMX_OT_one_click(bpy.types.Operator, ImportHelper):
    """导入 XPS，套用记住的修正单，依次 ② 识别（含自动修正）③ 预处理 ④ 生成骨架 ⑧ 导出 ⑨ 体检"""
    bl_idname = "xps2pmx.one_click"
    bl_label = "一键转换"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".xps"
    filter_glob: StringProperty(default="*.xps;*.mesh;*.ascii", options={'HIDDEN'})
    use_panel_path: BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})

    def invoke(self, context, event):
        if self.use_panel_path:
            path = props.state(context).xps_path
            if path:
                self.filepath = path
                return self.execute(context)
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        props.state(context).xps_path = self.filepath
        res, job = runner.one_click(context, self.filepath)
        _activate(context, job)
        return _finish(self, res)


class XPS2PMX_OT_redo_full(bpy.types.Operator):
    """删除本任务生成的对象，重新导入同一个 XPS，按当前修正单和选项跑到 ⑨ 体检，并与上一次体检对比"""
    bl_idname = "xps2pmx.redo_full"
    bl_label = "按修正从头重做"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res, new = runner.redo(context, job, stop_after="checkup")
        _activate(context, new)
        return _finish(self, res)


class XPS2PMX_OT_redo_steps(bpy.types.Operator):
    """同「按修正从头重做」，但停在 ②：在「分步模式」里改映射，改完点「继续」"""
    bl_idname = "xps2pmx.redo_steps"
    bl_label = "分步重做"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res, new = runner.redo(context, job, stop_after="identify")
        _activate(context, new)
        return _finish(self, res)


class XPS2PMX_OT_continue(bpy.types.Operator):
    """从当前阶段一直做到 ⑨ 体检（还没生成骨架的任务可用）"""
    bl_idname = "xps2pmx.continue_run"
    bl_label = "继续"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        job = props.active_job(context)
        return job is not None and job.armature is not None and job.stage not in props.BUILT_STAGES

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        return _finish(self, runner.continue_job(context, job))


class XPS2PMX_OT_finding_fix(bpy.types.Operator):
    """把这条结果的修正记入修正单，或者切换启用/撤销（从头重做后生效）"""
    bl_idname = "xps2pmx.finding_fix"
    bl_label = "修正"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        text = fixlist.toggle_finding_fix(context, job, self.index)
        if text:
            self.report({'INFO'}, text)
        return {'FINISHED'}


class XPS2PMX_OT_finding_ignore(bpy.types.Operator):
    """以后不再报这条结果（记入修正单，可以在修正单里删掉）"""
    bl_idname = "xps2pmx.finding_ignore"
    bl_label = "忽略"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        text = fixlist.ignore_finding(context, job, self.index)
        if text:
            self.report({'INFO'}, text)
        return {'FINISHED'}


class XPS2PMX_OT_finding_locate(bpy.types.Operator):
    """摆出这条结果的测试姿势，选中出问题的顶点，镜头对过去（模型本身不动，看完点「复位」）；没有姿势的结果选中相关的骨"""
    bl_idname = "xps2pmx.finding_locate"
    bl_label = "定位"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None or not 0 <= self.index < len(job.findings):
            return {'CANCELLED'}
        item = job.findings[self.index]
        job.findings_index = self.index
        if not item.view_json:
            if not item.target:
                self.report({'WARNING'}, "这条结果没有可以定位的骨或顶点")
                return {'CANCELLED'}
            views.clear_preview(context, job)
            return bpy.ops.xps2pmx.locate_bone(bone=item.target)
        return _finish_view(self, views.locate(context, job, self.index))


class XPS2PMX_OT_pose_reset(bpy.types.Operator):
    """去掉定位时的姿势预览，显示原来的模型（预览的是副本，模型本身一直没动）"""
    bl_idname = "xps2pmx.pose_reset"
    bl_label = "复位"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        return _finish_view(self, views.reset(context, job))


class XPS2PMX_OT_finding_render(bpy.types.Operator):
    """渲染这条结果的测试姿势小图；从头重做以后，旁边会放上一次的图做对比"""
    bl_idname = "xps2pmx.finding_render"
    bl_label = "看图"

    index: IntProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None or not 0 <= self.index < len(job.findings):
            return {'CANCELLED'}
        job.findings_index = self.index
        return _finish_view(self, views.render_finding(context, job, self.index))


def _finish_view(op, res) -> set:
    for m in res.messages:
        op.report({'ERROR'} if m.level == 'error' else {'WARNING'} if m.level == 'warning' else {'INFO'}, m.text)
    return {'CANCELLED'} if not res.ok else {'FINISHED'}


class XPS2PMX_OT_fix_remove(bpy.types.Operator):
    """从修正单删掉这一条（自动修正只撤销、保留记录）"""
    bl_idname = "xps2pmx.fix_remove"
    bl_label = "删除修正"
    bl_options = {'REGISTER', 'UNDO'}

    index: IntProperty(options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        text = fixlist.remove_fix(context, job, self.index)
        if text:
            self.report({'INFO'}, text)
        return {'FINISHED'}


class XPS2PMX_OT_fixes_export(bpy.types.Operator, ExportHelper):
    """把修正单（含这个模型的选项）导出为 JSON"""
    bl_idname = "xps2pmx.fixes_export"
    bl_label = "导出修正单"

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def invoke(self, context, event):
        job = props.active_job(context)
        if job is not None and not self.filepath:
            self.filepath = f"{job.model_name}.fixes.json"
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res = fixlist.export_file(context, job, self.filepath)
        self.report({'INFO'}, res.messages[-1].text if res.messages else "完成")
        return {'FINISHED'}


class XPS2PMX_OT_fixes_import(bpy.types.Operator, ImportHelper):
    """导入修正单 JSON，按条合并进当前修正单（同一件事以导入的为准）"""
    bl_idname = "xps2pmx.fixes_import"
    bl_label = "导入修正单"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    def execute(self, context):
        job = _job_or_cancel(self, context)
        if job is None:
            return {'CANCELLED'}
        res = fixlist.load_file(context, job, self.filepath)
        for m in res.messages:
            self.report({'WARNING'} if m.level != 'info' else {'INFO'}, m.text)
        if job.stage in props.BUILT_STAGES:
            job.fixes_pending = True
        return {'FINISHED'}


CLASSES = (XPS2PMX_OT_one_click, XPS2PMX_OT_redo_full, XPS2PMX_OT_redo_steps, XPS2PMX_OT_continue,
           XPS2PMX_OT_finding_fix, XPS2PMX_OT_finding_ignore, XPS2PMX_OT_finding_locate, XPS2PMX_OT_pose_reset,
           XPS2PMX_OT_finding_render, XPS2PMX_OT_fix_remove, XPS2PMX_OT_fixes_export, XPS2PMX_OT_fixes_import)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
