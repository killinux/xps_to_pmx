"""Main sidebar panel (tab "XPS→PMX"): one-click, the checkup report, redo buttons (design doc §15.8).

Reads properties and calls operators only.
"""
from __future__ import annotations

import json
import re

import bpy

from .. import props
from ..core.checks.checkup import PART_LABELS
from ..core.fixes import Fix

LEVEL_ICONS = {'info': 'INFO', 'warning': 'ERROR', 'error': 'CANCEL'}
STATE_PREFIX = {'new': "", 'remaining': "", 'fixed': "已修复 · ", 'auto_fixed': "已自动修正 · "}
MAX_REPORT_LINES = 8
#: Width of one CJK character in pixels at UI scale 1 (labels wrap to the sidebar's real width).
CHAR_PX = 13.0
#: Stage report lines that explain decisions rather than problems (also left out of the checkup).
QUIET_CODES = ("mapping.disagreement",)
NEXT_STEP = {
    "": "下一步：点「一键转换」",
    "import": "下一步：点「继续」，或展开「分步模式」逐步做",
    "identify": "下一步：点「继续」；要改映射先展开「分步模式」",
    "prepare": "下一步：点「继续」",
    "build": "下一步：点「继续」导出并体检",
    "export": "下一步：点「继续」体检",
    "checkup": "看体检报告：勾选修正后点「按修正从头重做」；没有问题就到 MMD 里测试",
}


def draw_report(layout, job, stage: str = "") -> None:
    lines = [r for r in job.reports if (not stage or r.stage == stage) and r.code not in QUIET_CODES]
    if not lines:
        return
    box = layout.box()
    shown = sorted(lines, key=lambda r: {'error': 0, 'warning': 1, 'info': 2}[r.level])[:MAX_REPORT_LINES]
    for r in shown:
        box.label(text=r.text, icon=LEVEL_ICONS.get(r.level, 'INFO'))
    if len(lines) > len(shown):
        box.label(text=f"…另有 {len(lines) - len(shown)} 条，见报告 JSON")


def wrap_width(context) -> int:
    """Characters per label line that fit the current region (CJK-width estimate, icon column excluded)."""
    region = getattr(context, "region", None)
    width = getattr(region, "width", 0) or 360
    scale = context.preferences.system.ui_scale or context.preferences.view.ui_scale or 1.0  # 0 without a display
    return max(10, int((width - 40 * scale) / (CHAR_PX * scale)))


def wrap_lines(text: str, width: int) -> list:
    """Greedy wrap: CJK characters count 1, ASCII 0.55; ASCII words are not split unless longer than a line."""
    lines, line, used = [], "", 0.0
    for token in re.findall(r"[A-Za-z0-9_.\-/]+|\s+|.", text):
        w = sum(0.55 if ord(ch) < 128 else 1.0 for ch in token)
        if used + w > width and line.strip():
            lines.append(line.rstrip())
            line, used = "", 0.0
            if token.isspace():
                continue
        while w > width:  # a single ASCII run longer than a line
            cut = int(width / 0.55)
            lines.append(token[:cut])
            token = token[cut:]
            w = sum(0.55 if ord(ch) < 128 else 1.0 for ch in token)
        line += token
        used += w
    if line.strip():
        lines.append(line.rstrip())
    return lines or [""]


def wrapped(layout, text: str, icon: str = 'NONE', width: int = 24) -> None:
    for i, line in enumerate(wrap_lines(text, width)):
        layout.label(text=line, icon=icon if i == 0 else 'BLANK1')


def fix_line(job, fix_json: str) -> str:
    if not fix_json:
        return ""
    try:
        fix = Fix(**json.loads(fix_json))
    except (TypeError, ValueError):
        return ""

    def slot_name(slot_id: str) -> str:
        slot = job.slot(slot_id)
        return slot.name_j if slot is not None and slot.name_j else slot_id
    return fix.describe(slot_name)


def finding_counts(job) -> dict:
    out = {'error': 0, 'warning': 0, 'info': 0, 'fixed': 0, 'auto_fixed': 0}
    for f in job.findings:
        out[f.state if f.state in ('fixed', 'auto_fixed') else f.level] += 1
    return out


class XPS2PMX_UL_findings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        job = data
        row = layout.row(align=True)
        if item.state == 'fixed':
            icon = 'CHECKMARK'
        elif item.state == 'auto_fixed':
            icon = 'AUTO'
        else:
            icon = LEVEL_ICONS.get(item.level, 'INFO')
        part = PART_LABELS.get(item.part, "")
        row.label(text=f"{STATE_PREFIX.get(item.state, '')}{part}：{item.text}", icon=icon)
        if item.fix_key and item.state != 'fixed':
            fix = job.fix_item(item.fix_key)
            on = fix is not None and fix.enabled
            op = row.operator("xps2pmx.finding_fix", text="", icon='CHECKBOX_HLT' if on else 'CHECKBOX_DEHLT')
            op.index = index
        if item.target:
            op = row.operator("xps2pmx.locate_bone", text="", icon='VIEWZOOM')
            op.bone = item.target
        if item.state not in ('fixed', 'auto_fixed'):
            op = row.operator("xps2pmx.finding_ignore", text="", icon='HIDE_ON')
            op.index = index


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
        op = row.operator("xps2pmx.one_click", text="一键转换", icon='PLAY')
        op.use_panel_path = True

        job = props.active_job(context)
        if job is None:
            layout.label(text="还没有转换任何模型", icon='INFO')
            return
        info = job.summary().get("import", {})
        box = layout.box()
        box.label(text=f"{job.model_name}", icon='ARMATURE_DATA')
        if info:
            box.label(text=f"{info.get('bones', 0)} 骨 · {info.get('meshes', 0)} 网格 · "
                           f"{info.get('vertices', 0)} 顶点 · XPS {info.get('version', '')}")
        enabled = sum(1 for f in job.fixes if f.enabled)
        box.label(text=f"已完成：{props.STAGE_LABELS.get(job.stage, '—')}    修正单 {enabled} 条")

        if job.findings:
            c = finding_counts(job)
            text = f"体检：✗{c['error']}  ⚠{c['warning']}  ℹ{c['info']}"
            if c['auto_fixed']:
                text += f" · 已自动修正 {c['auto_fixed']}"
            if c['fixed']:
                text += f" · 比上次修好 {c['fixed']}"
            layout.label(text=text, icon='VIEWZOOM')
            layout.template_list("XPS2PMX_UL_findings", "", job, "findings", job, "findings_index", rows=6)
            if 0 <= job.findings_index < len(job.findings):
                item = job.findings[job.findings_index]
                detail = layout.box().column(align=True)
                width = wrap_width(context)
                wrapped(detail, item.text, LEVEL_ICONS.get(item.level, 'INFO'), width)
                if item.detail:
                    wrapped(detail, item.detail, 'DOT', width)
                line = fix_line(job, item.fix_json)
                if line:
                    wrapped(detail, f"修正：{line}", 'MODIFIER', width)
        else:
            draw_report(layout, job, stage=job.stage)

        row = layout.row(align=True)
        row.operator("xps2pmx.redo_full", text="按修正从头重做", icon='FILE_REFRESH')
        row.operator("xps2pmx.redo_steps", text="分步重做", icon='MODIFIER')
        sub = row.row(align=True)
        sub.enabled = job.stage not in props.BUILT_STAGES
        sub.operator("xps2pmx.continue_run", text="继续", icon='FORWARD')
        if job.fixes_pending:
            layout.label(text="修正单改过，点「按修正从头重做」才生效", icon='ERROR')
        layout.label(text=NEXT_STEP.get(job.stage, ""), icon='FORWARD')


CLASSES = (XPS2PMX_UL_findings, XPS2PMX_PT_main)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
