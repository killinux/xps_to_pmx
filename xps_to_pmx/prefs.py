"""Add-on preferences: where user data and exports go (outside the add-on folder)."""
from __future__ import annotations

import os

import bpy
from bpy.props import StringProperty


def default_user_data_dir() -> str:
    try:
        return bpy.utils.user_resource('CONFIG', path="xps_to_pmx")
    except TypeError:  # very old signature
        return os.path.join(bpy.utils.user_resource('CONFIG'), "xps_to_pmx")


class XPS2PMX_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    export_root: StringProperty(
        name="PMX 输出根目录", subtype='DIR_PATH', default=r"D:\xps_exports",
        description="导出时写到 <根目录>\\<模型名>\\<模型名>.pmx，不写回 XPS 源目录")
    user_data_dir: StringProperty(
        name="用户数据目录", subtype='DIR_PATH', default="",
        description="放用户自己的 CSV 覆盖表与映射记录；留空 = Blender 配置目录下的 xps_to_pmx")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "export_root")
        layout.prop(self, "user_data_dir")
        layout.label(text=f"当前用户数据目录：{user_data_dir(context)}")


def get(context: bpy.types.Context) -> XPS2PMX_Preferences:
    return context.preferences.addons[__package__].preferences


def user_data_dir(context: bpy.types.Context) -> str:
    try:
        configured = get(context).user_data_dir
    except KeyError:  # add-on loaded without being enabled (tests)
        configured = ""
    return bpy.path.abspath(configured) if configured else default_user_data_dir()


CLASSES = (XPS2PMX_Preferences,)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
