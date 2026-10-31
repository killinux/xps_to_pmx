"""Regenerate the screenshots of docs/使用说明.md.

    python scripts/make_guide_screenshots.py [--xps <file.xps>] [--images <folder>] [--measure] [--skip-shoot]

1. Starts Blender 3.6 with a window running scripts/guide_shots_blender.py.  The window pops up for
   about three minutes and ignores the mouse and keyboard while it works; raw shots, ``log.txt``
   and the throw-away exports go to ``out/guide_shots/``.
2. Crops the shots and draws numbered red boxes (Pillow) into ``docs/images/usage/`` (or --images).
   docs/使用说明.md refers to the boxes by their numbers.

The boxes are window coordinates measured on the reference setup described in
guide_shots_blender.py.  After a UI change: run with --measure (no panel-header clicks), look at
``out/guide_shots/*.png``, update HEADER_CLICKS there and BOXES here, run again.
``--skip-shoot`` only redoes step 2 from the existing raw shots.

Needs Pillow in the Python that runs this script; Blender is ``XPS2PMX_BLENDER`` or the 3.6.15 default.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLENDER = os.environ.get("XPS2PMX_BLENDER", r"D:\Program Files\blender-3.6.15-windows-x64\blender.exe")
RAW = os.path.join(REPO, "out", "guide_shots")
IMAGES = os.path.join(REPO, "docs", "images", "usage")
XPS = r"E:\Downloads\rouffe (grand magician)\rouffe\xps.xps"
WINDOW = (1600, 1000)                    # must match guide_shots_blender.WIDTH / HEIGHT
FONT = r"C:\Windows\Fonts\msyhbd.ttc"
RED = (235, 64, 52)
SIDEBAR = (1128, 95, 1600, 975)          # crop boxes: x0, y0, x1, y1 in window coordinates
SIDEBAR_SHORT = (1128, 95, 1600, 934)    # ends under the thumbnail's 「打开大图」 button
WIDE = (500, 0, 1600, 1000)

#: output image: (raw shot, crop or None for the whole shot, numbered boxes in window coordinates)
BOXES = {
    "01_启用插件.png": ("01_prefs.png", None, [(224, 76, 452, 104)]),
    "02_侧栏.png": ("02_empty.png", None, [(1571, 213, 1599, 293), (1141, 139, 1348, 165),
                                         (1350, 139, 1556, 165)]),
    "03_体检报告.png": ("03_report.png", SIDEBAR, [(1141, 283, 1300, 307), (1141, 319, 1556, 489),
                                                 (1141, 496, 1556, 684), (1141, 686, 1556, 713)]),
    "04_查看详情.png": ("04_detail.png", SIDEBAR, [(1141, 345, 1556, 371), (1141, 496, 1556, 758)]),
    "13_定位.png": ("13_locate.png", WIDE, [(1141, 767, 1348, 795), (620, 330, 930, 700),
                                          (1141, 174, 1556, 204)]),
    "05_勾选修正.png": ("05_ticked.png", SIDEBAR, [(1497, 344, 1525, 397), (1141, 760, 1280, 788),
                                                 (1141, 795, 1556, 823)]),
    "06_修正单.png": ("06_fixlist.png", SIDEBAR, [(1141, 842, 1300, 870), (1141, 903, 1556, 958)]),
    "14_看图.png": ("14_render.png", SIDEBAR, [(1350, 650, 1556, 677), (1245, 702, 1442, 899),
                                             (1141, 900, 1556, 927)]),
    "07_重做之后.png": ("07_after_redo.png", SIDEBAR_SHORT, [(1141, 283, 1385, 307), (1141, 369, 1556, 421)]),
    "15_前后对比.png": ("15_compare.png", SIDEBAR, [(1350, 575, 1556, 602), (1141, 603, 1556, 826)]),
    "08_分步重做.png": ("08_at_identify.png", WIDE, [(1416, 431, 1556, 457), (1153, 532, 1292, 557)]),
    "09_分步模式.png": ("09_steps_open.png", SIDEBAR, [(1141, 568, 1556, 595), (1141, 675, 1556, 702),
                                                   (1476, 706, 1557, 734)]),
    "10_槽位.png": ("10_mapping_1.png", SIDEBAR, [(1252, 379, 1276, 704), (1277, 379, 1301, 704),
                                               (1302, 379, 1552, 704)]),
    "11_其余骨骼.png": ("11_bones.png", SIDEBAR, [(1141, 311, 1556, 416), (1353, 583, 1556, 609),
                                               (1141, 794, 1556, 872)]),
    "12_生成后只读.png": ("12_continued.png", SIDEBAR, [(1141, 779, 1556, 836)]),
}


def shoot(xps: str, measure: bool) -> bool:
    script = os.path.join(REPO, "scripts", "guide_shots_blender.py")
    cmd = [BLENDER, "--factory-startup", "--enable-event-simulate", "-p", "0", "0", str(WINDOW[0]), str(WINDOW[1]),
           "--python", script, "--", "--out", RAW, "--xps", xps] + (["--measure"] if measure else [])
    print("starting Blender with a window; it ignores the mouse and keyboard until it closes …", flush=True)
    subprocess.run(cmd, cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1200)
    log = os.path.join(RAW, "log.txt")
    lines = open(log, encoding="utf-8").read().splitlines() if os.path.isfile(log) else []
    for line in lines:
        if line.startswith(("WARNING", "Traceback")) or "Error" in line:
            print("  " + line)
    done = bool(lines) and lines[-1] == "DONE"
    print("raw shots:", RAW, "(complete)" if done else "(INCOMPLETE, see log.txt)")
    return done


def annotate(images: str) -> None:
    from PIL import Image, ImageDraw, ImageFont

    font = ImageFont.truetype(FONT, 17) if os.path.isfile(FONT) else ImageFont.load_default()
    os.makedirs(images, exist_ok=True)

    def label(draw, x, y, n):
        r = 13
        draw.ellipse((x - r, y - r, x + r, y + r), fill=RED, outline=(255, 255, 255), width=2)
        text = str(n)
        draw.text((x - draw.textlength(text, font=font) / 2, y - 12), text, font=font, fill=(255, 255, 255))

    for out, (raw, crop, boxes) in BOXES.items():
        src = os.path.join(RAW, raw)
        if not os.path.isfile(src):
            print("  missing", raw)
            continue
        img = Image.open(src).convert("RGB")
        ox, oy = (crop[0], crop[1]) if crop else (0, 0)
        if crop:
            img = img.crop(crop)
        draw = ImageDraw.Draw(img)
        for n, (x0, y0, x1, y1) in enumerate(boxes, 1):
            box = (x0 - ox, y0 - oy, x1 - ox, y1 - oy)
            draw.rounded_rectangle(box, radius=4, outline=RED, width=3)
            label(draw, box[0] - 2 if box[0] >= 16 else 15, max(box[1], 15), n)
        img.save(os.path.join(images, out), optimize=True)
        print(f"  {out}  {img.size[0]}×{img.size[1]}  {os.path.getsize(os.path.join(images, out)) // 1024} KB")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xps", default=XPS, help="the model to show (default: rouffe)")
    ap.add_argument("--images", default=IMAGES, help="where the finished images go")
    ap.add_argument("--measure", action="store_true", help="no panel-header clicks: for reading new positions")
    ap.add_argument("--skip-shoot", action="store_true", help="only crop and annotate the existing raw shots")
    args = ap.parse_args()
    if not args.skip_shoot and not shoot(args.xps, args.measure):
        return 1
    annotate(args.images)
    print("images:", args.images)
    return 0


if __name__ == "__main__":
    sys.exit(main())
