# -*- coding: utf-8 -*-
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models

def L(k):
    return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", k + ".json"), encoding="utf-8"))

keys = [k for k, _ in models.ALL]
print("| model | H | minY | センター | グルーブ | 腰 | 下半身 | 上半身 | 上半身2 | 首 | 頭 | 両目 | 左腕 | 左足 | 左足首 | 左つま先 |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for k in keys:
    S = L(k); bp = S["bones_pos"]
    def y(n):
        return f"{bp[n][1]:.3f}" if n in bp else "-"
    print(f"| {k} | {S['height']:.3f} | {S['minY']:.3f} | {y('センター')} | {y('グルーブ')} | {y('腰')} | {y('下半身')} | {y('上半身')} | {y('上半身2')} | {y('首')} | {y('頭')} | {y('両目')} | {y('左腕')} | {y('左足')} | {y('左足首')} | {y('左つま先')} |")
print()
print("| model | 肩→腕 | 腕→ひじ L/R | ひじ→手首 L/R | elbow | knee | kneeZ | 足首→つま先 pitch | 腕→ひじ fwd | ひじ→手首 fwd | 手首→中指１ | 中指１→３ | 親指１→２ |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for k in keys:
    S = L(k); p = S["pose"]
    l, r = p.get("左", {}), p.get("右", {})
    def g(side, lab, i=0):
        try:
            return f"{side['segs'][lab][i]:.2f}"
        except Exception:
            return "-"
    def f(side, lab, i=0):
        try:
            return f"{side['fingers'][lab][i]:.1f}"
        except Exception:
            return "-"
    def n(x):
        return "-" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.2f}"
    print(f"| {k} | {g(l,'肩→腕')} | {g(l,'腕→ひじ')}/{g(r,'腕→ひじ')} | {g(l,'ひじ→手首')}/{g(r,'ひじ→手首')} | {n(l.get('elbow'))} | {n(l.get('knee'))} | {n(l.get('kneez'))} | {n(l['foot'][1]) if l.get('foot') else '-'} | {g(l,'腕→ひじ',1)} | {g(l,'ひじ→手首',1)} | {f(l,'手首→中指１')} | {f(l,'中指１→中指３')} | {f(l,'親指１→親指２')} |")
