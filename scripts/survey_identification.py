"""Run stage ② (identification + mapping checks) offline over every XPS sample on this machine.

    python scripts/survey_identification.py [roots...] [--out out/identification_survey.md]

Reports per model: naming convention, required slots filled, 下半身 case, check
errors / warnings and timing; and a summary.  Duplicate files (same size and
SHA-1) are analysed once.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xps_to_pmx.core.checks.mapping import check_mapping  # noqa: E402
from xps_to_pmx.core.rig.identify import identify  # noqa: E402
from xps_to_pmx.core.rig.rigdata import RigData  # noqa: E402
from xps_to_pmx.core.spec import load_bone_spec  # noqa: E402
from xps_to_pmx.core.xps import load_xps  # noqa: E402
from xps_to_pmx.core.xps.convert import build_import_data  # noqa: E402

DEFAULT_ROOTS = ["E:/day_work", "E:/4090", "E:/mywork"]
EXTS = (".xps", ".mesh", ".ascii")


def find_files(roots):
    seen = {}
    for root in roots:
        for dirpath, _dirs, files in os.walk(root):
            if "node_modules" in dirpath or ".git" in dirpath:
                continue
            for name in files:
                low = name.lower()
                if low.endswith(EXTS) and ".bak" not in low:
                    path = os.path.join(dirpath, name)
                    try:
                        size = os.path.getsize(path)
                        with open(path, "rb") as f:
                            digest = hashlib.sha1(f.read()).hexdigest()
                    except OSError:
                        continue
                    seen.setdefault((size, digest), path)
    return sorted(seen.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", default=DEFAULT_ROOTS)
    ap.add_argument("--out", default=os.path.join("out", "identification_survey.md"))
    args = ap.parse_args()
    spec = load_bone_spec()
    required = [s.slot_id for s in spec if s.required]
    rows, summary = [], Counter()
    error_codes, warn_codes = Counter(), Counter()
    for path in find_files(args.roots):
        t0 = time.perf_counter()
        try:
            model = load_xps(path)
        except Exception as exc:  # noqa: BLE001 - survey keeps going
            rows.append((path, "PARSE FAIL", "", "", "", str(exc)[:60], 0.0))
            summary["parse_fail"] += 1
            continue
        if len(model.bones) <= 3:
            summary["props"] += 1
            continue
        rig = RigData.from_import_data(build_import_data(model))
        ident = identify(rig, spec)
        items = check_mapping(rig, spec, ident)
        filled = sum(1 for s in required if ident.slots[s].mapped)
        errors = [i for i in items if i.level == "error"]
        warnings = [i for i in items if i.level == "warning"]
        error_codes.update(i.code for i in errors)
        warn_codes.update(i.code for i in warnings)
        summary["models"] += 1
        summary["all_required"] += filled == len(required)
        summary[f"case_{ident.lower_body.case or '-'}"] += 1
        summary["no_errors"] += not errors
        summary[f"conv_{ident.convention or 'none'}"] += 1
        detail = "; ".join(i.text for i in errors)[:120]
        rows.append((path, ident.convention or "-", f"{filled}/{len(required)}", ident.lower_body.case or "-",
                     f"{len(errors)}/{len(warnings)}", detail, time.perf_counter() - t0))
        print(f"{filled:2d}/{len(required)} {ident.lower_body.case or '-'} E{len(errors)} W{len(warnings)} "
              f"{ident.convention:12s} {path}", flush=True)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# 识别器全样本统计（scripts/survey_identification.py 生成）\n\n")
        f.write(f"- 模型数（排除 ≤3 骨的道具）：{summary['models']}；道具 {summary['props']}；"
                f"解析失败 {summary['parse_fail']}\n")
        f.write(f"- 必需槽全部填上：{summary['all_required']}/{summary['models']}\n")
        f.write(f"- 没有错误级检查：{summary['no_errors']}/{summary['models']}\n")
        f.write("- 下半身诊断：" + "、".join(f"{k[5:]} {v}" for k, v in sorted(summary.items())
                                             if k.startswith("case_")) + "\n")
        f.write("- 骨架约定：" + "、".join(f"{k[5:]} {v}" for k, v in sorted(summary.items())
                                          if k.startswith("conv_")) + "\n")
        f.write("- 错误代码：" + ("、".join(f"{c} {n}" for c, n in error_codes.most_common()) or "无") + "\n")
        f.write("- 警告代码：" + ("、".join(f"{c} {n}" for c, n in warn_codes.most_common()) or "无") + "\n\n")
        f.write("| 文件 | 约定 | 必需槽 | 下半身 | 错误/警告 | 错误内容 | 秒 |\n|---|---|---|---|---|---|---|\n")
        for path, conv, filled, case, ew, detail, secs in rows:
            f.write(f"| {path} | {conv} | {filled} | {case} | {ew} | {detail} | {secs:.1f} |\n")
    print("written", args.out)


if __name__ == "__main__":
    main()
