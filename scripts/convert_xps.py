"""Convert XPS files to PMX headlessly: the same one-click flow as the panel (① → ⑨, design doc §15.2).

    "D:\\Program Files\\blender-3.6.15-windows-x64\\blender.exe" -b --factory-startup --python scripts/convert_xps.py ^
        -- <file.xps> [<file2.xps> ...] [--out D:\\xps_exports] [--blend] [--fixes <file>] [--no-fixes]

Output: ``<out>/<model>/<model>.pmx`` + ``.report.json`` (with the checkup) + ``.fixes.json``
(and ``.blend`` with ``--blend``).  The fix list remembered for each XPS file is applied unless
``--no-fixes``; ``--fixes`` applies one fix file to every model instead.  A model stops at the
first stage with errors; the others continue.
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
    ap.add_argument("--out", default="", help="export root (default: D:\\xps_exports)")
    ap.add_argument("--blend", action="store_true", help="also save the converted scene as .blend")
    ap.add_argument("--fixes", default="", help="apply this fix file to every model")
    ap.add_argument("--no-fixes", action="store_true", help="ignore the fix lists remembered for the files")
    args = ap.parse_args(argv)
    if args.out:
        os.environ["XPS2PMX_EXPORT_ROOT"] = os.path.abspath(args.out)

    import xps_to_pmx
    try:
        xps_to_pmx.register()
    except ValueError:
        pass
    from xps_to_pmx.pipeline import runner

    failed = 0
    for path in args.files:
        bpy.ops.wm.read_homefile(use_empty=True, use_factory_startup=True)
        t0 = time.time()
        print(f"\n=== {path}")
        res, job = runner.one_click(bpy.context, path, remember=not args.no_fixes, fixes_file=args.fixes)
        for step in res.data.get("steps", []):
            warn = f"，{len(step['warnings'])} 条警告" if step["warnings"] else ""
            print(f"  {step['label']}: {'OK' if step['ok'] else 'FAILED'}{warn}")
            for text in step["errors"][:5]:
                print(f"     ✗ {text}")
        for m in res.messages:
            if m.code.startswith("fixes."):
                print(f"  · {m.text}")
        if job is not None and job.findings:
            print("  体检：")
            for f in job.findings:
                if f.level == "info" and f.state not in ("auto_fixed",):
                    continue
                mark = {"error": "✗", "warning": "!", "info": "·"}[f.level]
                state = {"auto_fixed": "（已自动修正）", "fixed": "（已修复）"}.get(f.state, "")
                print(f"     {mark} {f.text}{state}")
        if res.ok and job is not None and job.stage == "checkup":
            print(f"  → {job.last_export}（{time.time() - t0:.1f}s）")
            if args.blend:
                bpy.ops.wm.save_as_mainfile(filepath=os.path.splitext(job.last_export)[0] + ".blend",
                                            check_existing=False)
        else:
            failed += 1
            for m in res.messages:
                if m.code.startswith("run.") and m.level == "error":
                    print(f"  ✗ {m.text}")
    print(f"\n{len(args.files) - failed}/{len(args.files)} converted")
    return 1 if failed else 0


if __name__ == "__main__":
    code = main()
    sys.stdout.flush()
    if code:
        raise SystemExit(code)
