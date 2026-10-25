"""Run headless Blender tests from the system Python.

    python scripts/run_blender_tests.py                 # all tests_blender/test_*.py
    python scripts/run_blender_tests.py m1_import -- --models daz_purifier_inase

Uses Blender 3.6.15 with --factory-startup so only the add-ons a test enables
explicitly are active.
"""
from __future__ import annotations

import glob
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("XPS2PMX_BLENDER", r"D:\Program Files\blender-3.6.15-windows-x64\blender.exe")


def main(argv):
    passthrough = []
    if "--" in argv:
        i = argv.index("--")
        argv, passthrough = argv[:i], argv[i + 1:]
    names = argv or [os.path.basename(p)[5:-3] for p in sorted(glob.glob(os.path.join(REPO, "tests_blender", "test_*.py")))]
    failed = []
    for name in names:
        script = os.path.join(REPO, "tests_blender", f"test_{name}.py")
        cmd = [BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python", script, "--", *passthrough]
        print(">>", " ".join(f'"{c}"' if " " in c else c for c in cmd), flush=True)
        proc = subprocess.run(cmd, cwd=REPO)
        if proc.returncode != 0:
            failed.append(name)
    print("FAILED:" if failed else "ALL PASSED", " ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
