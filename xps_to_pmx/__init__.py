"""XPS → PMX: convert XPS / XNALara models into MMD PMX models inside Blender 3.6.

Layers (see docs/design/XPS转PMX插件实施设计_v0.3.md §3):
``core`` (pure Python, no bpy) → ``blender`` (bpy adapters; only
``blender.mmdtools_bridge`` imports mmd_tools) → ``pipeline`` (stage functions)
→ ``ops`` (operators) → ``ui`` (panels).
"""

bl_info = {
    "name": "XPS → PMX",
    "author": "xps_to_pmx contributors",
    "version": (0, 2, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > XPS→PMX；File > Import > XPS → PMX",
    "description": "把 XPS/XNALara 模型转换成 MMD PMX：骨骼识别与补全、映射检查、表情、物理、校验",
    "category": "Import-Export",
}

# Modules in dependency order; re-imported on "Reload Scripts" so edits apply without restarting.
_MODULES = (
    "core.result",
    "core.fixes",
    "core.xps.types",
    "core.xps.render_groups",
    "core.xps.reader",
    "core.xps.convert",
    "core.xps",
    "core.spec.bone_slots",
    "core.spec",
    "core.rig.rigdata",
    "core.rig.topology",
    "core.rig.limbs",
    "core.rig.lower_body",
    "core.rig.classify",
    "core.rig.identify",
    "core.checks.mapping",
    "core.checks.cause",
    "core.checks.checkup",
    "core.mapping_io",
    "core.pose",
    "core.weights.skin",
    "core.weights.rules",
    "core.weights.split",
    "core.rig.skeleton",
    "core.mmd_material",
    "core.checks.export",
    "core.checks.lower_body",
    "core.checks.posetest",
    "props",
    "prefs",
    "blender.importer",
    "blender.snapshot",
    "blender.rigedit",
    "blender.skeleton_apply",
    "blender.mmdtools_bridge",
    "blender.posetest",
    "pipeline.fixlist",
    "pipeline.stage_import",
    "pipeline.stage_identify",
    "pipeline.stage_prepare",
    "pipeline.views",
    "pipeline.stage_build",
    "pipeline.stage_export",
    "pipeline.stage_checkup",
    "pipeline.runner",
    "ops.import_ops",
    "ops.mapping_ops",
    "ops.prepare_ops",
    "ops.build_ops",
    "ops.checkup_ops",
    "ui.previews",
    "ui.panel_main",
    "ui.panel_checkup",
    "ui.panel_steps",
    "ui.panel_mapping",
    "ui.panel_prepare",
    "ui.panel_build",
)

import importlib.util as _ilu  # noqa: E402

#: ``core`` must stay importable outside Blender (offline pytest), so bpy-dependent
#: modules are only loaded when running inside Blender.
IN_BLENDER = _ilu.find_spec("bpy") is not None

if IN_BLENDER:
    if "_REGISTER_ORDER" in locals():  # "Reload Scripts": re-import edited modules in order
        import importlib
        import sys

        for _name in _MODULES:
            _mod = sys.modules.get(f"{__name__}.{_name}")
            if _mod is not None:
                importlib.reload(_mod)

    from . import prefs, props  # noqa: E402
    from .ops import build_ops, checkup_ops, import_ops, mapping_ops, prepare_ops  # noqa: E402
    from .ui import panel_build, panel_checkup, panel_main, panel_mapping, panel_prepare, panel_steps, previews  # noqa: E402

    # parents before sub-panels: main → 修正单 / 分步模式 → ② ③ ④ ⑧
    _REGISTER_ORDER = (prefs, props, import_ops, mapping_ops, prepare_ops, build_ops, checkup_ops, previews,
                       panel_main, panel_checkup, panel_steps, panel_mapping, panel_prepare, panel_build)


def register():
    if not IN_BLENDER:
        raise RuntimeError("xps_to_pmx.register() must run inside Blender")
    for module in _REGISTER_ORDER:
        module.register()


def unregister():
    for module in reversed(_REGISTER_ORDER):
        module.unregister()
