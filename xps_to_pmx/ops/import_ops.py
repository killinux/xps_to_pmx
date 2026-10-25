"""Operators for stage ① (thin wrappers around :mod:`pipeline.stage_import`)."""
from __future__ import annotations

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper

from .. import props
from ..pipeline import stage_import


def _report_result(op: bpy.types.Operator, res) -> None:
    for msg in res.messages:
        if msg.level == 'error':
            op.report({'ERROR'}, msg.text)
    if res.ok:
        last = res.messages[-1].text if res.messages else "完成"
        op.report({'INFO'}, last)


class XPS2PMX_OT_import_xps(bpy.types.Operator, ImportHelper):
    """读取 XPS 模型，建立骨架、网格、权重与预览材质，并记录高清材质清单"""
    bl_idname = "xps2pmx.import_xps"
    bl_label = "导入 XPS"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".xps"
    filter_glob: StringProperty(default="*.xps;*.mesh;*.ascii", options={'HIDDEN'})
    use_panel_path: bpy.props.BoolProperty(default=False, options={'HIDDEN', 'SKIP_SAVE'})

    def invoke(self, context, event):
        if self.use_panel_path:
            path = props.state(context).xps_path
            if path:
                self.filepath = path
                return self.execute(context)
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        res, _job = stage_import.run(context, self.filepath)
        props.state(context).xps_path = self.filepath
        _report_result(self, res)
        return {'FINISHED'} if res.ok else {'CANCELLED'}


def menu_func_import(self, context):
    self.layout.operator(XPS2PMX_OT_import_xps.bl_idname, text="XPS → PMX：XPS 模型 (.xps/.mesh/.ascii)")


CLASSES = (XPS2PMX_OT_import_xps,)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister() -> None:
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
