"""Raw screenshots for docs/使用说明.md, taken in a real Blender window (called by make_guide_screenshots.py).

    blender --factory-startup --enable-event-simulate -p 0 0 1600 1000 --python scripts/guide_shots_blender.py ^
        -- --out <folder> --xps <file.xps> [--measure]

The window is driven with simulated events (it ignores the mouse and keyboard while it runs): the
script widens the sidebar, opens the XPS→PMX tab, converts the model, ticks fixes, redoes, and saves
one window screenshot per step plus ``log.txt``.  Exports and fix files go to ``<folder>/work``.

Python cannot read or set where a panel header is or whether a panel is open, so the header click
positions are measured: ``--measure`` skips those clicks; read the positions off the shots and update
HEADER_CLICKS.  Whether a panel really opened is checked by watching its ``draw`` calls.  Measured
2026-10-31 on a 1600×1000 window, Windows display scale 150 %, Blender UI scale 0.85.
"""
import argparse
import os
import shutil
import sys
import time
import traceback

import addon_utils
import bpy

WIDTH, HEIGHT = 1600, 1000      # must match the -p window geometry
UI_SCALE = 0.85
SIDEBAR_WIDTH = 478
#: Window positions (origin top-left) of panel headers in the state where they are clicked.
HEADER_CLICKS = {
    "fixes": (1230, 850),        # 「修正单」 after the two fixes are ticked (05_ticked.png)
    "steps": (1220, 544),        # 「分步模式（高级）」 after 分步重做 (08_at_identify.png)
}
MAPPING_SCROLLS = (0, 10, 10, 10)   # wheel steps between the 10_mapping_*.png shots
BONES_SCROLL = 10
BONE_TO_SHOW = "unused bip001 lcalftwist"

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--xps", required=True)
ap.add_argument("--measure", action="store_true", help="do not click panel headers")
ARGS = ap.parse_args(argv)
WORK = os.path.join(ARGS.out, "work")
shutil.rmtree(ARGS.out, ignore_errors=True)
os.makedirs(WORK)
os.environ["XPS2PMX_EXPORT_ROOT"] = os.path.join(WORK, "exports")
os.environ["XPS2PMX_USER_DATA"] = os.path.join(WORK, "user_data")

prefs = bpy.context.preferences
prefs.use_preferences_save = False   # factory settings must never overwrite the user's preferences
prefs.view.show_splash = False       # the splash lists recent files, and changing screens under it crashes
prefs.view.ui_scale = UI_SCALE
LOG = open(os.path.join(ARGS.out, "log.txt"), "w", encoding="utf-8")


def log(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
    LOG.flush()


addon_utils.enable("xps_to_pmx", default_set=True)
# mmd_tools is enabled by ④ itself; enabling it here would add an "MMD" tab before the shots
from xps_to_pmx.ui import panel_checkup, panel_main, panel_steps  # noqa: E402

DRAWN = {}


def watch(cls, key):
    """Record when a panel draws: only the active tab's panels and open sub-panels are drawn."""
    original = cls.draw

    def draw(self, context):
        DRAWN[key] = time.monotonic()
        original(self, context)
    cls.draw = draw


watch(panel_main.XPS2PMX_PT_main, "main")
watch(panel_checkup.XPS2PMX_PT_fixes, "fixes")
watch(panel_steps.XPS2PMX_PT_steps, "steps")


def ctx():
    win = bpy.context.window_manager.windows[0]
    area = next(a for a in win.screen.areas if a.type == 'VIEW_3D')
    ui = next(r for r in area.regions if r.type == 'UI')
    main = next(r for r in area.regions if r.type == 'WINDOW')
    return win, area, ui, main


def redraw():
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            a.tag_redraw()


def shot(name, win=None):
    win = win or bpy.context.window_manager.windows[0]
    with bpy.context.temp_override(window=win, area=win.screen.areas[0]):
        bpy.ops.screen.screenshot(filepath=os.path.join(ARGS.out, name))
    log("shot", name)


def click(win, x, y):
    """x, y in window coordinates with the origin at the top left (as in the screenshots)."""
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=int(x), y=int(HEIGHT - y))
    yield 0.15
    win.event_simulate(type='LEFTMOUSE', value='PRESS', x=int(x), y=int(HEIGHT - y))
    yield 0.08
    win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=int(x), y=int(HEIGHT - y))
    redraw()
    yield 0.5


def scroll(win, x, y, steps):
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=int(x), y=int(HEIGHT - y))
    yield 0.1
    kind = 'WHEELDOWNMOUSE' if steps > 0 else 'WHEELUPMOUSE'
    for _ in range(abs(steps)):
        win.event_simulate(type=kind, value='PRESS', x=int(x), y=int(HEIGHT - y))
        yield 0.05
    redraw()
    yield 0.4


def toggle_header(win, key, opening=True):
    """Click a sub-panel header; when opening, report whether it opened (a sub-panel draws only when open)."""
    if ARGS.measure:
        return
    started = time.monotonic()
    yield from click(win, *HEADER_CLICKS[key])
    yield 0.3
    if opening and DRAWN.get(key, 0) < started:
        log(f"WARNING: header '{key}' not hit at {HEADER_CLICKS[key]}; run with --measure and update HEADER_CLICKS")


def op(name, **kw):
    win, area, ui, main = ctx()
    module, func = name.split(".")
    with bpy.context.temp_override(window=win, area=area, region=main):
        getattr(getattr(bpy.ops, module), func)('EXEC_DEFAULT', **kw)


def job():
    st = bpy.context.scene.xps2pmx
    return st.jobs[-1] if st.jobs else None


def frame_model():
    """Front view of the model, textures on, bones hidden; the armature stays active but unselected."""
    win, area, ui, main = ctx()
    j = job()
    if j is not None and j.armature is not None:
        for obj in bpy.context.view_layer.objects:
            obj.select_set(False)
        bpy.context.view_layer.objects.active = j.armature   # the panel follows the active object
    space = area.spaces.active
    space.shading.type = 'SOLID'
    space.shading.color_type = 'TEXTURE'
    space.overlay.show_floor = False
    space.overlay.show_axis_x = space.overlay.show_axis_y = False
    space.overlay.show_bones = False
    with bpy.context.temp_override(window=win, area=area, region=main):
        bpy.ops.view3d.view_axis(type='FRONT')
        bpy.ops.view3d.view_all(center=False)


def widen_sidebar():
    """There is no API for region width: drag the sidebar's visible left edge (8–11 px inside the region)."""
    for attempt in range(12):
        win, area, ui, main = ctx()
        if ui.width >= SIDEBAR_WIDTH - 4:
            return
        x, y = ui.x + (8, 9, 10, 11)[attempt % 4], ui.y + ui.height // 2
        dx = SIDEBAR_WIDTH - ui.width
        win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x + 30, y=y)
        yield 0.2
        win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x, y=y)
        yield 0.25
        win.event_simulate(type='LEFTMOUSE', value='PRESS', x=x, y=y)
        yield 0.2
        for k in range(1, 11):
            win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=x - dx * k // 10, y=y)
            yield 0.03
        win.event_simulate(type='LEFTMOUSE', value='RELEASE', x=x - dx, y=y)
        yield 0.5
    log("WARNING: could not widen the sidebar")


def open_tab():
    """Click down the tab column until the XPS→PMX panel draws (the column holds only tabs)."""
    win, area, ui, main = ctx()
    x = ui.x + ui.width - 8
    top = HEIGHT - (ui.y + ui.height)
    for k in range(60):
        started = time.monotonic()
        yield from click(win, x, top + 10 + 12 * k)
        if DRAWN.get("main", 0) >= started:
            log("tab found at", (x, top + 10 + 12 * k))
            return
    log("WARNING: XPS→PMX tab not found")


def shots():
    win, area, ui, main = ctx()
    with bpy.context.temp_override(window=win, area=area):
        bpy.ops.screen.screen_full_area()
    yield 1.0
    win, area, ui, main = ctx()
    area.spaces.active.show_region_ui = True
    yield 0.6
    yield from widen_sidebar()     # in the factory scene: its Item tab keeps the tab layout predictable
    yield from open_tab()
    for obj in list(bpy.data.objects):  # the factory cube, camera and light would crowd the view
        bpy.data.objects.remove(obj)
    yield 0.5
    win, area, ui, main = ctx()
    log("sidebar", ui.x, ui.width)

    # 1 enabling the add-on
    prefs.active_section = 'ADDONS'
    bpy.context.window_manager.addon_search = "XPS →"
    bpy.ops.screen.userpref_show()
    yield 1.5
    prefs_win = bpy.context.window_manager.windows[-1]
    shot("01_prefs.png", prefs_win)
    with bpy.context.temp_override(window=prefs_win):
        bpy.ops.wm.window_close()
    yield 0.8

    # 2 the empty panel with the file path filled in
    bpy.context.scene.xps2pmx.xps_path = ARGS.xps
    redraw()
    yield 0.8
    shot("02_empty.png")

    # 3 one-click and the report
    op("xps2pmx.one_click", filepath=ARGS.xps)
    yield 0.5
    frame_model()
    yield 1.0
    j = job()
    log("findings", [(f.level, f.code, f.state) for f in j.findings])
    j.findings_index = 0
    redraw()
    yield 0.8
    shot("03_report.png")

    # 4 one finding in detail: the first duplicate-name finding
    dup = [i for i, f in enumerate(j.findings) if f.code == "mapping.duplicate_name"]
    if dup:
        j.findings_index = dup[0]
    redraw()
    yield 0.8
    shot("04_detail.png")

    # 5 tick their fixes
    for i in dup:
        op("xps2pmx.finding_fix", index=i)
    redraw()
    yield 0.8
    shot("05_ticked.png")

    # 6 the fix list
    yield from toggle_header(win, "fixes")
    redraw()
    yield 0.8
    shot("06_fixlist.png")
    yield from toggle_header(win, "fixes", opening=False)      # fold it again

    # 7 redo from scratch: the report compares with the last one
    op("xps2pmx.redo_full")
    yield 0.5
    frame_model()
    yield 1.0
    j = job()
    log("after redo", [(f.level, f.code, f.state) for f in j.findings])
    fixed = [i for i, f in enumerate(j.findings) if f.state == "fixed"]
    j.findings_index = fixed[0] if fixed else 0
    redraw()
    yield 0.8
    shot("07_after_redo.png")

    # 8 分步重做 stops at ②; the step panels
    op("xps2pmx.redo_steps")
    yield 0.5
    frame_model()
    yield 1.0
    shot("08_at_identify.png")
    yield from toggle_header(win, "steps")
    redraw()
    yield 0.8
    shot("09_steps_open.png")
    win, area, ui, main = ctx()
    sx = ui.x + ui.width // 2
    for k, steps in enumerate(MAPPING_SCROLLS):
        yield from scroll(win, sx, 500, steps)
        shot(f"10_mapping_{k}.png")
    j = job()
    j.bones_filter = 'merge'
    if BONE_TO_SHOW in j.bones:
        j.bones_index = list(j.bones.keys()).index(BONE_TO_SHOW)
    yield from scroll(win, sx, 500, BONES_SCROLL)
    shot("11_bones.png")
    yield from scroll(win, sx, 500, -60)

    # 9 继续 runs to ⑨; the mapping is read-only after ④
    op("xps2pmx.continue_run")
    yield 0.5
    frame_model()
    yield 1.0
    shot("12_continued.png")
    log("DONE")


STEPS = shots()


def runner():
    try:
        return next(STEPS)
    except StopIteration:
        LOG.close()
        bpy.ops.wm.quit_blender()
        return None
    except Exception:  # noqa: BLE001 - log and leave, the caller reads log.txt
        log(traceback.format_exc())
        LOG.close()
        os._exit(1)


bpy.app.timers.register(runner, first_interval=2.0)
