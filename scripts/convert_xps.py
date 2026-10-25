"""Convert XPS files to PMX headlessly with the default options (stages ① → ④ → ⑧).

    "D:\\Program Files\\blender-3.6.15-windows-x64\\blender.exe" -b --factory-startup --python scripts/convert_xps.py ^
        -- <file.xps> [<file2.xps> ...] [--out D:\\xps_exports] [--blend]

Output: ``<out>/<model>/<model>.pmx`` + ``.report.json`` (and ``.blend`` with
``--blend``).  Stops a model at the first stage with errors and prints them.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import bpy  # noqa: E402


def main() -> int:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", default="")
    ap.add_argument("--blend", action="store_true", help="also save the converted scene as .blend")
    args = ap.parse_args(argv)

    import xps_to_pmx
    try:
        xps_to_pmx.register()
    except ValueError:
        pass
    from xps_to_pmx.pipeline import stage_build, stage_export, stage_identify, stage_import, stage_prepare

    failed = 0
    for path in args.files:
        bpy.ops.wm.read_homefile(use_empty=True, use_factory_startup=True)
        t0 = time.time()
        print(f"\n=== {path}")
        res, job = stage_import.run(bpy.context, path)
        steps = [("① 导入", res)]
        if res.ok:
            steps.append(("② 识别", stage_identify.run(bpy.context, job)))
        if steps[-1][1].ok:
            steps.append(("③ 预处理", stage_prepare.run(bpy.context, job)))
        if steps[-1][1].ok:
            steps.append(("④ 骨架", stage_build.run(bpy.context, job)))
        if steps[-1][1].ok:
            out = ""
            if args.out:
                name = stage_export.safe_name(job.model_name)
                out = os.path.join(args.out, name, f"{name}.pmx")
            steps.append(("⑧ 导出", stage_export.run(bpy.context, job, out)))
        for label, r in steps:
            errors = [m.text for m in r.messages if m.level == "error"]
            warnings = [m.text for m in r.messages if m.level == "warning"]
            print(f"  {label}: {'OK' if r.ok else 'FAILED'}" + (f"，{len(warnings)} 条警告" if warnings else ""))
            for text in errors[:5]:
                print(f"     ✗ {text}")
            for text in warnings[:8]:
                print(f"     ! {text}")
        if steps[-1][0] == "⑧ 导出" and steps[-1][1].ok:
            pmx = steps[-1][1].data["path"]
            print(f"  → {pmx}（{time.time() - t0:.1f}s）")
            if args.blend:
                bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(pmx)[0] + ".blend", check_existing=False)
        else:
            failed += 1
    print(f"\n{len(args.files) - failed}/{len(args.files)} converted")
    return 1 if failed else 0


if __name__ == "__main__":
    code = main()
    sys.stdout.flush()
    if code:
        raise SystemExit(code)
