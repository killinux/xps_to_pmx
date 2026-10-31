"""Draw every panel / UIList with a recording stub layout (background Blender cannot draw UI).

Catches wrong property names, wrong operator ids and exceptions in draw code.
"""
from __future__ import annotations

import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness  # noqa: E402

import bpy  # noqa: E402

ARGS = harness.parse_args()
os.environ["XPS2PMX_EXPORT_ROOT"] = os.path.join(ARGS.out, "ui_exports")
os.environ["XPS2PMX_USER_DATA"] = os.path.join(ARGS.out, "ui_user_data")
harness.register_addon()
from xps_to_pmx.pipeline import (fixlist, stage_build, stage_checkup, stage_export, stage_identify,  # noqa: E402
                                 stage_import, stage_prepare)
from xps_to_pmx.ui import panel_build, panel_checkup, panel_main, panel_mapping, panel_prepare, panel_steps  # noqa: E402


ICONS = set(bpy.types.UILayout.bl_rna.functions['label'].parameters['icon'].enum_items.keys())


class Stub:
    """Records layout calls and validates property / operator / icon names."""

    problems = []

    @staticmethod
    def _check_icon(kwargs):
        icon = kwargs.get("icon")
        if icon is not None and icon not in ICONS:
            Stub.problems.append(f"unknown icon {icon!r}")

    def __getattr__(self, name):
        def call(*a, **k):
            Stub._check_icon(k)
            return Stub()
        return call

    def _check_prop(self, data, prop):
        if data is not None and not hasattr(data, prop):
            Stub.problems.append(f"{type(data).__name__} has no property {prop!r}")

    def prop(self, data, prop, *a, **k):
        self._check_prop(data, prop)
        self._check_icon(k)
        return Stub()

    def prop_search(self, data, prop, search_data, search_prop, *a, **k):
        self._check_prop(data, prop)
        self._check_prop(search_data, search_prop)
        return Stub()

    def operator(self, idname, *a, **k):
        self._check_icon(k)
        mod, _, op = idname.partition(".")
        if not hasattr(getattr(bpy.ops, mod), op):
            Stub.problems.append(f"unknown operator {idname}")
        return types.SimpleNamespace()

    def template_list(self, list_id, list_name, data, prop, active_data, active_prop, *a, **k):
        if not hasattr(bpy.types, list_id):
            Stub.problems.append(f"unknown UIList {list_id}")
        self._check_prop(data, prop)
        self._check_prop(active_data, active_prop)
        return Stub()


def draw_panel(cls, context):
    panel = types.SimpleNamespace(layout=Stub())
    if hasattr(cls, "poll") and not cls.poll(context):
        return False
    cls.draw(panel, context)
    return True


def main():
    args = ARGS
    checkers = []
    c = harness.Checker("ui")
    checkers.append(c)

    harness.reset_scene()
    c.run("main panel without a job", draw_panel, panel_main.XPS2PMX_PT_main, bpy.context)
    c.run("steps panel without a job", draw_panel, panel_steps.XPS2PMX_PT_steps, bpy.context)
    model = next((m for m in harness.regression_models(args.models) if os.path.isfile(m["path"])), None)
    if model is None:
        c.check("a regression model exists", False)
    else:
        res, job = stage_import.run(bpy.context, model["path"])
        bpy.context.view_layer.objects.active = job.armature
        c.run("main panel after import", draw_panel, panel_main.XPS2PMX_PT_main, bpy.context)
        c.run("mapping panel before identify", draw_panel, panel_mapping.XPS2PMX_PT_mapping, bpy.context)
        c.run("fixes panel, empty", draw_panel, panel_checkup.XPS2PMX_PT_fixes, bpy.context)
        c.run("steps panel after import", draw_panel, panel_steps.XPS2PMX_PT_steps, bpy.context)
        stage_identify.run(bpy.context, job)
        job.slot("left_toe_bone").bone = ""          # a hand edit → one fix in the list
        c.run("mapping panel after identify", draw_panel, panel_mapping.XPS2PMX_PT_mapping, bpy.context)
        fake = types.SimpleNamespace(filter_name="", bitflag_filter_item=1 << 30)
        bones_ul, checks_ul = panel_mapping.XPS2PMX_UL_bones, panel_mapping.XPS2PMX_UL_checks
        for item in list(job.bones)[:20]:
            c.run("bones list item", bones_ul.draw_item, fake, bpy.context, Stub(), job, item, 0, job,
                  "bones_index", 0)
        for item in job.checks:
            c.run("checks list item", checks_ul.draw_item, fake, bpy.context, Stub(), job, item, 0, job,
                  "checks_index", 0)
        for mode in ('UNMAPPED', 'merge', 'keep', 'delete', 'ALL'):
            job.bones_filter = mode
            flags = c.run("bones filter", bones_ul.filter_items, fake, bpy.context, job, "bones")
            if flags is not None:
                c.check(f"filter {mode} returns one flag per item", len(flags[0]) == len(job.bones))
        c.run("prepare panel", draw_panel, panel_prepare.XPS2PMX_PT_prepare, bpy.context)
        c.run("build panel before build", draw_panel, panel_build.XPS2PMX_PT_build, bpy.context)
        c.run("export panel before build", draw_panel, panel_build.XPS2PMX_PT_export, bpy.context)
        res = stage_prepare.run(bpy.context, job)
        c.run("prepare panel after prepare", draw_panel, panel_prepare.XPS2PMX_PT_prepare, bpy.context)
        res = stage_build.run(bpy.context, job)
        c.check("build ran for the panel test", res.ok, [m.text for m in res.messages if m.level == 'error'][:3])
        bpy.context.view_layer.objects.active = job.armature
        c.run("build panel after build", draw_panel, panel_build.XPS2PMX_PT_build, bpy.context)
        c.run("export panel after build", draw_panel, panel_build.XPS2PMX_PT_export, bpy.context)
        c.run("main panel after build", draw_panel, panel_main.XPS2PMX_PT_main, bpy.context)
        c.run("mapping panel after build", draw_panel, panel_mapping.XPS2PMX_PT_mapping, bpy.context)
        res = stage_export.run(bpy.context, job, "")
        c.check("export ran for the panel test", res.ok, [m.text for m in res.messages if m.level == 'error'][:3])
        res = stage_checkup.run(bpy.context, job)
        c.check("checkup ran for the panel test", res.ok and len(job.findings) > 0, len(job.findings))
        fix_finding = next((i for i, f in enumerate(job.findings) if f.fix_key), None)
        if fix_finding is not None:
            fixlist.toggle_finding_fix(bpy.context, job, fix_finding)
        c.run("main panel after the checkup", draw_panel, panel_main.XPS2PMX_PT_main, bpy.context)
        c.run("fixes panel with entries", draw_panel, panel_checkup.XPS2PMX_PT_fixes, bpy.context)
        findings_ul, fixes_ul = panel_main.XPS2PMX_UL_findings, panel_checkup.XPS2PMX_UL_fixes
        for i, item in enumerate(job.findings):
            c.run("findings list item", findings_ul.draw_item, fake, bpy.context, Stub(), job, item, 0, job,
                  "findings_index", i)
        for i, item in enumerate(job.fixes):
            c.run("fixes list item", fixes_ul.draw_item, fake, bpy.context, Stub(), job, item, 0, job,
                  "fixes_index", i)
        c.check("fix list has the hand edit", job.fix_item("slot:left_toe_bone") is not None,
                [f.key for f in job.fixes])
    c.check("no layout problems", not Stub.problems, sorted(set(Stub.problems))[:10])
    report = harness.write_report(args.out, "ui_draw", checkers)
    harness.finish(report)


main()
