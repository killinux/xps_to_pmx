# Own_DOAReika

E:/mywork/xps2mmd/DOA-Shimohira Reika/Generic_Item_new.pmx

name='Model' name_e='Model'

comment:
~~~

~~~
comment_e:
~~~

~~~
V=45424 F=66056 Tex=24 Mat=17 Bone=1100 Morph=0 Disp=2 RB=0 J=0 addUV=3 idx(v,t,m,b,mo,r)=4,4,4,4,4,4

## 1. Scale
bbox min=(-6.053, 0.106, -1.568) max=(6.053, 16.759, 1.404) size=(12.105, 16.653, 2.972) height=16.653 ground(minY)=0.1061

| bone | pos | Y/height (from ground) |
|---|---|---|
| 全ての親 | (0.000, 0.000, -0.000) | -0.006 |
| センター | (0.000, 10.320, 0.000) | 0.613 |
| 上半身 | (0.000, 11.257, -0.066) | 0.670 |
| 上半身2 | (0.000, 12.277, -0.136) | 0.731 |
| 首 | (0.000, 14.180, 0.312) | 0.845 |
| 頭 | (0.000, 14.879, 0.120) | 0.887 |
| 左目 | (0.295, 15.456, -0.494) | 0.922 |
| 右目 | (-0.295, 15.456, -0.494) | 0.922 |
| 左肩 | (0.686, 13.623, 0.273) | 0.812 |
| 左腕 | (1.300, 13.560, 0.273) | 0.808 |
| 左ひじ | (3.094, 11.766, 0.273) | 0.700 |
| 左手首 | (4.805, 10.055, 0.273) | 0.597 |
| 左足 | (0.820, 9.407, 0.156) | 0.559 |
| 左ひざ | (1.881, 5.447, 0.156) | 0.321 |
| 左つま先 | (3.217, 0.463, -0.814) | 0.021 |
| 左つま先ＩＫ | (3.217, 0.463, -0.814) | 0.021 |

## 2. Rest pose angles
| side | segment | deg below horizontal (or angle) | deg forward(-Z) |
|---|---|---|---|
| 左 | 肩→腕 | 5.92 | -0.03 |
| 左 | 腕→ひじ | 45.00 | -0.00 |
| 左 | ひじ→手首 | 45.00 | -0.00 |
| 左 | 腕→手首 | 45.00 | -0.00 |
| 左 | elbow bend(3D) | 0.00 |  |
| 左 | knee bend(3D) | nan |  |
| 左 | leg spread (足→足首 from vertical, +outward) | - |  |
| 左 | 手首→中指１ | 33.80 | 6.84 |
| 左 | 人指１→人指３ | 44.69 | 8.45 |
| 左 | 中指１→中指３ | 45.00 | -0.00 |
| 左 | 小指１→小指３ | 44.68 | -17.88 |
| 左 | 親指１→親指２ | 58.63 | 78.55 |
| 左 | 親指０→親指２ | 58.63 | 78.55 |
| 右 | 肩→腕 | 5.92 | -0.03 |
| 右 | 腕→ひじ | 45.00 | -0.00 |
| 右 | ひじ→手首 | 45.00 | -0.00 |
| 右 | 腕→手首 | 45.00 | -0.00 |
| 右 | elbow bend(3D) | 0.00 |  |
| 右 | knee bend(3D) | nan |  |
| 右 | leg spread (足→足首 from vertical, +outward) | - |  |
| 右 | 手首→中指１ | 33.05 | 6.77 |
| 右 | 人指１→人指３ | 44.69 | 8.45 |
| 右 | 中指１→中指３ | 45.00 | -0.00 |
| 右 | 小指１→小指３ | 44.76 | -17.91 |
| 右 | 親指１→親指２ | 59.62 | 81.42 |
| 右 | 親指０→親指２ | 59.62 | 81.42 |

## 3. Bones (full)
| # | name_j | name_e | parent | pos | flags | 層 | tail | 付与 | 軸 | ローカル軸 | IK | nV | Σw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 全ての親 | root ground | - | (0.000, 0.000, -0.000) | RM-C | 0 | センター |  |  |  |  | 0 | 0 |
| 1 | センター | root hips | 全ての親 | (0.000, 10.320, 0.000) | RMVC | 0 | (-0.00, -0.50, 0.09) |  |  |  |  | 4315 | 2582 |
| 2 | 上半身 | spine lower | センター | (0.000, 11.257, -0.066) | RMVC | 0 | 上半身2 |  |  |  |  | 3113 | 474 |
| 3 | 上半身2 | spine upper | 上半身 | (0.000, 12.277, -0.136) | RMVC | 0 | (0.00, 0.71, 0.06) |  |  |  |  | 5483 | 2292 |
| 4 | 首 | head neck lower | 上半身2 | (0.000, 14.180, 0.312) | RMVC | 0 | 頭 |  |  |  |  | 1879 | 404 |
| 5 | 頭 | head neck upper | 首 | (0.000, 14.879, 0.120) | RMVC | 0 | (0.02, 0.55, 0.28) |  |  |  |  | 4071 | 2756 |
| 6 | unused face | unused face | 頭 | (0.000, 14.879, 0.120) | RM-C | 0 | (-0.00, 0.39, -0.77) |  |  |  |  | 1276 | 671 |
| 7 | head eyebrow middle | head eyebrow middle | unused head neck upper attached-full head neck upper | (0.000, 15.554, -0.751) | RMVC | 0 | (0.00, 0.70, -0.90) |  |  |  |  | 25 | 6 |
| 8 | head lip upper middle | head lip upper middle | unused head neck upper attached-full head neck upper | (0.000, 14.901, -0.786) | RMVC | 0 | (0.00, 0.05, -0.93) |  |  |  |  | 274 | 66 |
| 9 | head nose middle | head nose middle | unused head neck upper attached-full head neck upper | (0.000, 15.122, -0.896) | RMVC | 0 | (0.00, 0.27, -1.04) |  |  |  |  | 146 | 34 |
| 10 | head jaw | head jaw | unused head neck upper attached-full head neck upper | (0.000, 15.056, -0.048) | RMVC | 0 | (0.00, -0.20, -0.46) |  |  |  |  | 1150 | 656 |
| 11 | head lip lower middle | head lip lower middle | head jaw | (0.000, 14.824, -0.756) | RMVC | 0 | (0.00, -0.23, -0.71) |  |  |  |  | 136 | 54 |
| 12 | head tongue 1 | head tongue 1 | head jaw | (0.000, 14.846, -0.189) | RMVC | 0 | head tongue 2 |  |  |  |  | 64 | 32 |
| 13 | head tongue 2 | head tongue 2 | head tongue 1 | (0.000, 14.873, -0.470) | RMVC | 0 | (0.00, 0.03, -0.28) |  |  |  |  | 63 | 32 |
| 14 | head lip lower left | head lip lower left | head jaw | (0.116, 14.841, -0.706) | RMVC | 0 | (0.12, -0.22, -0.66) |  |  |  |  | 158 | 47 |
| 15 | head lip lower right | head lip lower right | head jaw | (-0.116, 14.841, -0.706) | RMVC | 0 | (-0.12, -0.22, -0.66) |  |  |  |  | 157 | 45 |
| 16 | head cheek left 1 | head cheek left 1 | unused face | (0.281, 15.227, -0.686) | RMVC | 0 | (0.28, 0.35, -0.81) |  |  |  |  | 127 | 28 |
| 17 | head cheek left 2 | head cheek left 2 | unused face | (0.452, 15.276, -0.595) | RMVC | 0 | (0.45, 0.40, -0.71) |  |  |  |  | 132 | 16 |
| 18 | head cheek left 3 | head cheek left 3 | unused face | (0.522, 14.989, -0.362) | RMVC | 0 | (0.52, 0.11, -0.48) |  |  |  |  | 129 | 29 |
| 19 | 左目 | head eyeball left | unused head neck upper attached-full head neck upper | (0.295, 15.456, -0.494) | RMVC | 0 | (0.29, 0.60, -0.64) |  |  |  |  | 129 | 129 |
| 20 | head eyelid left lower 1 | head eyelid left lower 1 | unused face | (0.238, 15.364, -0.654) | RMVC | 0 | (0.24, 0.48, -0.77) |  |  |  |  | 135 | 28 |
| 21 | head eyelid left lower 2 | head eyelid left lower 2 | unused face | (0.345, 15.353, -0.648) | RMVC | 0 | (0.35, 0.47, -0.77) |  |  |  |  | 190 | 52 |
| 22 | head eyebrow left 1 | head eyebrow left 1 | unused face | (0.142, 15.543, -0.728) | RMVC | 0 | (0.14, 0.66, -0.85) |  |  |  |  | 102 | 21 |
| 23 | head eyebrow left 2 | head eyebrow left 2 | unused face | (0.335, 15.594, -0.697) | RMVC | 0 | (0.33, 0.71, -0.82) |  |  |  |  | 142 | 20 |
| 24 | head eyebrow left 3 | head eyebrow left 3 | unused face | (0.488, 15.570, -0.593) | RMVC | 0 | (0.49, 0.69, -0.71) |  |  |  |  | 88 | 17 |
| 25 | head eyelid left upper | head eyelid left upper | unused face | (0.286, 15.455, -0.495) | RMVC | 0 | (0.29, 0.58, -0.61) |  |  |  |  | 528 | 306 |
| 26 | head forehead left | head forehead left | unused head neck upper attached-full head neck upper | (0.319, 15.717, -0.700) | RMVC | 0 | (0.32, 0.86, -0.85) |  |  |  |  | 42 | 7 |
| 27 | head lip corner left | head lip corner left | unused head neck upper attached-full head neck upper | (0.182, 14.873, -0.677) | RMVC | 0 | (0.18, 0.02, -0.83) |  |  |  |  | 237 | 59 |
| 28 | head lip upper left | head lip upper left | unused head neck upper attached-full head neck upper | (0.107, 14.894, -0.740) | RMVC | 0 | (0.11, 0.04, -0.89) |  |  |  |  | 153 | 48 |
| 29 | head nose left 1 | head nose left 1 | unused face | (0.087, 15.261, -0.743) | RMVC | 0 | (0.09, 0.38, -0.86) |  |  |  |  | 85 | 18 |
| 30 | head nose left 2 | head nose left 2 | unused face | (0.141, 15.084, -0.720) | RMVC | 0 | (0.14, 0.21, -0.84) |  |  |  |  | 166 | 48 |
| 31 | head nose left 3 | head nose left 3 | unused face | (0.192, 15.027, -0.702) | RMVC | 0 | (0.19, 0.15, -0.82) |  |  |  |  | 61 | 10 |
| 32 | head nose left 4 | head nose left 4 | unused face | (0.225, 14.956, -0.683) | RMVC | 0 | (0.22, 0.08, -0.80) |  |  |  |  | 36 | 6 |
| 33 | head cheek right 1 | head cheek right 1 | unused face | (-0.281, 15.227, -0.686) | RMVC | 0 | (-0.28, 0.35, -0.81) |  |  |  |  | 125 | 29 |
| 34 | head cheek right 2 | head cheek right 2 | unused face | (-0.452, 15.276, -0.595) | RMVC | 0 | (-0.45, 0.40, -0.71) |  |  |  |  | 132 | 19 |
| 35 | head cheek right 3 | head cheek right 3 | unused face | (-0.522, 14.989, -0.362) | RMVC | 0 | (-0.52, 0.11, -0.48) |  |  |  |  | 129 | 26 |
| 36 | 右目 | head eyeball right | unused head neck upper attached-full head neck upper | (-0.295, 15.456, -0.494) | RMVC | 0 | (-0.29, 0.60, -0.64) |  |  |  |  | 129 | 129 |
| 37 | head eyelid right lower 1 | head eyelid right lower 1 | unused face | (-0.238, 15.364, -0.654) | RMVC | 0 | (-0.24, 0.48, -0.77) |  |  |  |  | 135 | 27 |
| 38 | head eyelid right lower 2 | head eyelid right lower 2 | unused face | (-0.345, 15.353, -0.648) | RMVC | 0 | (-0.35, 0.47, -0.77) |  |  |  |  | 190 | 48 |
| 39 | head eyebrow right 1 | head eyebrow right 1 | unused face | (-0.142, 15.543, -0.728) | RMVC | 0 | (-0.14, 0.66, -0.85) |  |  |  |  | 102 | 21 |
| 40 | head eyebrow right 2 | head eyebrow right 2 | unused face | (-0.335, 15.594, -0.697) | RMVC | 0 | (-0.33, 0.71, -0.82) |  |  |  |  | 142 | 21 |
| 41 | head eyebrow right 3 | head eyebrow right 3 | unused face | (-0.488, 15.570, -0.593) | RMVC | 0 | (-0.49, 0.69, -0.71) |  |  |  |  | 88 | 16 |
| 42 | head eyelid right upper | head eyelid right upper | unused face | (-0.286, 15.455, -0.495) | RMVC | 0 | (-0.29, 0.58, -0.61) |  |  |  |  | 529 | 304 |
| 43 | head forehead right | head forehead right | unused head neck upper attached-full head neck upper | (-0.319, 15.717, -0.700) | RMVC | 0 | (-0.32, 0.86, -0.85) |  |  |  |  | 42 | 7 |
| 44 | head lip corner right | head lip corner right | unused head neck upper attached-full head neck upper | (-0.182, 14.873, -0.677) | RMVC | 0 | (-0.18, 0.02, -0.83) |  |  |  |  | 238 | 59 |
| 45 | head lip upper right | head lip upper right | unused head neck upper attached-full head neck upper | (-0.107, 14.894, -0.740) | RMVC | 0 | (-0.11, 0.04, -0.89) |  |  |  |  | 149 | 48 |
| 46 | head nose right 1 | head nose right 1 | unused face | (-0.087, 15.261, -0.743) | RMVC | 0 | (-0.09, 0.38, -0.86) |  |  |  |  | 79 | 16 |
| 47 | head nose right 2 | head nose right 2 | unused face | (-0.141, 15.084, -0.720) | RMVC | 0 | (-0.14, 0.21, -0.84) |  |  |  |  | 164 | 51 |
| 48 | head nose right 3 | head nose right 3 | unused face | (-0.192, 15.027, -0.702) | RMVC | 0 | (-0.19, 0.15, -0.82) |  |  |  |  | 61 | 11 |
| 49 | head nose right 4 | head nose right 4 | unused face | (-0.225, 14.956, -0.683) | RMVC | 0 | (-0.22, 0.08, -0.80) |  |  |  |  | 36 | 6 |
| 50 | unused dummy | unused dummy | 頭 | (0.000, 14.879, 0.120) | RM-C | 0 | (0.00, -0.00, -0.00) |  |  |  |  | 1369 | 1033 |
| 51 | hair back a middle 1 | hair back a middle 1 | 頭 | (0.000, 15.191, 1.014) | RMVC | 0 | hair back a middle 2 |  |  |  |  | 12 | 1 |
| 52 | hair back a middle 2 | hair back a middle 2 | hair back a middle 1 | (-0.002, 14.633, 0.934) | RMVC | 0 | hair back a middle 3 |  |  |  |  | 17 | 3 |
| 53 | hair back a middle 3 | hair back a middle 3 | hair back a middle 2 | (-0.002, 13.900, 0.932) | RMVC | 0 | hair back a middle 4 |  |  |  |  | 29 | 14 |
| 54 | hair back a middle 4 | hair back a middle 4 | hair back a middle 3 | (-0.001, 13.167, 0.930) | RMVC | 0 | hair back a middle 5 |  |  |  |  | 26 | 12 |
| 55 | hair back a middle 5 | hair back a middle 5 | hair back a middle 4 | (-0.001, 12.434, 0.928) | RMVC | 0 | hair back a middle 6 |  |  |  |  | 26 | 12 |
| 56 | hair back a middle 6 | hair back a middle 6 | hair back a middle 5 | (-0.001, 11.701, 0.926) | RMVC | 0 | hair back a middle 7 |  |  |  |  | 26 | 12 |
| 57 | hair back a middle 7 | hair back a middle 7 | hair back a middle 6 | (-0.001, 10.968, 0.924) | RMVC | 0 | hair back a middle 8 |  |  |  |  | 26 | 12 |
| 58 | hair back a middle 8 | hair back a middle 8 | hair back a middle 7 | (-0.000, 10.235, 0.921) | RMVC | 0 | (0.00, -0.73, -0.00) |  |  |  |  | 24 | 19 |
| 59 | hair back a left 1 | hair back a left 1 | 頭 | (0.444, 15.221, 0.750) | RMVC | 0 | hair back a left 2 |  |  |  |  | 29 | 2 |
| 60 | hair back a left 2 | hair back a left 2 | hair back a left 1 | (0.199, 14.736, 0.687) | RMVC | 0 | hair back a left 3 |  |  |  |  | 40 | 8 |
| 61 | hair back a left 3 | hair back a left 3 | hair back a left 2 | (0.169, 14.093, 0.633) | RMVC | 0 | hair back a left 4 |  |  |  |  | 44 | 16 |
| 62 | hair back a left 4 | hair back a left 4 | hair back a left 3 | (0.181, 13.451, 0.652) | RMVC | 0 | hair back a left 5 |  |  |  |  | 54 | 20 |
| 63 | hair back a left 5 | hair back a left 5 | hair back a left 4 | (0.193, 12.808, 0.671) | RMVC | 0 | hair back a left 6 |  |  |  |  | 53 | 20 |
| 64 | hair back a left 6 | hair back a left 6 | hair back a left 5 | (0.202, 12.055, 0.664) | RMVC | 0 | hair back a left 7 |  |  |  |  | 56 | 31 |
| 65 | hair back a left 7 | hair back a left 7 | hair back a left 6 | (0.216, 11.208, 0.656) | RMVC | 0 | (0.01, -0.85, -0.01) |  |  |  |  | 50 | 31 |
| 66 | hair back a right 1 | hair back a right 1 | 頭 | (-0.443, 15.221, 0.731) | RMVC | 0 | hair back a right 2 |  |  |  |  | 27 | 2 |
| 67 | hair back a right 2 | hair back a right 2 | hair back a right 1 | (-0.199, 14.736, 0.662) | RMVC | 0 | hair back a right 3 |  |  |  |  | 37 | 6 |
| 68 | hair back a right 3 | hair back a right 3 | hair back a right 2 | (-0.158, 14.092, 0.621) | RMVC | 0 | hair back a right 4 |  |  |  |  | 45 | 18 |
| 69 | hair back a right 4 | hair back a right 4 | hair back a right 3 | (-0.140, 13.449, 0.640) | RMVC | 0 | hair back a right 5 |  |  |  |  | 50 | 19 |
| 70 | hair back a right 5 | hair back a right 5 | hair back a right 4 | (-0.152, 12.807, 0.659) | RMVC | 0 | hair back a right 6 |  |  |  |  | 49 | 21 |
| 71 | hair back a right 6 | hair back a right 6 | hair back a right 5 | (-0.161, 12.053, 0.652) | RMVC | 0 | hair back a right 7 |  |  |  |  | 54 | 32 |
| 72 | hair back a right 7 | hair back a right 7 | hair back a right 6 | (-0.177, 11.207, 0.645) | RMVC | 0 | (-0.02, -0.85, -0.01) |  |  |  |  | 46 | 30 |
| 73 | hair back a side left 1 | hair back a side left 1 | 頭 | (0.778, 15.384, 0.427) | RMVC | 0 | hair back a side left 2 |  |  |  |  | 26 | 6 |
| 74 | hair back a side left 2 | hair back a side left 2 | hair back a side left 1 | (0.746, 14.794, 0.451) | RMVC | 0 | hair back a side left 3 |  |  |  |  | 38 | 7 |
| 75 | hair back a side left 3 | hair back a side left 3 | hair back a side left 2 | (0.743, 14.238, 0.456) | RMVC | 0 | hair back a side left 4 |  |  |  |  | 36 | 10 |
| 76 | hair back a side left 4 | hair back a side left 4 | hair back a side left 3 | (0.740, 13.682, 0.461) | RMVC | 0 | hair back a side left 5 |  |  |  |  | 38 | 14 |
| 77 | hair back a side left 5 | hair back a side left 5 | hair back a side left 4 | (0.737, 13.126, 0.466) | RMVC | 0 | hair back a side left 6 |  |  |  |  | 36 | 17 |
| 78 | hair back a side left 6 | hair back a side left 6 | hair back a side left 5 | (0.734, 12.570, 0.470) | RMVC | 0 | hair back a side left 7 |  |  |  |  | 24 | 8 |
| 79 | hair back a side left 7 | hair back a side left 7 | hair back a side left 6 | (0.731, 12.014, 0.475) | RMVC | 0 | hair back a side left 8 |  |  |  |  | 25 | 11 |
| 80 | hair back a side left 8 | hair back a side left 8 | hair back a side left 7 | (0.727, 11.458, 0.480) | RMVC | 0 | (-0.00, -0.56, 0.00) |  |  |  |  | 24 | 19 |
| 81 | hair back a side right 1 | hair back a side right 1 | 頭 | (-0.748, 15.295, 0.454) | RMVC | 0 | hair back a side right 2 |  |  |  |  | 38 | 9 |
| 82 | hair back a side right 2 | hair back a side right 2 | hair back a side right 1 | (-0.746, 14.794, 0.451) | RMVC | 0 | hair back a side right 3 |  |  |  |  | 39 | 6 |
| 83 | hair back a side right 3 | hair back a side right 3 | hair back a side right 2 | (-0.743, 14.238, 0.456) | RMVC | 0 | hair back a side right 4 |  |  |  |  | 39 | 11 |
| 84 | hair back a side right 4 | hair back a side right 4 | hair back a side right 3 | (-0.740, 13.682, 0.461) | RMVC | 0 | hair back a side right 5 |  |  |  |  | 38 | 14 |
| 85 | hair back a side right 5 | hair back a side right 5 | hair back a side right 4 | (-0.737, 13.126, 0.466) | RMVC | 0 | hair back a side right 6 |  |  |  |  | 31 | 12 |
| 86 | hair back a side right 6 | hair back a side right 6 | hair back a side right 5 | (-0.734, 12.570, 0.471) | RMVC | 0 | hair back a side right 7 |  |  |  |  | 27 | 12 |
| 87 | hair back a side right 7 | hair back a side right 7 | hair back a side right 6 | (-0.730, 12.014, 0.475) | RMVC | 0 | hair back a side right 8 |  |  |  |  | 30 | 10 |
| 88 | hair back a side right 8 | hair back a side right 8 | hair back a side right 7 | (-0.727, 11.458, 0.480) | RMVC | 0 | (0.00, -0.56, 0.00) |  |  |  |  | 27 | 21 |
| 89 | hair back b middle 1 | hair back b middle 1 | 頭 | (0.022, 15.430, 1.203) | RMVC | 0 | hair back b middle 2 |  |  |  |  | 40 | 15 |
| 90 | hair back b middle 2 | hair back b middle 2 | hair back b middle 1 | (-0.005, 14.879, 1.160) | RMVC | 0 | hair back b middle 3 |  |  |  |  | 41 | 11 |
| 91 | hair back b middle 3 | hair back b middle 3 | hair back b middle 2 | (-0.010, 14.304, 1.157) | RMVC | 0 | hair back b middle 4 |  |  |  |  | 37 | 14 |
| 92 | hair back b middle 4 | hair back b middle 4 | hair back b middle 3 | (-0.015, 13.730, 1.153) | RMVC | 0 | hair back b middle 5 |  |  |  |  | 27 | 6 |
| 93 | hair back b middle 5 | hair back b middle 5 | hair back b middle 4 | (-0.020, 13.155, 1.149) | RMVC | 0 | hair back b middle 6 |  |  |  |  | 14 | 5 |
| 94 | hair back b middle 6 | hair back b middle 6 | hair back b middle 5 | (-0.026, 12.580, 1.144) | RMVC | 0 | hair back b middle 7 |  |  |  |  | 15 | 9 |
| 95 | hair back b middle 7 | hair back b middle 7 | hair back b middle 6 | (-0.022, 11.888, 1.164) | RMVC | 0 | hair back b middle 8 |  |  |  |  | 15 | 4 |
| 96 | hair back b middle 8 | hair back b middle 8 | hair back b middle 7 | (-0.022, 11.118, 1.130) | RMVC | 0 | hair back b middle 9 |  |  |  |  | 11 | 6 |
| 97 | hair back b middle 9 | hair back b middle 9 | hair back b middle 8 | (-0.023, 10.349, 1.096) | RMVC | 0 | (-0.00, -0.77, -0.03) |  |  |  |  | 12 | 11 |
| 98 | hair back b left 1 | hair back b left 1 | 頭 | (0.615, 15.677, 0.995) | RMVC | 0 | hair back b left 2 |  |  |  |  | 38 | 11 |
| 99 | hair back b left 2 | hair back b left 2 | hair back b left 1 | (0.580, 15.179, 0.996) | RMVC | 0 | hair back b left 3 |  |  |  |  | 36 | 11 |
| 100 | hair back b left 3 | hair back b left 3 | hair back b left 2 | (0.558, 14.596, 0.974) | RMVC | 0 | hair back b left 4 |  |  |  |  | 42 | 14 |
| 101 | hair back b left 4 | hair back b left 4 | hair back b left 3 | (0.566, 14.020, 0.989) | RMVC | 0 | hair back b left 5 |  |  |  |  | 38 | 12 |
| 102 | hair back b left 5 | hair back b left 5 | hair back b left 4 | (0.574, 13.444, 1.004) | RMVC | 0 | hair back b left 6 |  |  |  |  | 30 | 12 |
| 103 | hair back b left 6 | hair back b left 6 | hair back b left 5 | (0.582, 12.868, 1.019) | RMVC | 0 | hair back b left 7 |  |  |  |  | 31 | 13 |
| 104 | hair back b left 7 | hair back b left 7 | hair back b left 6 | (0.598, 12.187, 1.027) | RMVC | 0 | hair back b left 8 |  |  |  |  | 34 | 15 |
| 105 | hair back b left 8 | hair back b left 8 | hair back b left 7 | (0.599, 11.401, 1.028) | RMVC | 0 | hair back b left 9 |  |  |  |  | 36 | 15 |
| 106 | hair back b left 9 | hair back b left 9 | hair back b left 8 | (0.622, 10.615, 1.029) | RMVC | 0 | (0.02, -0.79, 0.00) |  |  |  |  | 28 | 18 |
| 107 | hair back b right 1 | hair back b right 1 | 頭 | (-0.624, 15.673, 1.013) | RMVC | 0 | hair back b right 2 |  |  |  |  | 38 | 12 |
| 108 | hair back b right 2 | hair back b right 2 | hair back b right 1 | (-0.606, 15.178, 1.014) | RMVC | 0 | hair back b right 3 |  |  |  |  | 39 | 10 |
| 109 | hair back b right 3 | hair back b right 3 | hair back b right 2 | (-0.599, 14.595, 0.990) | RMVC | 0 | hair back b right 4 |  |  |  |  | 42 | 13 |
| 110 | hair back b right 4 | hair back b right 4 | hair back b right 3 | (-0.604, 14.019, 0.997) | RMVC | 0 | hair back b right 5 |  |  |  |  | 40 | 13 |
| 111 | hair back b right 5 | hair back b right 5 | hair back b right 4 | (-0.613, 13.444, 1.008) | RMVC | 0 | hair back b right 6 |  |  |  |  | 31 | 12 |
| 112 | hair back b right 6 | hair back b right 6 | hair back b right 5 | (-0.621, 12.868, 1.019) | RMVC | 0 | hair back b right 7 |  |  |  |  | 31 | 12 |
| 113 | hair back b right 7 | hair back b right 7 | hair back b right 6 | (-0.634, 12.194, 1.023) | RMVC | 0 | hair back b right 8 |  |  |  |  | 28 | 15 |
| 114 | hair back b right 8 | hair back b right 8 | hair back b right 7 | (-0.651, 11.422, 1.018) | RMVC | 0 | hair back b right 9 |  |  |  |  | 34 | 22 |
| 115 | hair back b right 9 | hair back b right 9 | hair back b right 8 | (-0.651, 10.640, 1.027) | RMVC | 0 | (0.00, -0.78, 0.01) |  |  |  |  | 28 | 12 |
| 116 | hair back b side left 1 | hair back b side left 1 | 頭 | (0.873, 15.875, 0.484) | RMVC | 0 | hair back b side left 2 |  |  |  |  | 49 | 7 |
| 117 | hair back b side left 2 | hair back b side left 2 | hair back b side left 1 | (0.872, 15.425, 0.563) | RMVC | 0 | hair back b side left 3 |  |  |  |  | 56 | 12 |
| 118 | hair back b side left 3 | hair back b side left 3 | hair back b side left 2 | (0.853, 14.912, 0.581) | RMVC | 0 | hair back b side left 4 |  |  |  |  | 54 | 15 |
| 119 | hair back b side left 4 | hair back b side left 4 | hair back b side left 3 | (0.859, 14.269, 0.585) | RMVC | 0 | hair back b side left 5 |  |  |  |  | 46 | 20 |
| 120 | hair back b side left 5 | hair back b side left 5 | hair back b side left 4 | (0.868, 13.627, 0.586) | RMVC | 0 | hair back b side left 6 |  |  |  |  | 44 | 15 |
| 121 | hair back b side left 6 | hair back b side left 6 | hair back b side left 5 | (0.871, 12.984, 0.601) | RMVC | 0 | hair back b side left 7 |  |  |  |  | 38 | 16 |
| 122 | hair back b side left 7 | hair back b side left 7 | hair back b side left 6 | (0.874, 12.341, 0.616) | RMVC | 0 | hair back b side left 8 |  |  |  |  | 38 | 16 |
| 123 | hair back b side left 8 | hair back b side left 8 | hair back b side left 7 | (0.877, 11.699, 0.631) | RMVC | 0 | hair back b side left 9 |  |  |  |  | 35 | 15 |
| 124 | hair back b side left 9 | hair back b side left 9 | hair back b side left 8 | (0.880, 11.056, 0.646) | RMVC | 0 | (0.00, -0.64, 0.02) |  |  |  |  | 33 | 22 |
| 125 | hair back b side right 1 | hair back b side right 1 | 頭 | (-0.897, 15.884, 0.392) | RMVC | 0 | hair back b side right 2 |  |  |  |  | 41 | 9 |
| 126 | hair back b side right 2 | hair back b side right 2 | hair back b side right 1 | (-0.922, 15.398, 0.448) | RMVC | 0 | hair back b side right 3 |  |  |  |  | 51 | 12 |
| 127 | hair back b side right 3 | hair back b side right 3 | hair back b side right 2 | (-0.878, 14.876, 0.471) | RMVC | 0 | hair back b side right 4 |  |  |  |  | 51 | 15 |
| 128 | hair back b side right 4 | hair back b side right 4 | hair back b side right 3 | (-0.871, 14.244, 0.487) | RMVC | 0 | hair back b side right 5 |  |  |  |  | 50 | 18 |
| 129 | hair back b side right 5 | hair back b side right 5 | hair back b side right 4 | (-0.865, 13.611, 0.502) | RMVC | 0 | hair back b side right 6 |  |  |  |  | 44 | 20 |
| 130 | hair back b side right 6 | hair back b side right 6 | hair back b side right 5 | (-0.858, 12.979, 0.518) | RMVC | 0 | hair back b side right 7 |  |  |  |  | 37 | 10 |
| 131 | hair back b side right 7 | hair back b side right 7 | hair back b side right 6 | (-0.851, 12.346, 0.534) | RMVC | 0 | hair back b side right 8 |  |  |  |  | 36 | 19 |
| 132 | hair back b side right 8 | hair back b side right 8 | hair back b side right 7 | (-0.844, 11.714, 0.549) | RMVC | 0 | hair back b side right 9 |  |  |  |  | 36 | 15 |
| 133 | hair back b side right 9 | hair back b side right 9 | hair back b side right 8 | (-0.838, 11.081, 0.565) | RMVC | 0 | (0.01, -0.63, 0.02) |  |  |  |  | 34 | 23 |
| 134 | hair back c middle 1 | hair back c middle 1 | 頭 | (0.043, 15.680, 1.220) | RMVC | 0 | hair back c middle 2 |  |  |  |  | 35 | 5 |
| 135 | hair back c middle 2 | hair back c middle 2 | hair back c middle 1 | (0.008, 15.180, 1.202) | RMVC | 0 | hair back c middle 3 |  |  |  |  | 47 | 9 |
| 136 | hair back c middle 3 | hair back c middle 3 | hair back c middle 2 | (-0.013, 14.537, 1.188) | RMVC | 0 | hair back c middle 4 |  |  |  |  | 50 | 11 |
| 137 | hair back c middle 4 | hair back c middle 4 | hair back c middle 3 | (-0.014, 13.918, 1.201) | RMVC | 0 | hair back c middle 5 |  |  |  |  | 27 | 10 |
| 138 | hair back c middle 5 | hair back c middle 5 | hair back c middle 4 | (-0.016, 13.300, 1.214) | RMVC | 0 | hair back c middle 6 |  |  |  |  | 24 | 8 |
| 139 | hair back c middle 6 | hair back c middle 6 | hair back c middle 5 | (-0.017, 12.681, 1.228) | RMVC | 0 | hair back c middle 7 |  |  |  |  | 18 | 6 |
| 140 | hair back c middle 7 | hair back c middle 7 | hair back c middle 6 | (-0.018, 12.062, 1.241) | RMVC | 0 | hair back c middle 8 |  |  |  |  | 15 | 6 |
| 141 | hair back c middle 8 | hair back c middle 8 | hair back c middle 7 | (-0.019, 11.443, 1.254) | RMVC | 0 | hair back c middle 9 |  |  |  |  | 15 | 6 |
| 142 | hair back c middle 9 | hair back c middle 9 | hair back c middle 8 | (-0.021, 10.824, 1.268) | RMVC | 0 | hair back c middle 10 |  |  |  |  | 21 | 6 |
| 143 | hair back c middle 10 | hair back c middle 10 | hair back c middle 9 | (-0.022, 10.205, 1.281) | RMVC | 0 | (-0.00, -0.62, 0.01) |  |  |  |  | 15 | 10 |
| 144 | hair back c left 1 | hair back c left 1 | 頭 | (0.630, 15.684, 0.999) | RMVC | 0 | hair back c left 2 |  |  |  |  | 27 | 1 |
| 145 | hair back c left 2 | hair back c left 2 | hair back c left 1 | (0.612, 15.187, 0.990) | RMVC | 0 | hair back c left 3 |  |  |  |  | 55 | 9 |
| 146 | hair back c left 3 | hair back c left 3 | hair back c left 2 | (0.595, 14.551, 0.965) | RMVC | 0 | hair back c left 4 |  |  |  |  | 53 | 12 |
| 147 | hair back c left 4 | hair back c left 4 | hair back c left 3 | (0.618, 13.891, 1.037) | RMVC | 0 | hair back c left 5 |  |  |  |  | 42 | 14 |
| 148 | hair back c left 5 | hair back c left 5 | hair back c left 4 | (0.640, 13.231, 1.108) | RMVC | 0 | hair back c left 6 |  |  |  |  | 34 | 13 |
| 149 | hair back c left 6 | hair back c left 6 | hair back c left 5 | (0.655, 12.571, 1.160) | RMVC | 0 | hair back c left 7 |  |  |  |  | 33 | 14 |
| 150 | hair back c left 7 | hair back c left 7 | hair back c left 6 | (0.644, 11.896, 1.173) | RMVC | 0 | hair back c left 8 |  |  |  |  | 37 | 17 |
| 151 | hair back c left 8 | hair back c left 8 | hair back c left 7 | (0.625, 11.221, 1.166) | RMVC | 0 | hair back c left 9 |  |  |  |  | 46 | 17 |
| 152 | hair back c left 9 | hair back c left 9 | hair back c left 8 | (0.606, 10.546, 1.159) | RMVC | 0 | (-0.02, -0.67, -0.01) |  |  |  |  | 28 | 17 |
| 153 | hair back c right 1 | hair back c right 1 | 頭 | (-0.642, 15.681, 1.015) | RMVC | 0 | hair back c right 2 |  |  |  |  | 22 | 2 |
| 154 | hair back c right 2 | hair back c right 2 | hair back c right 1 | (-0.642, 15.185, 0.996) | RMVC | 0 | hair back c right 3 |  |  |  |  | 47 | 7 |
| 155 | hair back c right 3 | hair back c right 3 | hair back c right 2 | (-0.630, 14.549, 0.967) | RMVC | 0 | hair back c right 4 |  |  |  |  | 48 | 11 |
| 156 | hair back c right 4 | hair back c right 4 | hair back c right 3 | (-0.647, 13.890, 1.029) | RMVC | 0 | hair back c right 5 |  |  |  |  | 37 | 14 |
| 157 | hair back c right 5 | hair back c right 5 | hair back c right 4 | (-0.664, 13.231, 1.090) | RMVC | 0 | hair back c right 6 |  |  |  |  | 34 | 13 |
| 158 | hair back c right 6 | hair back c right 6 | hair back c right 5 | (-0.674, 12.572, 1.132) | RMVC | 0 | hair back c right 7 |  |  |  |  | 37 | 15 |
| 159 | hair back c right 7 | hair back c right 7 | hair back c right 6 | (-0.669, 11.896, 1.152) | RMVC | 0 | hair back c right 8 |  |  |  |  | 37 | 14 |
| 160 | hair back c right 8 | hair back c right 8 | hair back c right 7 | (-0.657, 11.221, 1.152) | RMVC | 0 | hair back c right 9 |  |  |  |  | 50 | 18 |
| 161 | hair back c right 9 | hair back c right 9 | hair back c right 8 | (-0.645, 10.545, 1.152) | RMVC | 0 | (0.01, -0.68, -0.00) |  |  |  |  | 28 | 17 |
| 162 | hair back c side left 1 | hair back c side left 1 | 頭 | (0.866, 15.656, 0.555) | RMVC | 0 | hair back c side left 2 |  |  |  |  | 71 | 14 |
| 163 | hair back c side left 2 | hair back c side left 2 | hair back c side left 1 | (0.850, 15.197, 0.591) | RMVC | 0 | hair back c side left 3 |  |  |  |  | 58 | 14 |
| 164 | hair back c side left 3 | hair back c side left 3 | hair back c side left 2 | (0.839, 14.684, 0.621) | RMVC | 0 | hair back c side left 4 |  |  |  |  | 65 | 19 |
| 165 | hair back c side left 4 | hair back c side left 4 | hair back c side left 3 | (0.848, 14.064, 0.630) | RMVC | 0 | hair back c side left 5 |  |  |  |  | 48 | 18 |
| 166 | hair back c side left 5 | hair back c side left 5 | hair back c side left 4 | (0.867, 13.449, 0.622) | RMVC | 0 | hair back c side left 6 |  |  |  |  | 33 | 15 |
| 167 | hair back c side left 6 | hair back c side left 6 | hair back c side left 5 | (0.879, 12.826, 0.626) | RMVC | 0 | hair back c side left 7 |  |  |  |  | 36 | 18 |
| 168 | hair back c side left 7 | hair back c side left 7 | hair back c side left 6 | (0.891, 12.208, 0.623) | RMVC | 0 | hair back c side left 8 |  |  |  |  | 33 | 16 |
| 169 | hair back c side left 8 | hair back c side left 8 | hair back c side left 7 | (0.901, 11.591, 0.634) | RMVC | 0 | hair back c side left 9 |  |  |  |  | 36 | 15 |
| 170 | hair back c side left 9 | hair back c side left 9 | hair back c side left 8 | (0.910, 10.973, 0.645) | RMVC | 0 | (0.01, -0.62, 0.01) |  |  |  |  | 20 | 13 |
| 171 | hair back c side right 1 | hair back c side right 1 | 頭 | (-0.878, 15.645, 0.420) | RMVC | 0 | hair back c side right 2 |  |  |  |  | 50 | 7 |
| 172 | hair back c side right 2 | hair back c side right 2 | hair back c side right 1 | (-0.866, 15.137, 0.456) | RMVC | 0 | hair back c side right 3 |  |  |  |  | 50 | 11 |
| 173 | hair back c side right 3 | hair back c side right 3 | hair back c side right 2 | (-0.838, 14.582, 0.467) | RMVC | 0 | hair back c side right 4 |  |  |  |  | 55 | 20 |
| 174 | hair back c side right 4 | hair back c side right 4 | hair back c side right 3 | (-0.844, 13.979, 0.466) | RMVC | 0 | hair back c side right 5 |  |  |  |  | 48 | 18 |
| 175 | hair back c side right 5 | hair back c side right 5 | hair back c side right 4 | (-0.851, 13.375, 0.466) | RMVC | 0 | hair back c side right 6 |  |  |  |  | 35 | 14 |
| 176 | hair back c side right 6 | hair back c side right 6 | hair back c side right 5 | (-0.857, 12.772, 0.465) | RMVC | 0 | hair back c side right 7 |  |  |  |  | 40 | 16 |
| 177 | hair back c side right 7 | hair back c side right 7 | hair back c side right 6 | (-0.863, 12.168, 0.465) | RMVC | 0 | hair back c side right 8 |  |  |  |  | 34 | 16 |
| 178 | hair back c side right 8 | hair back c side right 8 | hair back c side right 7 | (-0.869, 11.565, 0.464) | RMVC | 0 | hair back c side right 9 |  |  |  |  | 41 | 17 |
| 179 | hair back c side right 9 | hair back c side right 9 | hair back c side right 8 | (-0.876, 10.961, 0.464) | RMVC | 0 | (-0.01, -0.60, -0.00) |  |  |  |  | 24 | 17 |
| 180 | hair front middle 1 | hair front middle 1 | 頭 | (0.213, 16.221, -0.645) | RMVC | 0 | hair front middle 2 |  |  |  |  | 28 | 17 |
| 181 | hair front middle 2 | hair front middle 2 | hair front middle 1 | (0.146, 15.900, -0.788) | RMVC | 0 | hair front middle 3 |  |  |  |  | 28 | 13 |
| 182 | hair front middle 3 | hair front middle 3 | hair front middle 2 | (0.004, 15.640, -0.814) | RMVC | 0 | hair front middle 4 |  |  |  |  | 21 | 10 |
| 183 | hair front middle 4 | hair front middle 4 | hair front middle 3 | (-0.137, 15.457, -0.791) | RMVC | 0 | (-0.14, -0.18, 0.02) |  |  |  |  | 6 | 2 |
| 184 | hair front left 1 | hair front left 1 | 頭 | (0.430, 16.198, -0.548) | RMVC | 0 | hair front left 2 |  |  |  |  | 42 | 17 |
| 185 | hair front left 2 | hair front left 2 | hair front left 1 | (0.572, 15.826, -0.538) | RMVC | 0 | hair front left 3 |  |  |  |  | 66 | 24 |
| 186 | hair front left 3 | hair front left 3 | hair front left 2 | (0.631, 15.502, -0.464) | RMVC | 0 | hair front left 4 |  |  |  |  | 39 | 18 |
| 187 | hair front left 4 | hair front left 4 | hair front left 3 | (0.656, 15.131, -0.393) | RMVC | 0 | hair front left 5 |  |  |  |  | 20 | 11 |
| 188 | hair front left 5 | hair front left 5 | hair front left 4 | (0.639, 14.761, -0.328) | RMVC | 0 | (-0.02, -0.37, 0.07) |  |  |  |  | 7 | 4 |
| 189 | hair front right 1 | hair front right 1 | 頭 | (0.068, 16.456, -0.591) | RMVC | 0 | hair front right 2 |  |  |  |  | 55 | 26 |
| 190 | hair front right 2 | hair front right 2 | hair front right 1 | (-0.103, 16.294, -0.763) | RMVC | 0 | hair front right 3 |  |  |  |  | 95 | 34 |
| 191 | hair front right 3 | hair front right 3 | hair front right 2 | (-0.333, 16.018, -0.813) | RMVC | 0 | hair front right 4 |  |  |  |  | 78 | 35 |
| 192 | hair front right 4 | hair front right 4 | hair front right 3 | (-0.518, 15.709, -0.721) | RMVC | 0 | hair front right 5 |  |  |  |  | 70 | 34 |
| 193 | hair front right 5 | hair front right 5 | hair front right 4 | (-0.658, 15.399, -0.590) | RMVC | 0 | hair front right 6 |  |  |  |  | 52 | 23 |
| 194 | hair front right 6 | hair front right 6 | hair front right 5 | (-0.695, 15.085, -0.440) | RMVC | 0 | (-0.04, -0.31, 0.15) |  |  |  |  | 23 | 11 |
| 195 | hair front side right 1 | hair front side right 1 | 頭 | (-0.769, 15.902, -0.279) | RMVC | 0 | hair front side right 2 |  |  |  |  | 41 | 13 |
| 196 | hair front side right 2 | hair front side right 2 | hair front side right 1 | (-0.707, 15.338, -0.186) | RMVC | 0 | hair front side right 3 |  |  |  |  | 65 | 10 |
| 197 | hair front side right 3 | hair front side right 3 | hair front side right 2 | (-0.683, 14.873, -0.125) | RMVC | 0 | hair front side right 4 |  |  |  |  | 75 | 14 |
| 198 | hair front side right 4 | hair front side right 4 | hair front side right 3 | (-0.642, 14.378, -0.081) | RMVC | 0 | hair front side right 5 |  |  |  |  | 58 | 16 |
| 199 | hair front side right 5 | hair front side right 5 | hair front side right 4 | (-0.639, 13.924, -0.034) | RMVC | 0 | (0.00, -0.45, 0.05) |  |  |  |  | 22 | 6 |
| 200 | hair front side left 1 | hair front side left 1 | 頭 | (0.655, 15.482, -0.239) | RMVC | 0 | hair front side left 2 |  |  |  |  | 24 | 8 |
| 201 | hair front side left 2 | hair front side left 2 | hair front side left 1 | (0.633, 14.701, -0.240) | RMVC | 0 | hair front side left 3 |  |  |  |  | 51 | 16 |
| 202 | hair front side left 3 | hair front side left 3 | hair front side left 2 | (0.643, 13.740, -0.240) | RMVC | 0 | hair front side left 4 |  |  |  |  | 121 | 55 |
| 203 | hair front side left 4 | hair front side left 4 | hair front side left 3 | (0.643, 13.312, -0.240) | RMVC | 0 | hair front side left 5 |  |  |  |  | 64 | 18 |
| 204 | hair front side left 5 | hair front side left 5 | hair front side left 4 | (0.643, 13.312, -0.240) | RMVC | 0 | hair front side left 6 |  |  |  |  | 56 | 9 |
| 205 | hair front side left 6 | hair front side left 6 | hair front side left 5 | (0.643, 13.312, -0.240) | RMVC | 0 | (0.00, 0.00, 0.00) |  |  |  |  | 46 | 29 |
| 206 | 左足 | leg left thigh | センター | (0.820, 9.407, 0.156) | RMVC | 0 | (0.53, -1.98, 0.00) |  |  |  |  | 618 | 229 |
| 207 | 左ひざ | leg left knee | 左足 | (1.881, 5.447, 0.156) | RMVC | 0 | (0.56, -2.08, -0.00) |  |  |  |  | 1448 | 1058 |
| 208 | leg left foot | leg left foot | 左ひざ | (2.994, 1.293, 0.156) | RMVC | 0 | 左つま先 |  |  |  |  | 749 | 214 |
| 209 | 左つま先 | leg left toe | leg left foot | (3.217, 0.463, -0.814) | RMVC | 0 | (0.22, -0.83, -0.97) |  |  |  |  | 106 | 58 |
| 210 | leg left knee ctr | leg left knee ctr | 左ひざ | (1.881, 5.447, 0.147) | RMVC | 0 | (0.00, 0.00, -0.01) |  |  |  |  | 299 | 27 |
| 211 | leg left thigh ctr | leg left thigh ctr | 左足 | (0.823, 9.398, 0.156) | RMVC | 0 | (0.00, -0.01, 0.00) |  |  |  |  | 1758 | 330 |
| 212 | leg left thigh ctr2 | leg left thigh ctr2 | 左足 | (1.351, 7.427, 0.156) | RMVC | 0 | (0.53, -1.98, 0.00) |  |  |  |  | 699 | 149 |
| 213 | 右足 | leg right thigh | センター | (-0.820, 9.407, 0.156) | RMVC | 0 | (-0.53, -1.98, 0.00) |  |  |  |  | 14442 | 3254 |
| 214 | 右ひざ | leg right knee | 右足 | (-1.881, 5.447, 0.156) | RMVC | 0 | (-0.56, -2.08, -0.00) |  |  |  |  | 1474 | 1059 |
| 215 | leg right foot | leg right foot | 右ひざ | (-2.994, 1.293, 0.156) | RMVC | 0 | 右つま先 |  |  |  |  | 749 | 214 |
| 216 | 右つま先 | leg right toe | leg right foot | (-3.217, 0.463, -0.814) | RMVC | 0 | (-0.22, -0.83, -0.97) |  |  |  |  | 106 | 58 |
| 217 | leg right knee ctr | leg right knee ctr | 右ひざ | (-1.881, 5.447, 0.146) | RMVC | 0 | (0.00, 0.00, -0.01) |  |  |  |  | 299 | 27 |
| 218 | leg right thigh ctr | leg right thigh ctr | 右足 | (-0.823, 9.398, 0.156) | RMVC | 0 | (-0.00, -0.01, 0.00) |  |  |  |  | 15578 | 3116 |
| 219 | leg right thigh ctr2 | leg right thigh ctr2 | 右足 | (-1.351, 7.427, 0.156) | RMVC | 0 | (-0.53, -1.98, 0.00) |  |  |  |  | 14523 | 8160 |
| 220 | 左肩 | arm left shoulder 1 | 上半身2 | (0.686, 13.623, 0.273) | RMVC | 0 | 左腕 |  |  |  |  | 1774 | 201 |
| 221 | 左腕 | arm left shoulder 2 | 左肩 | (1.300, 13.560, 0.273) | RMVC | 0 | (0.90, -0.90, 0.00) |  |  |  |  | 1165 | 364 |
| 222 | 左ひじ | arm left elbow | 左腕 | (3.094, 11.766, 0.273) | RMVC | 0 | (0.86, -0.86, 0.00) |  |  |  |  | 683 | 213 |
| 223 | 左手首 | arm left wrist | 左ひじ | (4.805, 10.055, 0.273) | RMVC | 0 | (0.29, -0.21, -0.16) |  |  |  |  | 1640 | 561 |
| 224 | 左人指１ | arm left finger 2a | 左手首 | (5.388, 9.640, -0.012) | RMVC | 0 | 左人指２ |  |  |  |  | 319 | 100 |
| 225 | 左人指２ | arm left finger 2b | 左人指１ | (5.619, 9.409, -0.046) | RMVC | 0 | 左人指３ |  |  |  |  | 313 | 121 |
| 226 | 左人指３ | arm left finger 2c | 左人指２ | (5.762, 9.266, -0.067) | RMVC | 0 | (0.14, -0.14, -0.02) |  |  |  |  | 455 | 372 |
| 227 | unused arm left metacarpal | unused arm left metacarpal | 左手首 | (4.725, 10.187, 0.243) | RM-C | 0 | (0.62, -0.55, 0.26) |  |  |  |  | 608 | 235 |
| 228 | 左小指１ | arm left finger 5a | unused arm left metacarpal | (5.315, 9.642, 0.585) | RMVC | 0 | 左小指２ |  |  |  |  | 259 | 76 |
| 229 | 左小指２ | arm left finger 5b | 左小指１ | (5.487, 9.463, 0.641) | RMVC | 0 | 左小指３ |  |  |  |  | 189 | 70 |
| 230 | 左小指３ | arm left finger 5c | 左小指２ | (5.597, 9.348, 0.677) | RMVC | 0 | (0.11, -0.11, 0.04) |  |  |  |  | 314 | 268 |
| 231 | 左薬指１ | arm left finger 4a | unused arm left metacarpal | (5.377, 9.641, 0.412) | RMVC | 0 | 左薬指２ |  |  |  |  | 249 | 70 |
| 232 | 左薬指２ | arm left finger 4b | 左薬指１ | (5.600, 9.418, 0.443) | RMVC | 0 | 左薬指３ |  |  |  |  | 201 | 82 |
| 233 | 左薬指３ | arm left finger 4c | 左薬指２ | (5.753, 9.265, 0.465) | RMVC | 0 | (0.15, -0.15, 0.02) |  |  |  |  | 355 | 281 |
| 234 | 左中指１ | arm left finger 3a | 左手首 | (5.422, 9.639, 0.199) | RMVC | 0 | 左中指２ |  |  |  |  | 272 | 84 |
| 235 | 左中指２ | arm left finger 3b | 左中指１ | (5.673, 9.388, 0.199) | RMVC | 0 | 左中指３ |  |  |  |  | 218 | 70 |
| 236 | 左中指３ | arm left finger 3c | 左中指２ | (5.827, 9.234, 0.199) | RMVC | 0 | (0.15, -0.15, 0.00) |  |  |  |  | 342 | 273 |
| 237 | 左親指０ | arm left finger 1a | 左手首 | (4.844, 9.899, 0.024) | RMVC | 0 | 左親指１ |  |  |  |  | 455 | 118 |
| 238 | 左親指１ | arm left finger 1b | 左親指０ | (4.880, 9.602, -0.153) | RMVC | 0 | 左親指２ |  |  |  |  | 347 | 153 |
| 239 | 左親指２ | arm left finger 1c | 左親指１ | (4.909, 9.359, -0.298) | RMVC | 0 | (0.03, -0.24, -0.14) |  |  |  |  | 312 | 256 |
| 240 | arm left elbow ctr | arm left elbow ctr | 左ひじ | (3.094, 11.766, 0.283) | RMVC | 0 | (-0.00, 0.00, 0.01) |  |  |  |  | 182 | 20 |
| 241 | arm left elbow ctr2 | arm left elbow ctr2 | 左ひじ | (3.665, 11.196, 0.273) | RMVC | 0 | (0.57, -0.57, 0.00) |  |  |  |  | 946 | 209 |
| 242 | arm left wrist ctr | arm left wrist ctr | 左ひじ | (4.235, 10.625, 0.273) | RMVC | 0 | (1.14, -1.14, 0.00) |  |  |  |  | 1077 | 675 |
| 243 | arm left shoulder 2 ctr | arm left shoulder 2 ctr | 左腕 | (1.308, 13.553, 0.273) | RMVC | 0 | (0.01, -0.01, 0.00) |  |  |  |  | 1506 | 545 |
| 244 | arm left shoulder 2 ctr2 | arm left shoulder 2 ctr2 | 左腕 | (2.197, 12.663, 0.273) | RMVC | 0 | (0.90, -0.90, 0.00) |  |  |  |  | 964 | 292 |
| 245 | 右肩 | arm right shoulder 1 | 上半身2 | (-0.686, 13.623, 0.273) | RMVC | 0 | 右腕 |  |  |  |  | 1785 | 202 |
| 246 | 右腕 | arm right shoulder 2 | 右肩 | (-1.300, 13.560, 0.273) | RMVC | 0 | (-0.90, -0.90, 0.00) |  |  |  |  | 1167 | 366 |
| 247 | 右ひじ | arm right elbow | 右腕 | (-3.094, 11.766, 0.273) | RMVC | 0 | (-0.86, -0.86, 0.00) |  |  |  |  | 683 | 212 |
| 248 | 右手首 | arm right wrist | 右ひじ | (-4.805, 10.055, 0.273) | RMVC | 0 | (-0.29, -0.21, -0.16) |  |  |  |  | 1646 | 559 |
| 249 | 右人指１ | arm right finger 2a | 右手首 | (-5.393, 9.646, -0.012) | RMVC | 0 | 右人指２ |  |  |  |  | 301 | 100 |
| 250 | 右人指２ | arm right finger 2b | 右人指１ | (-5.625, 9.415, -0.046) | RMVC | 0 | 右人指３ |  |  |  |  | 315 | 120 |
| 251 | 右人指３ | arm right finger 2c | 右人指２ | (-5.767, 9.272, -0.067) | RMVC | 0 | (-0.14, -0.14, -0.02) |  |  |  |  | 457 | 374 |
| 252 | unused arm right metacarpal | unused arm right metacarpal | 右手首 | (-4.727, 10.188, 0.243) | RM-C | 0 | (-0.62, -0.54, 0.26) |  |  |  |  | 612 | 234 |
| 253 | 右小指１ | arm right finger 5a | unused arm right metacarpal | (-5.318, 9.645, 0.585) | RMVC | 0 | 右小指２ |  |  |  |  | 261 | 75 |
| 254 | 右小指２ | arm right finger 5b | 右小指１ | (-5.490, 9.466, 0.641) | RMVC | 0 | 右小指３ |  |  |  |  | 193 | 70 |
| 255 | 右小指３ | arm right finger 5c | 右小指２ | (-5.600, 9.351, 0.677) | RMVC | 0 | (-0.11, -0.11, 0.04) |  |  |  |  | 314 | 269 |
| 256 | 右薬指１ | arm right finger 4a | unused arm right metacarpal | (-5.382, 9.647, 0.412) | RMVC | 0 | 右薬指２ |  |  |  |  | 252 | 71 |
| 257 | 右薬指２ | arm right finger 4b | 右薬指１ | (-5.605, 9.424, 0.443) | RMVC | 0 | 右薬指３ |  |  |  |  | 201 | 83 |
| 258 | 右薬指３ | arm right finger 4c | 右薬指２ | (-5.759, 9.270, 0.465) | RMVC | 0 | (-0.15, -0.15, 0.02) |  |  |  |  | 360 | 281 |
| 259 | 右中指１ | arm right finger 3a | 右手首 | (-5.429, 9.646, 0.199) | RMVC | 0 | 右中指２ |  |  |  |  | 277 | 82 |
| 260 | 右中指２ | arm right finger 3b | 右中指１ | (-5.680, 9.395, 0.199) | RMVC | 0 | 右中指３ |  |  |  |  | 225 | 71 |
| 261 | 右中指３ | arm right finger 3c | 右中指２ | (-5.834, 9.241, 0.199) | RMVC | 0 | (-0.15, -0.15, 0.00) |  |  |  |  | 339 | 273 |
| 262 | 右親指０ | arm right finger 1a | 右手首 | (-4.840, 9.894, 0.024) | RMVC | 0 | 右親指１ |  |  |  |  | 459 | 115 |
| 263 | 右親指１ | arm right finger 1b | 右親指０ | (-4.867, 9.588, -0.153) | RMVC | 0 | 右親指２ |  |  |  |  | 357 | 157 |
| 264 | 右親指２ | arm right finger 1c | 右親指１ | (-4.889, 9.338, -0.298) | RMVC | 0 | (-0.02, -0.25, -0.14) |  |  |  |  | 316 | 255 |
| 265 | arm right elbow ctr | arm right elbow ctr | 右ひじ | (-3.094, 11.766, 0.283) | RMVC | 0 | (0.00, 0.00, 0.01) |  |  |  |  | 188 | 20 |
| 266 | arm right elbow ctr2 | arm right elbow ctr2 | 右ひじ | (-3.665, 11.196, 0.273) | RMVC | 0 | (-0.57, -0.57, 0.00) |  |  |  |  | 943 | 209 |
| 267 | arm right wrist ctr | arm right wrist ctr | 右ひじ | (-4.235, 10.625, 0.273) | RMVC | 0 | (-1.14, -1.14, 0.00) |  |  |  |  | 1077 | 674 |
| 268 | arm right shoulder 2 ctr | arm right shoulder 2 ctr | 右腕 | (-1.308, 13.553, 0.273) | RMVC | 0 | (-0.01, -0.01, 0.00) |  |  |  |  | 1516 | 547 |
| 269 | arm right shoulder 2 ctr2 | arm right shoulder 2 ctr2 | 右腕 | (-2.197, 12.663, 0.273) | RMVC | 0 | (-0.90, -0.90, 0.00) |  |  |  |  | 964 | 292 |
| 270 | breast left base | breast left base | 上半身2 | (0.603, 12.580, -0.536) | RMVC | 0 | breast left tip |  |  |  |  | 406 | 19 |
| 271 | breast left tip | breast left tip | breast left base | (0.879, 12.580, -1.422) | RMVC | 0 | (-0.16, 0.32, 0.52) |  |  |  |  | 458 | 275 |
| 272 | breast left a | breast left a | breast left tip | (0.075, 12.580, -1.104) | RMVC | 0 | (-0.80, 0.00, 0.32) |  |  |  |  | 176 | 20 |
| 273 | breast left b | breast left b | breast left tip | (0.263, 13.056, -1.045) | RMVC | 0 | (-0.62, 0.48, 0.38) |  |  |  |  | 371 | 53 |
| 274 | breast left c | breast left c | breast left tip | (0.718, 13.253, -0.904) | RMVC | 0 | (-0.16, 0.67, 0.52) |  |  |  |  | 341 | 38 |
| 275 | breast left d | breast left d | breast left tip | (1.172, 13.056, -0.762) | RMVC | 0 | (0.29, 0.48, 0.66) |  |  |  |  | 178 | 15 |
| 276 | breast left e | breast left e | breast left tip | (1.360, 12.580, -0.704) | RMVC | 0 | (0.48, 0.00, 0.72) |  |  |  |  | 234 | 43 |
| 277 | breast right base | breast right base | 上半身2 | (-0.603, 12.580, -0.536) | RMVC | 0 | breast right tip |  |  |  |  | 406 | 19 |
| 278 | breast right tip | breast right tip | breast right base | (-0.879, 12.580, -1.422) | RMVC | 0 | (0.16, 0.32, 0.52) |  |  |  |  | 456 | 275 |
| 279 | breast right a | breast right a | breast right tip | (-0.075, 12.580, -1.104) | RMVC | 0 | (0.80, 0.00, 0.32) |  |  |  |  | 177 | 20 |
| 280 | breast right b | breast right b | breast right tip | (-0.263, 13.056, -1.045) | RMVC | 0 | (0.62, 0.48, 0.38) |  |  |  |  | 371 | 53 |
| 281 | breast right c | breast right c | breast right tip | (-0.718, 13.253, -0.904) | RMVC | 0 | (0.16, 0.67, 0.52) |  |  |  |  | 339 | 38 |
| 282 | breast right d | breast right d | breast right tip | (-1.172, 13.056, -0.762) | RMVC | 0 | (-0.29, 0.48, 0.66) |  |  |  |  | 178 | 15 |
| 283 | breast right e | breast right e | breast right tip | (-1.360, 12.580, -0.704) | RMVC | 0 | (-0.48, 0.00, 0.72) |  |  |  |  | 234 | 43 |
| 284 | leg left butt ctr | leg left butt ctr | センター | (0.817, 9.417, 0.156) | RMVC | 0 | (0.82, -0.90, 0.16) |  |  |  |  | 685 | 42 |
| 285 | leg right butt ctr | leg right butt ctr | センター | (-0.817, 9.417, 0.156) | RMVC | 0 | (-0.82, -0.90, 0.16) |  |  |  |  | 682 | 42 |
| 286 | unused head neck upper attached-new naotora face +2 head neck l item-full head +4 | unused head neck upper attached-new naotora face +2 head neck l item-full head +4 | 頭 | (0.000, 14.146, 0.280) | RM-C | 0 | unused head neck upper attached-full head +4 head neck upper |  |  |  |  | 0 | 0 |
| 287 | unused head neck upper attached-full head +4 head neck upper | unused head neck upper attached-full head +4 head neck upper | unused head neck upper attached-new naotora face +2 head neck l item-full head +4 | (0.000, 14.846, 0.149) | RM-C | 0 | (0.00, 0.78, -0.25) |  |  |  |  | 0 | 0 |
| 288 | unused head eyebrow middle | unused head eyebrow middle | unused face | (0.000, 15.582, -0.777) | RM-C | 0 | (-0.00, 0.70, -0.90) |  |  |  |  | 0 | 0 |
| 289 | unused head lip upper middle | unused head lip upper middle | unused face | (0.000, 14.981, -0.812) | RM-C | 0 | (-0.00, 0.10, -0.93) |  |  |  |  | 0 | 0 |
| 290 | unused head nose middle | unused head nose middle | unused face | (0.000, 15.187, -0.949) | RM-C | 0 | (-0.00, 0.31, -1.07) |  |  |  |  | 0 | 0 |
| 291 | unused head jaw | unused head jaw | unused face | (0.000, 15.137, -0.073) | RM-C | 0 | (0.00, -0.24, -0.45) |  |  |  |  | 0 | 0 |
| 292 | unused head lip lower middle | unused head lip lower middle | unused head jaw | (0.000, 14.904, -0.773) | RM-C | 0 | (0.00, -0.23, -0.70) |  |  |  |  | 0 | 0 |
| 293 | unused head tongue a | unused head tongue a | unused head jaw | (0.000, 14.913, -0.162) | RM-C | 0 | unused head tongue b |  |  |  |  | 0 | 0 |
| 294 | unused head tongue b | unused head tongue b | unused head tongue a | (0.000, 14.942, -0.476) | RM-C | 0 | (0.00, 0.03, -0.31) |  |  |  |  | 0 | 0 |
| 295 | unused head lip lower left | unused head lip lower left | unused head jaw | (0.116, 14.907, -0.731) | RM-C | 0 | (0.12, -0.23, -0.66) |  |  |  |  | 0 | 0 |
| 296 | unused head lip lower right | unused head lip lower right | unused head jaw | (-0.116, 14.907, -0.731) | RM-C | 0 | (-0.12, -0.23, -0.66) |  |  |  |  | 0 | 0 |
| 297 | unused head cheek left a | unused head cheek left a | unused head neck upper attached-full head +4 head neck upper | (0.281, 15.307, -0.659) | RM-C | 0 | (0.28, 0.46, -0.81) |  |  |  |  | 0 | 0 |
| 298 | unused head cheek left b | unused head cheek left b | unused head neck upper attached-full head +4 head neck upper | (0.452, 15.356, -0.568) | RM-C | 0 | (0.45, 0.51, -0.72) |  |  |  |  | 0 | 0 |
| 299 | unused head cheek left c | unused head cheek left c | unused head neck upper attached-full head +4 head neck upper | (0.503, 15.050, -0.388) | RM-C | 0 | (0.50, 0.20, -0.54) |  |  |  |  | 0 | 0 |
| 300 | unused head eyeball left | unused head eyeball left | unused face | (0.284, 15.502, -0.511) | RM-C | 0 | (0.28, 0.62, -0.63) |  |  |  |  | 0 | 0 |
| 301 | unused head eyelid lower left a | unused head eyelid lower left a | unused head neck upper attached-full head +4 head neck upper | (0.221, 15.455, -0.625) | RM-C | 0 | (0.22, 0.61, -0.77) |  |  |  |  | 0 | 0 |
| 302 | unused head eyelid lower left b | unused head eyelid lower left b | unused head neck upper attached-full head +4 head neck upper | (0.310, 15.438, -0.634) | RM-C | 0 | (0.31, 0.59, -0.78) |  |  |  |  | 0 | 0 |
| 303 | unused head eyebrow left a | unused head eyebrow left a | unused head neck upper attached-full head +4 head neck upper | (0.142, 15.629, -0.771) | RM-C | 0 | (0.14, 0.78, -0.92) |  |  |  |  | 0 | 0 |
| 304 | unused head eyebrow left b | unused head eyebrow left b | unused head neck upper attached-full head +4 head neck upper | (0.323, 15.679, -0.723) | RM-C | 0 | (0.32, 0.83, -0.87) |  |  |  |  | 0 | 0 |
| 305 | unused head eyebrow left c | unused head eyebrow left c | unused head neck upper attached-full head +4 head neck upper | (0.459, 15.667, -0.592) | RM-C | 0 | (0.46, 0.82, -0.74) |  |  |  |  | 0 | 0 |
| 306 | unused head eyelid upper left | unused head eyelid upper left | unused head neck upper attached-full head +4 head neck upper | (0.284, 15.502, -0.506) | RM-C | 0 | (0.28, 0.66, -0.65) |  |  |  |  | 0 | 0 |
| 307 | unused head forehead left | unused head forehead left | unused face | (0.296, 15.793, -0.726) | RM-C | 0 | (0.30, 0.91, -0.85) |  |  |  |  | 0 | 0 |
| 308 | unused head lip corner left | unused head lip corner left | unused face | (0.207, 14.935, -0.642) | RM-C | 0 | (0.21, 0.06, -0.76) |  |  |  |  | 0 | 0 |
| 309 | unused head lip upper left | unused head lip upper left | unused face | (0.115, 14.961, -0.740) | RM-C | 0 | (0.12, 0.08, -0.86) |  |  |  |  | 0 | 0 |
| 310 | unused head nose left a | unused head nose left a | unused head neck upper attached-full head +4 head neck upper | (0.124, 15.362, -0.700) | RM-C | 0 | (0.12, 0.52, -0.85) |  |  |  |  | 0 | 0 |
| 311 | unused head nose left b | unused head nose left b | unused head neck upper attached-full head +4 head neck upper | (0.146, 15.135, -0.719) | RM-C | 0 | (0.15, 0.29, -0.87) |  |  |  |  | 0 | 0 |
| 312 | unused head nose left c | unused head nose left c | unused head neck upper attached-full head +4 head neck upper | (0.213, 15.081, -0.676) | RM-C | 0 | (0.21, 0.23, -0.82) |  |  |  |  | 0 | 0 |
| 313 | unused head nose left d | unused head nose left d | unused head neck upper attached-full head +4 head neck upper | (0.289, 14.964, -0.617) | RM-C | 0 | (0.29, 0.12, -0.77) |  |  |  |  | 0 | 0 |
| 314 | unused head cheek right a | unused head cheek right a | unused head neck upper attached-full head +4 head neck upper | (-0.281, 15.307, -0.659) | RM-C | 0 | (-0.28, 0.46, -0.81) |  |  |  |  | 0 | 0 |
| 315 | unused head cheek right b | unused head cheek right b | unused head neck upper attached-full head +4 head neck upper | (-0.452, 15.356, -0.568) | RM-C | 0 | (-0.45, 0.51, -0.72) |  |  |  |  | 0 | 0 |
| 316 | unused head cheek right c | unused head cheek right c | unused head neck upper attached-full head +4 head neck upper | (-0.503, 15.050, -0.388) | RM-C | 0 | (-0.50, 0.20, -0.54) |  |  |  |  | 0 | 0 |
| 317 | unused head eyeball right | unused head eyeball right | unused face | (-0.285, 15.502, -0.511) | RM-C | 0 | (-0.28, 0.62, -0.63) |  |  |  |  | 0 | 0 |
| 318 | unused head eyelid lower right a | unused head eyelid lower right a | unused head neck upper attached-full head +4 head neck upper | (-0.221, 15.455, -0.625) | RM-C | 0 | (-0.22, 0.61, -0.77) |  |  |  |  | 0 | 0 |
| 319 | unused head eyelid lower right b | unused head eyelid lower right b | unused head neck upper attached-full head +4 head neck upper | (-0.310, 15.438, -0.634) | RM-C | 0 | (-0.31, 0.59, -0.78) |  |  |  |  | 0 | 0 |
| 320 | unused head eyebrow right a | unused head eyebrow right a | unused head neck upper attached-full head +4 head neck upper | (-0.142, 15.629, -0.771) | RM-C | 0 | (-0.14, 0.78, -0.92) |  |  |  |  | 0 | 0 |
| 321 | unused head eyebrow right b | unused head eyebrow right b | unused head neck upper attached-full head +4 head neck upper | (-0.323, 15.679, -0.723) | RM-C | 0 | (-0.32, 0.83, -0.87) |  |  |  |  | 0 | 0 |
| 322 | unused head eyebrow right c | unused head eyebrow right c | unused head neck upper attached-full head +4 head neck upper | (-0.459, 15.667, -0.592) | RM-C | 0 | (-0.46, 0.82, -0.74) |  |  |  |  | 0 | 0 |
| 323 | unused head eyelid upper right | unused head eyelid upper right | unused head neck upper attached-full head +4 head neck upper | (-0.285, 15.502, -0.506) | RM-C | 0 | (-0.28, 0.66, -0.65) |  |  |  |  | 0 | 0 |
| 324 | unused head forehead right | unused head forehead right | unused face | (-0.296, 15.793, -0.726) | RM-C | 0 | (-0.30, 0.91, -0.85) |  |  |  |  | 0 | 0 |
| 325 | unused head lip corner right | unused head lip corner right | unused face | (-0.207, 14.935, -0.642) | RM-C | 0 | (-0.21, 0.06, -0.76) |  |  |  |  | 0 | 0 |
| 326 | unused head lip upper right | unused head lip upper right | unused face | (-0.116, 14.961, -0.740) | RM-C | 0 | (-0.12, 0.08, -0.86) |  |  |  |  | 0 | 0 |
| 327 | unused head nose right a | unused head nose right a | unused head neck upper attached-full head +4 head neck upper | (-0.124, 15.362, -0.700) | RM-C | 0 | (-0.12, 0.52, -0.85) |  |  |  |  | 0 | 0 |
| 328 | unused head nose right b | unused head nose right b | unused head neck upper attached-full head +4 head neck upper | (-0.146, 15.135, -0.719) | RM-C | 0 | (-0.15, 0.29, -0.87) |  |  |  |  | 0 | 0 |
| 329 | unused head nose right c | unused head nose right c | unused head neck upper attached-full head +4 head neck upper | (-0.213, 15.081, -0.676) | RM-C | 0 | (-0.21, 0.23, -0.82) |  |  |  |  | 0 | 0 |
| 330 | unused head nose right d | unused head nose right d | unused head neck upper attached-full head +4 head neck upper | (-0.289, 14.964, -0.617) | RM-C | 0 | (-0.29, 0.12, -0.77) |  |  |  |  | 0 | 0 |
| 331 | unused hair middle front a | unused hair middle front a | unused head neck upper attached-full head +4 head neck upper | (0.012, 16.597, -0.451) | RM-C | 0 | unused hair middle front b |  |  |  |  | 0 | 0 |
| 332 | unused hair middle front b | unused hair middle front b | unused hair middle front a | (0.029, 16.436, -0.682) | RM-C | 0 | unused hair middle front c |  |  |  |  | 0 | 0 |
| 333 | unused hair middle front c | unused hair middle front c | unused hair middle front b | (0.033, 16.170, -0.813) | RM-C | 0 | unused hair middle front d |  |  |  |  | 0 | 0 |
| 334 | unused hair middle front d | unused hair middle front d | unused hair middle front c | (0.004, 15.843, -0.854) | RM-C | 0 | unused hair middle front e |  |  |  |  | 0 | 0 |
| 335 | unused hair middle front e | unused hair middle front e | unused hair middle front d | (-0.056, 15.490, -0.854) | RM-C | 0 | (-0.06, -0.35, -0.00) |  |  |  |  | 0 | 0 |
| 336 | unused hair left front a | unused hair left front a | unused head neck upper attached-full head +4 head neck upper | (0.086, 16.536, -0.515) | RM-C | 0 | unused hair left front b |  |  |  |  | 0 | 0 |
| 337 | unused hair left front b | unused hair left front b | unused hair left front a | (0.352, 16.349, -0.613) | RM-C | 0 | unused hair left front c |  |  |  |  | 0 | 0 |
| 338 | unused hair left front c | unused hair left front c | unused hair left front b | (0.508, 15.988, -0.641) | RM-C | 0 | unused hair left front d |  |  |  |  | 0 | 0 |
| 339 | unused hair left front d | unused hair left front d | unused hair left front c | (0.563, 15.604, -0.613) | RM-C | 0 | unused hair left front e |  |  |  |  | 0 | 0 |
| 340 | unused hair left front e | unused hair left front e | unused hair left front d | (0.569, 15.167, -0.559) | RM-C | 0 | (0.01, -0.44, 0.05) |  |  |  |  | 0 | 0 |
| 341 | unused hair right front a | unused hair right front a | unused head neck upper attached-full head +4 head neck upper | (-0.086, 16.536, -0.515) | RM-C | 0 | unused hair right front b |  |  |  |  | 0 | 0 |
| 342 | unused hair right front b | unused hair right front b | unused hair right front a | (-0.352, 16.349, -0.613) | RM-C | 0 | unused hair right front c |  |  |  |  | 0 | 0 |
| 343 | unused hair right front c | unused hair right front c | unused hair right front b | (-0.508, 15.989, -0.641) | RM-C | 0 | unused hair right front d |  |  |  |  | 0 | 0 |
| 344 | unused hair right front d | unused hair right front d | unused hair right front c | (-0.563, 15.604, -0.613) | RM-C | 0 | unused hair right front e |  |  |  |  | 0 | 0 |
| 345 | unused hair right front e | unused hair right front e | unused hair right front d | (-0.569, 15.167, -0.559) | RM-C | 0 | (-0.01, -0.44, 0.05) |  |  |  |  | 0 | 0 |
| 346 | unused hair left front 2a | unused hair left front 2a | unused head neck upper attached-full head +4 head neck upper | (0.652, 16.084, -0.283) | RM-C | 0 | unused hair left front 2b |  |  |  |  | 0 | 0 |
| 347 | unused hair left front 2b | unused hair left front 2b | unused hair left front 2a | (0.652, 15.679, -0.283) | RM-C | 0 | unused hair left front 2c |  |  |  |  | 0 | 0 |
| 348 | unused hair left front 2c | unused hair left front 2c | unused hair left front 2b | (0.652, 15.275, -0.283) | RM-C | 0 | unused hair left front 2d |  |  |  |  | 0 | 0 |
| 349 | unused hair left front 2d | unused hair left front 2d | unused hair left front 2c | (0.652, 14.870, -0.283) | RM-C | 0 | unused hair left front 2e |  |  |  |  | 0 | 0 |
| 350 | unused hair left front 2e | unused hair left front 2e | unused hair left front 2d | (0.652, 14.465, -0.283) | RM-C | 0 | unused hair left front 2f |  |  |  |  | 0 | 0 |
| 351 | unused hair left front 2f | unused hair left front 2f | unused hair left front 2e | (0.652, 14.061, -0.283) | RM-C | 0 | unused hair left front 2g |  |  |  |  | 0 | 0 |
| 352 | unused hair left front 2g | unused hair left front 2g | unused hair left front 2f | (0.652, 13.656, -0.283) | RM-C | 0 | (0.00, -0.40, 0.00) |  |  |  |  | 0 | 0 |
| 353 | unused hair right front 2a | unused hair right front 2a | unused head neck upper attached-full head +4 head neck upper | (-0.652, 16.084, -0.283) | RM-C | 0 | unused hair right front 2b |  |  |  |  | 0 | 0 |
| 354 | unused hair right front 2b | unused hair right front 2b | unused hair right front 2a | (-0.652, 15.679, -0.283) | RM-C | 0 | unused hair right front 2c |  |  |  |  | 0 | 0 |
| 355 | unused hair right front 2c | unused hair right front 2c | unused hair right front 2b | (-0.652, 15.275, -0.283) | RM-C | 0 | unused hair right front 2d |  |  |  |  | 0 | 0 |
| 356 | unused hair right front 2d | unused hair right front 2d | unused hair right front 2c | (-0.652, 14.870, -0.283) | RM-C | 0 | unused hair right front 2e |  |  |  |  | 0 | 0 |
| 357 | unused hair right front 2e | unused hair right front 2e | unused hair right front 2d | (-0.652, 14.465, -0.283) | RM-C | 0 | unused hair right front 2f |  |  |  |  | 0 | 0 |
| 358 | unused hair right front 2f | unused hair right front 2f | unused hair right front 2e | (-0.652, 14.061, -0.283) | RM-C | 0 | unused hair right front 2g |  |  |  |  | 0 | 0 |
| 359 | unused hair right front 2g | unused hair right front 2g | unused hair right front 2f | (-0.652, 13.656, -0.283) | RM-C | 0 | (-0.00, -0.40, 0.00) |  |  |  |  | 0 | 0 |
| 360 | unused hair back 5a | unused hair back 5a | unused head neck upper attached-full head +4 head neck upper | (0.248, 15.661, 0.906) | RM-C | 0 | unused hair back 5b |  |  |  |  | 0 | 0 |
| 361 | unused hair back 5b | unused hair back 5b | unused hair back 5a | (0.246, 15.210, 0.903) | RM-C | 0 | unused hair back 5c |  |  |  |  | 0 | 0 |
| 362 | unused hair back 5c | unused hair back 5c | unused hair back 5b | (0.244, 14.758, 0.899) | RM-C | 0 | unused hair back 5d |  |  |  |  | 0 | 0 |
| 363 | unused hair back 5d | unused hair back 5d | unused hair back 5c | (0.243, 14.306, 0.896) | RM-C | 0 | unused hair back 5e |  |  |  |  | 0 | 0 |
| 364 | unused hair back 5e | unused hair back 5e | unused hair back 5d | (0.241, 13.855, 0.893) | RM-C | 0 | unused hair back 5f |  |  |  |  | 0 | 0 |
| 365 | unused hair back 5f | unused hair back 5f | unused hair back 5e | (0.239, 13.403, 0.890) | RM-C | 0 | unused hair back 5g |  |  |  |  | 0 | 0 |
| 366 | unused hair back 5g | unused hair back 5g | unused hair back 5f | (0.237, 12.951, 0.886) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 367 | unused hair left back 3a | unused hair left back 3a | unused head neck upper attached-full head +4 head neck upper | (0.616, 15.660, 0.617) | RM-C | 0 | unused hair left back 3b |  |  |  |  | 0 | 0 |
| 368 | unused hair left back 3b | unused hair left back 3b | unused hair left back 3a | (0.612, 15.209, 0.614) | RM-C | 0 | unused hair left back 3c |  |  |  |  | 0 | 0 |
| 369 | unused hair left back 3c | unused hair left back 3c | unused hair left back 3b | (0.609, 14.757, 0.612) | RM-C | 0 | unused hair left back 3d |  |  |  |  | 0 | 0 |
| 370 | unused hair left back 3d | unused hair left back 3d | unused hair left back 3c | (0.605, 14.305, 0.609) | RM-C | 0 | unused hair left back 3e |  |  |  |  | 0 | 0 |
| 371 | unused hair left back 3e | unused hair left back 3e | unused hair left back 3d | (0.602, 13.853, 0.606) | RM-C | 0 | unused hair left back 3f |  |  |  |  | 0 | 0 |
| 372 | unused hair left back 3f | unused hair left back 3f | unused hair left back 3e | (0.598, 13.402, 0.603) | RM-C | 0 | unused hair left back 3g |  |  |  |  | 0 | 0 |
| 373 | unused hair left back 3g | unused hair left back 3g | unused hair left back 3f | (0.595, 12.950, 0.601) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 374 | unused hair left back 2a | unused hair left back 2a | unused head neck upper attached-full head +4 head neck upper | (0.726, 15.661, 0.427) | RM-C | 0 | unused hair left back 2b |  |  |  |  | 0 | 0 |
| 375 | unused hair left back 2b | unused hair left back 2b | unused hair left back 2a | (0.722, 15.209, 0.425) | RM-C | 0 | unused hair left back 2c |  |  |  |  | 0 | 0 |
| 376 | unused hair left back 2c | unused hair left back 2c | unused hair left back 2b | (0.718, 14.757, 0.423) | RM-C | 0 | unused hair left back 2d |  |  |  |  | 0 | 0 |
| 377 | unused hair left back 2d | unused hair left back 2d | unused hair left back 2c | (0.715, 14.305, 0.421) | RM-C | 0 | unused hair left back 2e |  |  |  |  | 0 | 0 |
| 378 | unused hair left back 2e | unused hair left back 2e | unused hair left back 2d | (0.711, 13.854, 0.419) | RM-C | 0 | unused hair left back 2f |  |  |  |  | 0 | 0 |
| 379 | unused hair left back 2f | unused hair left back 2f | unused hair left back 2e | (0.707, 13.402, 0.417) | RM-C | 0 | unused hair left back 2g |  |  |  |  | 0 | 0 |
| 380 | unused hair left back 2g | unused hair left back 2g | unused hair left back 2f | (0.703, 12.950, 0.415) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 381 | unused hair back 3a | unused hair back 3a | unused head neck upper attached-full head +4 head neck upper | (-0.239, 15.665, 0.906) | RM-C | 0 | unused hair back 3b |  |  |  |  | 0 | 0 |
| 382 | unused hair back 3b | unused hair back 3b | unused hair back 3a | (-0.240, 15.214, 0.904) | RM-C | 0 | unused hair back 3c |  |  |  |  | 0 | 0 |
| 383 | unused hair back 3c | unused hair back 3c | unused hair back 3b | (-0.241, 14.762, 0.902) | RM-C | 0 | unused hair back 3d |  |  |  |  | 0 | 0 |
| 384 | unused hair back 3d | unused hair back 3d | unused hair back 3c | (-0.242, 14.310, 0.900) | RM-C | 0 | unused hair back 3e |  |  |  |  | 0 | 0 |
| 385 | unused hair back 3e | unused hair back 3e | unused hair back 3d | (-0.243, 13.858, 0.898) | RM-C | 0 | unused hair back 3f |  |  |  |  | 0 | 0 |
| 386 | unused hair back 3f | unused hair back 3f | unused hair back 3e | (-0.243, 13.407, 0.896) | RM-C | 0 | unused hair back 3g |  |  |  |  | 0 | 0 |
| 387 | unused hair back 3g | unused hair back 3g | unused hair back 3f | (-0.244, 12.955, 0.895) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 388 | unused hair right back 4a | unused hair right back 4a | unused head neck upper attached-full head +4 head neck upper | (-0.607, 15.670, 0.618) | RM-C | 0 | unused hair right back 4b |  |  |  |  | 0 | 0 |
| 389 | unused hair right back 4b | unused hair right back 4b | unused hair right back 4a | (-0.609, 15.218, 0.617) | RM-C | 0 | unused hair right back 4c |  |  |  |  | 0 | 0 |
| 390 | unused hair right back 4c | unused hair right back 4c | unused hair right back 4b | (-0.610, 14.767, 0.617) | RM-C | 0 | unused hair right back 4d |  |  |  |  | 0 | 0 |
| 391 | unused hair right back 4d | unused hair right back 4d | unused hair right back 4c | (-0.612, 14.315, 0.616) | RM-C | 0 | unused hair right back 4e |  |  |  |  | 0 | 0 |
| 392 | unused hair right back 4e | unused hair right back 4e | unused hair right back 4d | (-0.614, 13.863, 0.615) | RM-C | 0 | unused hair right back 4f |  |  |  |  | 0 | 0 |
| 393 | unused hair right back 4f | unused hair right back 4f | unused hair right back 4e | (-0.615, 13.411, 0.615) | RM-C | 0 | unused hair right back 4g |  |  |  |  | 0 | 0 |
| 394 | unused hair right back 4g | unused hair right back 4g | unused hair right back 4f | (-0.617, 12.960, 0.614) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 395 | unused hair right back 3a | unused hair right back 3a | unused head neck upper attached-full head +4 head neck upper | (-0.717, 15.672, 0.428) | RM-C | 0 | unused hair right back 3b |  |  |  |  | 0 | 0 |
| 396 | unused hair right back 3b | unused hair right back 3b | unused hair right back 3a | (-0.720, 15.220, 0.427) | RM-C | 0 | unused hair right back 3c |  |  |  |  | 0 | 0 |
| 397 | unused hair right back 3c | unused hair right back 3c | unused hair right back 3b | (-0.722, 14.769, 0.427) | RM-C | 0 | unused hair right back 3d |  |  |  |  | 0 | 0 |
| 398 | unused hair right back 3d | unused hair right back 3d | unused hair right back 3c | (-0.725, 14.317, 0.427) | RM-C | 0 | unused hair right back 3e |  |  |  |  | 0 | 0 |
| 399 | unused hair right back 3e | unused hair right back 3e | unused hair right back 3d | (-0.727, 13.865, 0.426) | RM-C | 0 | unused hair right back 3f |  |  |  |  | 0 | 0 |
| 400 | unused hair right back 3f | unused hair right back 3f | unused hair right back 3e | (-0.730, 13.414, 0.426) | RM-C | 0 | unused hair right back 3g |  |  |  |  | 0 | 0 |
| 401 | unused hair right back 3g | unused hair right back 3g | unused hair right back 3f | (-0.732, 12.962, 0.425) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 402 | unused hair back 4a | unused hair back 4a | unused head neck upper attached-full head +4 head neck upper | (0.007, 15.982, 1.041) | RM-C | 0 | unused hair back 4b |  |  |  |  | 0 | 0 |
| 403 | unused hair back 4b | unused hair back 4b | unused hair back 4a | (0.005, 15.573, 1.039) | RM-C | 0 | unused hair back 4c |  |  |  |  | 0 | 0 |
| 404 | unused hair back 4c | unused hair back 4c | unused hair back 4b | (0.004, 15.164, 1.036) | RM-C | 0 | unused hair back 4d |  |  |  |  | 0 | 0 |
| 405 | unused hair back 4d | unused hair back 4d | unused hair back 4c | (0.002, 14.754, 1.034) | RM-C | 0 | unused hair back 4e |  |  |  |  | 0 | 0 |
| 406 | unused hair back 4e | unused hair back 4e | unused hair back 4d | (0.001, 14.345, 1.031) | RM-C | 0 | unused hair back 4f |  |  |  |  | 0 | 0 |
| 407 | unused hair back 4f | unused hair back 4f | unused hair back 4e | (-0.001, 13.936, 1.029) | RM-C | 0 | unused hair back 4g |  |  |  |  | 0 | 0 |
| 408 | unused hair back 4g | unused hair back 4g | unused hair back 4f | (-0.002, 13.527, 1.026) | RM-C | 0 | unused hair back 4h |  |  |  |  | 0 | 0 |
| 409 | unused hair back 4h | unused hair back 4h | unused hair back 4g | (-0.004, 13.118, 1.023) | RM-C | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 410 | unused hair back 7a | unused hair back 7a | unused head neck upper attached-full head +4 head neck upper | (0.434, 15.979, 0.889) | RM-C | 0 | unused hair back 7b |  |  |  |  | 0 | 0 |
| 411 | unused hair back 7b | unused hair back 7b | unused hair back 7a | (0.431, 15.570, 0.886) | RM-C | 0 | unused hair back 7c |  |  |  |  | 0 | 0 |
| 412 | unused hair back 7c | unused hair back 7c | unused hair back 7b | (0.429, 15.161, 0.883) | RM-C | 0 | unused hair back 7d |  |  |  |  | 0 | 0 |
| 413 | unused hair back 7d | unused hair back 7d | unused hair back 7c | (0.426, 14.752, 0.880) | RM-C | 0 | unused hair back 7e |  |  |  |  | 0 | 0 |
| 414 | unused hair back 7e | unused hair back 7e | unused hair back 7d | (0.423, 14.343, 0.877) | RM-C | 0 | unused hair back 7f |  |  |  |  | 0 | 0 |
| 415 | unused hair back 7f | unused hair back 7f | unused hair back 7e | (0.421, 13.934, 0.874) | RM-C | 0 | unused hair back 7g |  |  |  |  | 0 | 0 |
| 416 | unused hair back 7g | unused hair back 7g | unused hair back 7f | (0.418, 13.524, 0.871) | RM-C | 0 | unused hair back 7h |  |  |  |  | 0 | 0 |
| 417 | unused hair back 7h | unused hair back 7h | unused hair back 7g | (0.416, 13.115, 0.869) | RM-C | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 418 | unused hair left back 4a | unused hair left back 4a | unused head neck upper attached-full head +4 head neck upper | (0.697, 15.979, 0.640) | RM-C | 0 | unused hair left back 4b |  |  |  |  | 0 | 0 |
| 419 | unused hair left back 4b | unused hair left back 4b | unused hair left back 4a | (0.694, 15.570, 0.638) | RM-C | 0 | unused hair left back 4c |  |  |  |  | 0 | 0 |
| 420 | unused hair left back 4c | unused hair left back 4c | unused hair left back 4b | (0.691, 15.161, 0.635) | RM-C | 0 | unused hair left back 4d |  |  |  |  | 0 | 0 |
| 421 | unused hair left back 4d | unused hair left back 4d | unused hair left back 4c | (0.688, 14.751, 0.633) | RM-C | 0 | unused hair left back 4e |  |  |  |  | 0 | 0 |
| 422 | unused hair left back 4e | unused hair left back 4e | unused hair left back 4d | (0.685, 14.342, 0.630) | RM-C | 0 | unused hair left back 4f |  |  |  |  | 0 | 0 |
| 423 | unused hair left back 4f | unused hair left back 4f | unused hair left back 4e | (0.682, 13.933, 0.628) | RM-C | 0 | unused hair left back 4g |  |  |  |  | 0 | 0 |
| 424 | unused hair left back 4g | unused hair left back 4g | unused hair left back 4f | (0.678, 13.524, 0.625) | RM-C | 0 | unused hair left back 4h |  |  |  |  | 0 | 0 |
| 425 | unused hair left back 4h | unused hair left back 4h | unused hair left back 4g | (0.675, 13.115, 0.623) | RM-C | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 426 | unused hair back 1a | unused hair back 1a | unused head neck upper attached-full head +4 head neck upper | (-0.420, 15.986, 0.889) | RM-C | 0 | unused hair back 1b |  |  |  |  | 0 | 0 |
| 427 | unused hair back 1b | unused hair back 1b | unused hair back 1a | (-0.421, 15.577, 0.888) | RM-C | 0 | unused hair back 1c |  |  |  |  | 0 | 0 |
| 428 | unused hair back 1c | unused hair back 1c | unused hair back 1b | (-0.423, 15.168, 0.886) | RM-C | 0 | unused hair back 1d |  |  |  |  | 0 | 0 |
| 429 | unused hair back 1d | unused hair back 1d | unused hair back 1c | (-0.424, 14.759, 0.884) | RM-C | 0 | unused hair back 1e |  |  |  |  | 0 | 0 |
| 430 | unused hair back 1e | unused hair back 1e | unused hair back 1d | (-0.426, 14.350, 0.883) | RM-C | 0 | unused hair back 1f |  |  |  |  | 0 | 0 |
| 431 | unused hair back 1f | unused hair back 1f | unused hair back 1e | (-0.427, 13.940, 0.881) | RM-C | 0 | unused hair back 1g |  |  |  |  | 0 | 0 |
| 432 | unused hair back 1g | unused hair back 1g | unused hair back 1f | (-0.428, 13.531, 0.880) | RM-C | 0 | unused hair back 1h |  |  |  |  | 0 | 0 |
| 433 | unused hair back 1h | unused hair back 1h | unused hair back 1g | (-0.430, 13.122, 0.878) | RM-C | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 434 | unused hair right back 5a | unused hair right back 5a | unused head neck upper attached-full head +4 head neck upper | (-0.684, 15.990, 0.640) | RM-C | 0 | unused hair right back 5b |  |  |  |  | 0 | 0 |
| 435 | unused hair right back 5b | unused hair right back 5b | unused hair right back 5a | (-0.686, 15.581, 0.639) | RM-C | 0 | unused hair right back 5c |  |  |  |  | 0 | 0 |
| 436 | unused hair right back 5c | unused hair right back 5c | unused hair right back 5b | (-0.688, 15.172, 0.638) | RM-C | 0 | unused hair right back 5d |  |  |  |  | 0 | 0 |
| 437 | unused hair right back 5d | unused hair right back 5d | unused hair right back 5c | (-0.690, 14.762, 0.637) | RM-C | 0 | unused hair right back 5e |  |  |  |  | 0 | 0 |
| 438 | unused hair right back 5e | unused hair right back 5e | unused hair right back 5d | (-0.692, 14.353, 0.636) | RM-C | 0 | unused hair right back 5f |  |  |  |  | 0 | 0 |
| 439 | unused hair right back 5f | unused hair right back 5f | unused hair right back 5e | (-0.694, 13.944, 0.635) | RM-C | 0 | unused hair right back 5g |  |  |  |  | 0 | 0 |
| 440 | unused hair right back 5g | unused hair right back 5g | unused hair right back 5f | (-0.696, 13.535, 0.634) | RM-C | 0 | unused hair right back 5h |  |  |  |  | 0 | 0 |
| 441 | unused hair right back 5h | unused hair right back 5h | unused hair right back 5g | (-0.698, 13.126, 0.633) | RM-C | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 442 | unused hair back 6a | unused hair back 6a | unused head neck upper attached-full head +4 head neck upper | (0.348, 16.137, 1.059) | RM-C | 0 | unused hair back 6b |  |  |  |  | 0 | 0 |
| 443 | unused hair back 6b | unused hair back 6b | unused hair back 6a | (0.345, 15.674, 1.056) | RM-C | 0 | unused hair back 6c |  |  |  |  | 0 | 0 |
| 444 | unused hair back 6c | unused hair back 6c | unused hair back 6b | (0.343, 15.211, 1.053) | RM-C | 0 | unused hair back 6d |  |  |  |  | 0 | 0 |
| 445 | unused hair back 6d | unused hair back 6d | unused hair back 6c | (0.340, 14.748, 1.049) | RM-C | 0 | unused hair back 6e |  |  |  |  | 0 | 0 |
| 446 | unused hair back 6e | unused hair back 6e | unused hair back 6d | (0.338, 14.285, 1.046) | RM-C | 0 | unused hair back 6f |  |  |  |  | 0 | 0 |
| 447 | unused hair back 6f | unused hair back 6f | unused hair back 6e | (0.335, 13.821, 1.043) | RM-C | 0 | unused hair back 6g |  |  |  |  | 0 | 0 |
| 448 | unused hair back 6g | unused hair back 6g | unused hair back 6f | (0.333, 13.358, 1.039) | RM-C | 0 | unused hair back 6h |  |  |  |  | 0 | 0 |
| 449 | unused hair back 6h | unused hair back 6h | unused hair back 6g | (0.330, 12.895, 1.036) | RM-C | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 450 | unused hair left back 5a | unused hair left back 5a | unused head neck upper attached-full head +4 head neck upper | (0.751, 16.098, 0.477) | RM-C | 0 | unused hair left back 5b |  |  |  |  | 0 | 0 |
| 451 | unused hair left back 5b | unused hair left back 5b | unused hair left back 5a | (0.748, 15.634, 0.475) | RM-C | 0 | unused hair left back 5c |  |  |  |  | 0 | 0 |
| 452 | unused hair left back 5c | unused hair left back 5c | unused hair left back 5b | (0.744, 15.171, 0.473) | RM-C | 0 | unused hair left back 5d |  |  |  |  | 0 | 0 |
| 453 | unused hair left back 5d | unused hair left back 5d | unused hair left back 5c | (0.740, 14.708, 0.470) | RM-C | 0 | unused hair left back 5e |  |  |  |  | 0 | 0 |
| 454 | unused hair left back 5e | unused hair left back 5e | unused hair left back 5d | (0.736, 14.245, 0.468) | RM-C | 0 | unused hair left back 5f |  |  |  |  | 0 | 0 |
| 455 | unused hair left back 5f | unused hair left back 5f | unused hair left back 5e | (0.733, 13.782, 0.465) | RM-C | 0 | unused hair left back 5g |  |  |  |  | 0 | 0 |
| 456 | unused hair left back 5g | unused hair left back 5g | unused hair left back 5f | (0.729, 13.319, 0.463) | RM-C | 0 | unused hair left back 5h |  |  |  |  | 0 | 0 |
| 457 | unused hair left back 5h | unused hair left back 5h | unused hair left back 5g | (0.725, 12.856, 0.460) | RM-C | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 458 | unused hair left back 1a | unused hair left back 1a | unused head neck upper attached-full head +4 head neck upper | (0.772, 15.475, 0.282) | RM-C | 0 | unused hair left back 1b |  |  |  |  | 0 | 0 |
| 459 | unused hair left back 1b | unused hair left back 1b | unused hair left back 1a | (0.768, 15.023, 0.281) | RM-C | 0 | unused hair left back 1c |  |  |  |  | 0 | 0 |
| 460 | unused hair left back 1c | unused hair left back 1c | unused hair left back 1b | (0.765, 14.571, 0.280) | RM-C | 0 | unused hair left back 1d |  |  |  |  | 0 | 0 |
| 461 | unused hair left back 1d | unused hair left back 1d | unused hair left back 1c | (0.761, 14.120, 0.278) | RM-C | 0 | unused hair left back 1e |  |  |  |  | 0 | 0 |
| 462 | unused hair left back 1e | unused hair left back 1e | unused hair left back 1d | (0.757, 13.668, 0.277) | RM-C | 0 | unused hair left back 1f |  |  |  |  | 0 | 0 |
| 463 | unused hair left back 1f | unused hair left back 1f | unused hair left back 1e | (0.753, 13.216, 0.276) | RM-C | 0 | unused hair left back 1g |  |  |  |  | 0 | 0 |
| 464 | unused hair left back 1g | unused hair left back 1g | unused hair left back 1f | (0.750, 12.765, 0.275) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 465 | unused hair back 2a | unused hair back 2a | unused head neck upper attached-full head +4 head neck upper | (-0.332, 16.143, 1.059) | RM-C | 0 | unused hair back 2b |  |  |  |  | 0 | 0 |
| 466 | unused hair back 2b | unused hair back 2b | unused hair back 2a | (-0.334, 15.679, 1.057) | RM-C | 0 | unused hair back 2c |  |  |  |  | 0 | 0 |
| 467 | unused hair back 2c | unused hair back 2c | unused hair back 2b | (-0.335, 15.216, 1.055) | RM-C | 0 | unused hair back 2d |  |  |  |  | 0 | 0 |
| 468 | unused hair back 2d | unused hair back 2d | unused hair back 2c | (-0.337, 14.753, 1.053) | RM-C | 0 | unused hair back 2e |  |  |  |  | 0 | 0 |
| 469 | unused hair back 2e | unused hair back 2e | unused hair back 2d | (-0.338, 14.290, 1.051) | RM-C | 0 | unused hair back 2f |  |  |  |  | 0 | 0 |
| 470 | unused hair back 2f | unused hair back 2f | unused hair back 2e | (-0.340, 13.827, 1.048) | RM-C | 0 | unused hair back 2g |  |  |  |  | 0 | 0 |
| 471 | unused hair back 2g | unused hair back 2g | unused hair back 2f | (-0.342, 13.364, 1.046) | RM-C | 0 | unused hair back 2h |  |  |  |  | 0 | 0 |
| 472 | unused hair back 2h | unused hair back 2h | unused hair back 2g | (-0.343, 12.901, 1.044) | RM-C | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 473 | unused hair right back 6a | unused hair right back 6a | unused head neck upper attached-full head +4 head neck upper | (-0.775, 16.108, 0.695) | RM-C | 0 | unused hair right back 6b |  |  |  |  | 0 | 0 |
| 474 | unused hair right back 6b | unused hair right back 6b | unused hair right back 6a | (-0.777, 15.645, 0.694) | RM-C | 0 | unused hair right back 6c |  |  |  |  | 0 | 0 |
| 475 | unused hair right back 6c | unused hair right back 6c | unused hair right back 6b | (-0.780, 15.182, 0.692) | RM-C | 0 | unused hair right back 6d |  |  |  |  | 0 | 0 |
| 476 | unused hair right back 6d | unused hair right back 6d | unused hair right back 6c | (-0.782, 14.719, 0.691) | RM-C | 0 | unused hair right back 6e |  |  |  |  | 0 | 0 |
| 477 | unused hair right back 6e | unused hair right back 6e | unused hair right back 6d | (-0.784, 14.256, 0.690) | RM-C | 0 | unused hair right back 6f |  |  |  |  | 0 | 0 |
| 478 | unused hair right back 6f | unused hair right back 6f | unused hair right back 6e | (-0.786, 13.793, 0.689) | RM-C | 0 | unused hair right back 6g |  |  |  |  | 0 | 0 |
| 479 | unused hair right back 6g | unused hair right back 6g | unused hair right back 6f | (-0.789, 13.330, 0.688) | RM-C | 0 | unused hair right back 6h |  |  |  |  | 0 | 0 |
| 480 | unused hair right back 6h | unused hair right back 6h | unused hair right back 6g | (-0.791, 12.866, 0.687) | RM-C | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 481 | unused hair right back 2a | unused hair right back 2a | unused head neck upper attached-full head +4 head neck upper | (-0.817, 15.487, 0.356) | RM-C | 0 | unused hair right back 2b |  |  |  |  | 0 | 0 |
| 482 | unused hair right back 2b | unused hair right back 2b | unused hair right back 2a | (-0.819, 15.035, 0.356) | RM-C | 0 | unused hair right back 2c |  |  |  |  | 0 | 0 |
| 483 | unused hair right back 2c | unused hair right back 2c | unused hair right back 2b | (-0.822, 14.584, 0.356) | RM-C | 0 | unused hair right back 2d |  |  |  |  | 0 | 0 |
| 484 | unused hair right back 2d | unused hair right back 2d | unused hair right back 2c | (-0.825, 14.132, 0.356) | RM-C | 0 | unused hair right back 2e |  |  |  |  | 0 | 0 |
| 485 | unused hair right back 2e | unused hair right back 2e | unused hair right back 2d | (-0.827, 13.680, 0.356) | RM-C | 0 | unused hair right back 2f |  |  |  |  | 0 | 0 |
| 486 | unused hair right back 2f | unused hair right back 2f | unused hair right back 2e | (-0.830, 13.228, 0.356) | RM-C | 0 | unused hair right back 2g |  |  |  |  | 0 | 0 |
| 487 | unused hair right back 2g | unused hair right back 2g | unused hair right back 2f | (-0.832, 12.777, 0.356) | RM-C | 0 | (-0.00, -0.45, 0.00) |  |  |  |  | 0 | 0 |
| 488 | unused hair right back 1a | unused hair right back 1a | unused head neck upper attached-full head +4 head neck upper | (-0.767, 15.487, 0.282) | RM-C | 0 | unused hair right back 1b |  |  |  |  | 0 | 0 |
| 489 | unused hair right back 1b | unused hair right back 1b | unused hair right back 1a | (-0.769, 15.035, 0.282) | RM-C | 0 | unused hair right back 1c |  |  |  |  | 0 | 0 |
| 490 | unused hair right back 1c | unused hair right back 1c | unused hair right back 1b | (-0.772, 14.584, 0.282) | RM-C | 0 | unused hair right back 1d |  |  |  |  | 0 | 0 |
| 491 | unused hair right back 1d | unused hair right back 1d | unused hair right back 1c | (-0.775, 14.132, 0.282) | RM-C | 0 | unused hair right back 1e |  |  |  |  | 0 | 0 |
| 492 | unused hair right back 1e | unused hair right back 1e | unused hair right back 1d | (-0.778, 13.680, 0.282) | RM-C | 0 | unused hair right back 1f |  |  |  |  | 0 | 0 |
| 493 | unused hair right back 1f | unused hair right back 1f | unused hair right back 1e | (-0.781, 13.229, 0.282) | RM-C | 0 | unused hair right back 1g |  |  |  |  | 0 | 0 |
| 494 | unused hair right back 1g | unused hair right back 1g | unused hair right back 1f | (-0.784, 12.777, 0.282) | RM-C | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 495 | unused hair left back 6a | unused hair left back 6a | unused head neck upper attached-full head +4 head neck upper | (0.774, 16.096, 0.725) | RM-C | 0 | unused hair left back 6b |  |  |  |  | 0 | 0 |
| 496 | unused hair left back 6b | unused hair left back 6b | unused hair left back 6a | (0.770, 15.633, 0.723) | RM-C | 0 | unused hair left back 6c |  |  |  |  | 0 | 0 |
| 497 | unused hair left back 6c | unused hair left back 6c | unused hair left back 6b | (0.766, 15.170, 0.720) | RM-C | 0 | unused hair left back 6d |  |  |  |  | 0 | 0 |
| 498 | unused hair left back 6d | unused hair left back 6d | unused hair left back 6c | (0.763, 14.707, 0.717) | RM-C | 0 | unused hair left back 6e |  |  |  |  | 0 | 0 |
| 499 | unused hair left back 6e | unused hair left back 6e | unused hair left back 6d | (0.759, 14.244, 0.714) | RM-C | 0 | unused hair left back 6f |  |  |  |  | 0 | 0 |
| 500 | unused hair left back 6f | unused hair left back 6f | unused hair left back 6e | (0.756, 13.780, 0.711) | RM-C | 0 | unused hair left back 6g |  |  |  |  | 0 | 0 |
| 501 | unused hair left back 6g | unused hair left back 6g | unused hair left back 6f | (0.752, 13.317, 0.709) | RM-C | 0 | unused hair left back 6h |  |  |  |  | 0 | 0 |
| 502 | unused hair left back 6h | unused hair left back 6h | unused hair left back 6g | (0.748, 12.854, 0.706) | RM-C | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 503 | unusedopt-dummy-head item-honoka hair +3 item-full head +4 | unusedopt-dummy-head item-honoka hair +3 item-full head +4 | unused head neck upper attached-full head +4 head neck upper | (-0.000, 14.689, 0.097) | RM-C | 0 | (-0.00, -0.16, -0.05) |  |  |  |  | 0 | 0 |
| 504 | unused head neck upper attached-new naotora face +2 head neck l item-full head | unused head neck upper attached-new naotora face +2 head neck l item-full head | 頭 | (0.000, 14.156, 0.280) | RM-C | 0 | unused head neck upper attached-full head neck upper |  |  |  |  | 0 | 0 |
| 505 | unused head neck upper attached-full head neck upper | unused head neck upper attached-full head neck upper | unused head neck upper attached-new naotora face +2 head neck l item-full head | (0.000, 14.856, 0.149) | RM-C | 0 | (0.00, 0.69, -0.36) |  |  |  |  | 0 | 0 |
| 506 | head tongue a | head tongue a | head jaw | (0.000, 14.923, -0.162) | RMVC | 0 | head tongue b |  |  |  |  | 0 | 0 |
| 507 | head tongue b | head tongue b | head tongue a | (0.000, 14.952, -0.476) | RMVC | 0 | (0.00, 0.03, -0.31) |  |  |  |  | 0 | 0 |
| 508 | head cheek left a | head cheek left a | unused head neck upper attached-full head neck upper | (0.281, 15.317, -0.659) | RMVC | 0 | (0.28, 0.46, -0.81) |  |  |  |  | 0 | 0 |
| 509 | head cheek left b | head cheek left b | unused head neck upper attached-full head neck upper | (0.452, 15.366, -0.568) | RMVC | 0 | (0.45, 0.51, -0.72) |  |  |  |  | 0 | 0 |
| 510 | head cheek left c | head cheek left c | unused head neck upper attached-full head neck upper | (0.503, 15.060, -0.388) | RMVC | 0 | (0.50, 0.20, -0.54) |  |  |  |  | 0 | 0 |
| 511 | head eyelid lower left a | head eyelid lower left a | unused head neck upper attached-full head neck upper | (0.221, 15.465, -0.625) | RMVC | 0 | (0.22, 0.61, -0.77) |  |  |  |  | 0 | 0 |
| 512 | head eyelid lower left b | head eyelid lower left b | unused head neck upper attached-full head neck upper | (0.310, 15.448, -0.634) | RMVC | 0 | (0.31, 0.59, -0.78) |  |  |  |  | 0 | 0 |
| 513 | head eyebrow left a | head eyebrow left a | unused head neck upper attached-full head neck upper | (0.142, 15.639, -0.771) | RMVC | 0 | (0.14, 0.78, -0.92) |  |  |  |  | 0 | 0 |
| 514 | head eyebrow left b | head eyebrow left b | unused head neck upper attached-full head neck upper | (0.323, 15.689, -0.723) | RMVC | 0 | (0.32, 0.83, -0.87) |  |  |  |  | 0 | 0 |
| 515 | head eyebrow left c | head eyebrow left c | unused head neck upper attached-full head neck upper | (0.459, 15.677, -0.592) | RMVC | 0 | (0.46, 0.82, -0.74) |  |  |  |  | 0 | 0 |
| 516 | head eyelid upper left | head eyelid upper left | unused head neck upper attached-full head neck upper | (0.284, 15.512, -0.506) | RMVC | 0 | (0.28, 0.66, -0.65) |  |  |  |  | 0 | 0 |
| 517 | head nose left a | head nose left a | unused head neck upper attached-full head neck upper | (0.124, 15.372, -0.700) | RMVC | 0 | (0.12, 0.52, -0.85) |  |  |  |  | 0 | 0 |
| 518 | head nose left b | head nose left b | unused head neck upper attached-full head neck upper | (0.146, 15.145, -0.719) | RMVC | 0 | (0.15, 0.29, -0.87) |  |  |  |  | 0 | 0 |
| 519 | head nose left c | head nose left c | unused head neck upper attached-full head neck upper | (0.213, 15.091, -0.676) | RMVC | 0 | (0.21, 0.23, -0.82) |  |  |  |  | 0 | 0 |
| 520 | head nose left d | head nose left d | unused head neck upper attached-full head neck upper | (0.289, 14.974, -0.617) | RMVC | 0 | (0.29, 0.12, -0.77) |  |  |  |  | 0 | 0 |
| 521 | head cheek right a | head cheek right a | unused head neck upper attached-full head neck upper | (-0.281, 15.317, -0.659) | RMVC | 0 | (-0.28, 0.46, -0.81) |  |  |  |  | 0 | 0 |
| 522 | head cheek right b | head cheek right b | unused head neck upper attached-full head neck upper | (-0.452, 15.366, -0.568) | RMVC | 0 | (-0.45, 0.51, -0.72) |  |  |  |  | 0 | 0 |
| 523 | head cheek right c | head cheek right c | unused head neck upper attached-full head neck upper | (-0.503, 15.060, -0.388) | RMVC | 0 | (-0.50, 0.20, -0.54) |  |  |  |  | 0 | 0 |
| 524 | head eyelid lower right a | head eyelid lower right a | unused head neck upper attached-full head neck upper | (-0.221, 15.465, -0.625) | RMVC | 0 | (-0.22, 0.61, -0.77) |  |  |  |  | 0 | 0 |
| 525 | head eyelid lower right b | head eyelid lower right b | unused head neck upper attached-full head neck upper | (-0.310, 15.448, -0.634) | RMVC | 0 | (-0.31, 0.59, -0.78) |  |  |  |  | 0 | 0 |
| 526 | head eyebrow right a | head eyebrow right a | unused head neck upper attached-full head neck upper | (-0.142, 15.639, -0.771) | RMVC | 0 | (-0.14, 0.78, -0.92) |  |  |  |  | 0 | 0 |
| 527 | head eyebrow right b | head eyebrow right b | unused head neck upper attached-full head neck upper | (-0.323, 15.689, -0.723) | RMVC | 0 | (-0.32, 0.83, -0.87) |  |  |  |  | 0 | 0 |
| 528 | head eyebrow right c | head eyebrow right c | unused head neck upper attached-full head neck upper | (-0.459, 15.677, -0.592) | RMVC | 0 | (-0.46, 0.82, -0.74) |  |  |  |  | 0 | 0 |
| 529 | head eyelid upper right | head eyelid upper right | unused head neck upper attached-full head neck upper | (-0.285, 15.512, -0.506) | RMVC | 0 | (-0.28, 0.66, -0.65) |  |  |  |  | 0 | 0 |
| 530 | head nose right a | head nose right a | unused head neck upper attached-full head neck upper | (-0.124, 15.372, -0.700) | RMVC | 0 | (-0.12, 0.52, -0.85) |  |  |  |  | 0 | 0 |
| 531 | head nose right b | head nose right b | unused head neck upper attached-full head neck upper | (-0.146, 15.145, -0.719) | RMVC | 0 | (-0.15, 0.29, -0.87) |  |  |  |  | 0 | 0 |
| 532 | head nose right c | head nose right c | unused head neck upper attached-full head neck upper | (-0.213, 15.091, -0.676) | RMVC | 0 | (-0.21, 0.23, -0.82) |  |  |  |  | 0 | 0 |
| 533 | head nose right d | head nose right d | unused head neck upper attached-full head neck upper | (-0.289, 14.974, -0.617) | RMVC | 0 | (-0.29, 0.12, -0.77) |  |  |  |  | 0 | 0 |
| 534 | hair middle front a | hair middle front a | unused head neck upper attached-full head neck upper | (0.012, 16.607, -0.451) | RMVC | 0 | hair middle front b |  |  |  |  | 0 | 0 |
| 535 | hair middle front b | hair middle front b | hair middle front a | (0.029, 16.446, -0.682) | RMVC | 0 | hair middle front c |  |  |  |  | 0 | 0 |
| 536 | hair middle front c | hair middle front c | hair middle front b | (0.033, 16.180, -0.813) | RMVC | 0 | hair middle front d |  |  |  |  | 0 | 0 |
| 537 | hair middle front d | hair middle front d | hair middle front c | (0.004, 15.853, -0.854) | RMVC | 0 | hair middle front e |  |  |  |  | 0 | 0 |
| 538 | hair middle front e | hair middle front e | hair middle front d | (-0.056, 15.500, -0.854) | RMVC | 0 | (-0.06, -0.35, -0.00) |  |  |  |  | 0 | 0 |
| 539 | hair left front a | hair left front a | unused head neck upper attached-full head neck upper | (0.086, 16.546, -0.515) | RMVC | 0 | hair left front b |  |  |  |  | 0 | 0 |
| 540 | hair left front b | hair left front b | hair left front a | (0.352, 16.359, -0.613) | RMVC | 0 | hair left front c |  |  |  |  | 0 | 0 |
| 541 | hair left front c | hair left front c | hair left front b | (0.508, 15.998, -0.641) | RMVC | 0 | hair left front d |  |  |  |  | 0 | 0 |
| 542 | hair left front d | hair left front d | hair left front c | (0.563, 15.614, -0.613) | RMVC | 0 | hair left front e |  |  |  |  | 0 | 0 |
| 543 | hair left front e | hair left front e | hair left front d | (0.569, 15.177, -0.559) | RMVC | 0 | (0.01, -0.44, 0.05) |  |  |  |  | 0 | 0 |
| 544 | hair right front a | hair right front a | unused head neck upper attached-full head neck upper | (-0.086, 16.546, -0.515) | RMVC | 0 | hair right front b |  |  |  |  | 0 | 0 |
| 545 | hair right front b | hair right front b | hair right front a | (-0.352, 16.359, -0.613) | RMVC | 0 | hair right front c |  |  |  |  | 0 | 0 |
| 546 | hair right front c | hair right front c | hair right front b | (-0.508, 15.999, -0.641) | RMVC | 0 | hair right front d |  |  |  |  | 0 | 0 |
| 547 | hair right front d | hair right front d | hair right front c | (-0.563, 15.614, -0.613) | RMVC | 0 | hair right front e |  |  |  |  | 0 | 0 |
| 548 | hair right front e | hair right front e | hair right front d | (-0.569, 15.177, -0.559) | RMVC | 0 | (-0.01, -0.44, 0.05) |  |  |  |  | 0 | 0 |
| 549 | hair left front 2a | hair left front 2a | unused head neck upper attached-full head neck upper | (0.652, 16.094, -0.283) | RMVC | 0 | hair left front 2b |  |  |  |  | 0 | 0 |
| 550 | hair left front 2b | hair left front 2b | hair left front 2a | (0.652, 15.689, -0.283) | RMVC | 0 | hair left front 2c |  |  |  |  | 0 | 0 |
| 551 | hair left front 2c | hair left front 2c | hair left front 2b | (0.652, 15.285, -0.283) | RMVC | 0 | hair left front 2d |  |  |  |  | 0 | 0 |
| 552 | hair left front 2d | hair left front 2d | hair left front 2c | (0.652, 14.880, -0.283) | RMVC | 0 | hair left front 2e |  |  |  |  | 0 | 0 |
| 553 | hair left front 2e | hair left front 2e | hair left front 2d | (0.652, 14.475, -0.283) | RMVC | 0 | hair left front 2f |  |  |  |  | 0 | 0 |
| 554 | hair left front 2f | hair left front 2f | hair left front 2e | (0.652, 14.071, -0.283) | RMVC | 0 | hair left front 2g |  |  |  |  | 0 | 0 |
| 555 | hair left front 2g | hair left front 2g | hair left front 2f | (0.652, 13.666, -0.283) | RMVC | 0 | (0.00, -0.40, 0.00) |  |  |  |  | 0 | 0 |
| 556 | hair right front 2a | hair right front 2a | unused head neck upper attached-full head neck upper | (-0.652, 16.094, -0.283) | RMVC | 0 | hair right front 2b |  |  |  |  | 0 | 0 |
| 557 | hair right front 2b | hair right front 2b | hair right front 2a | (-0.652, 15.689, -0.283) | RMVC | 0 | hair right front 2c |  |  |  |  | 0 | 0 |
| 558 | hair right front 2c | hair right front 2c | hair right front 2b | (-0.652, 15.285, -0.283) | RMVC | 0 | hair right front 2d |  |  |  |  | 0 | 0 |
| 559 | hair right front 2d | hair right front 2d | hair right front 2c | (-0.652, 14.880, -0.283) | RMVC | 0 | hair right front 2e |  |  |  |  | 0 | 0 |
| 560 | hair right front 2e | hair right front 2e | hair right front 2d | (-0.652, 14.475, -0.283) | RMVC | 0 | hair right front 2f |  |  |  |  | 0 | 0 |
| 561 | hair right front 2f | hair right front 2f | hair right front 2e | (-0.652, 14.071, -0.283) | RMVC | 0 | hair right front 2g |  |  |  |  | 0 | 0 |
| 562 | hair right front 2g | hair right front 2g | hair right front 2f | (-0.652, 13.666, -0.283) | RMVC | 0 | (-0.00, -0.40, 0.00) |  |  |  |  | 0 | 0 |
| 563 | hair back 5a | hair back 5a | unused head neck upper attached-full head neck upper | (0.248, 15.671, 0.906) | RMVC | 0 | hair back 5b |  |  |  |  | 0 | 0 |
| 564 | hair back 5b | hair back 5b | hair back 5a | (0.246, 15.220, 0.903) | RMVC | 0 | hair back 5c |  |  |  |  | 0 | 0 |
| 565 | hair back 5c | hair back 5c | hair back 5b | (0.244, 14.768, 0.899) | RMVC | 0 | hair back 5d |  |  |  |  | 0 | 0 |
| 566 | hair back 5d | hair back 5d | hair back 5c | (0.243, 14.316, 0.896) | RMVC | 0 | hair back 5e |  |  |  |  | 0 | 0 |
| 567 | hair back 5e | hair back 5e | hair back 5d | (0.241, 13.865, 0.893) | RMVC | 0 | hair back 5f |  |  |  |  | 0 | 0 |
| 568 | hair back 5f | hair back 5f | hair back 5e | (0.239, 13.413, 0.890) | RMVC | 0 | hair back 5g |  |  |  |  | 0 | 0 |
| 569 | hair back 5g | hair back 5g | hair back 5f | (0.237, 12.961, 0.886) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 570 | hair left back 3a | hair left back 3a | unused head neck upper attached-full head neck upper | (0.616, 15.670, 0.617) | RMVC | 0 | hair left back 3b |  |  |  |  | 0 | 0 |
| 571 | hair left back 3b | hair left back 3b | hair left back 3a | (0.612, 15.219, 0.614) | RMVC | 0 | hair left back 3c |  |  |  |  | 0 | 0 |
| 572 | hair left back 3c | hair left back 3c | hair left back 3b | (0.609, 14.767, 0.612) | RMVC | 0 | hair left back 3d |  |  |  |  | 0 | 0 |
| 573 | hair left back 3d | hair left back 3d | hair left back 3c | (0.605, 14.315, 0.609) | RMVC | 0 | hair left back 3e |  |  |  |  | 0 | 0 |
| 574 | hair left back 3e | hair left back 3e | hair left back 3d | (0.602, 13.863, 0.606) | RMVC | 0 | hair left back 3f |  |  |  |  | 0 | 0 |
| 575 | hair left back 3f | hair left back 3f | hair left back 3e | (0.598, 13.412, 0.603) | RMVC | 0 | hair left back 3g |  |  |  |  | 0 | 0 |
| 576 | hair left back 3g | hair left back 3g | hair left back 3f | (0.595, 12.960, 0.601) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 577 | hair left back 2a | hair left back 2a | unused head neck upper attached-full head neck upper | (0.726, 15.671, 0.427) | RMVC | 0 | hair left back 2b |  |  |  |  | 0 | 0 |
| 578 | hair left back 2b | hair left back 2b | hair left back 2a | (0.722, 15.219, 0.425) | RMVC | 0 | hair left back 2c |  |  |  |  | 0 | 0 |
| 579 | hair left back 2c | hair left back 2c | hair left back 2b | (0.718, 14.767, 0.423) | RMVC | 0 | hair left back 2d |  |  |  |  | 0 | 0 |
| 580 | hair left back 2d | hair left back 2d | hair left back 2c | (0.715, 14.315, 0.421) | RMVC | 0 | hair left back 2e |  |  |  |  | 0 | 0 |
| 581 | hair left back 2e | hair left back 2e | hair left back 2d | (0.711, 13.864, 0.419) | RMVC | 0 | hair left back 2f |  |  |  |  | 0 | 0 |
| 582 | hair left back 2f | hair left back 2f | hair left back 2e | (0.707, 13.412, 0.417) | RMVC | 0 | hair left back 2g |  |  |  |  | 0 | 0 |
| 583 | hair left back 2g | hair left back 2g | hair left back 2f | (0.703, 12.960, 0.415) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 584 | hair back 3a | hair back 3a | unused head neck upper attached-full head neck upper | (-0.239, 15.675, 0.906) | RMVC | 0 | hair back 3b |  |  |  |  | 0 | 0 |
| 585 | hair back 3b | hair back 3b | hair back 3a | (-0.240, 15.224, 0.904) | RMVC | 0 | hair back 3c |  |  |  |  | 0 | 0 |
| 586 | hair back 3c | hair back 3c | hair back 3b | (-0.241, 14.772, 0.902) | RMVC | 0 | hair back 3d |  |  |  |  | 0 | 0 |
| 587 | hair back 3d | hair back 3d | hair back 3c | (-0.242, 14.320, 0.900) | RMVC | 0 | hair back 3e |  |  |  |  | 0 | 0 |
| 588 | hair back 3e | hair back 3e | hair back 3d | (-0.243, 13.868, 0.898) | RMVC | 0 | hair back 3f |  |  |  |  | 0 | 0 |
| 589 | hair back 3f | hair back 3f | hair back 3e | (-0.243, 13.417, 0.896) | RMVC | 0 | hair back 3g |  |  |  |  | 0 | 0 |
| 590 | hair back 3g | hair back 3g | hair back 3f | (-0.244, 12.965, 0.895) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 591 | hair right back 4a | hair right back 4a | unused head neck upper attached-full head neck upper | (-0.607, 15.680, 0.618) | RMVC | 0 | hair right back 4b |  |  |  |  | 0 | 0 |
| 592 | hair right back 4b | hair right back 4b | hair right back 4a | (-0.609, 15.228, 0.617) | RMVC | 0 | hair right back 4c |  |  |  |  | 0 | 0 |
| 593 | hair right back 4c | hair right back 4c | hair right back 4b | (-0.610, 14.777, 0.617) | RMVC | 0 | hair right back 4d |  |  |  |  | 0 | 0 |
| 594 | hair right back 4d | hair right back 4d | hair right back 4c | (-0.612, 14.325, 0.616) | RMVC | 0 | hair right back 4e |  |  |  |  | 0 | 0 |
| 595 | hair right back 4e | hair right back 4e | hair right back 4d | (-0.614, 13.873, 0.615) | RMVC | 0 | hair right back 4f |  |  |  |  | 0 | 0 |
| 596 | hair right back 4f | hair right back 4f | hair right back 4e | (-0.615, 13.421, 0.615) | RMVC | 0 | hair right back 4g |  |  |  |  | 0 | 0 |
| 597 | hair right back 4g | hair right back 4g | hair right back 4f | (-0.617, 12.970, 0.614) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 598 | hair right back 3a | hair right back 3a | unused head neck upper attached-full head neck upper | (-0.717, 15.682, 0.428) | RMVC | 0 | hair right back 3b |  |  |  |  | 0 | 0 |
| 599 | hair right back 3b | hair right back 3b | hair right back 3a | (-0.720, 15.230, 0.427) | RMVC | 0 | hair right back 3c |  |  |  |  | 0 | 0 |
| 600 | hair right back 3c | hair right back 3c | hair right back 3b | (-0.722, 14.779, 0.427) | RMVC | 0 | hair right back 3d |  |  |  |  | 0 | 0 |
| 601 | hair right back 3d | hair right back 3d | hair right back 3c | (-0.725, 14.327, 0.427) | RMVC | 0 | hair right back 3e |  |  |  |  | 0 | 0 |
| 602 | hair right back 3e | hair right back 3e | hair right back 3d | (-0.727, 13.875, 0.426) | RMVC | 0 | hair right back 3f |  |  |  |  | 0 | 0 |
| 603 | hair right back 3f | hair right back 3f | hair right back 3e | (-0.730, 13.424, 0.426) | RMVC | 0 | hair right back 3g |  |  |  |  | 0 | 0 |
| 604 | hair right back 3g | hair right back 3g | hair right back 3f | (-0.732, 12.972, 0.425) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 605 | hair back 4a | hair back 4a | unused head neck upper attached-full head neck upper | (0.007, 15.992, 1.041) | RMVC | 0 | hair back 4b |  |  |  |  | 0 | 0 |
| 606 | hair back 4b | hair back 4b | hair back 4a | (0.005, 15.583, 1.039) | RMVC | 0 | hair back 4c |  |  |  |  | 0 | 0 |
| 607 | hair back 4c | hair back 4c | hair back 4b | (0.004, 15.174, 1.036) | RMVC | 0 | hair back 4d |  |  |  |  | 0 | 0 |
| 608 | hair back 4d | hair back 4d | hair back 4c | (0.002, 14.764, 1.034) | RMVC | 0 | hair back 4e |  |  |  |  | 0 | 0 |
| 609 | hair back 4e | hair back 4e | hair back 4d | (0.001, 14.355, 1.031) | RMVC | 0 | hair back 4f |  |  |  |  | 0 | 0 |
| 610 | hair back 4f | hair back 4f | hair back 4e | (-0.001, 13.946, 1.029) | RMVC | 0 | hair back 4g |  |  |  |  | 0 | 0 |
| 611 | hair back 4g | hair back 4g | hair back 4f | (-0.002, 13.537, 1.026) | RMVC | 0 | hair back 4h |  |  |  |  | 0 | 0 |
| 612 | hair back 4h | hair back 4h | hair back 4g | (-0.004, 13.128, 1.023) | RMVC | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 613 | hair back 7a | hair back 7a | unused head neck upper attached-full head neck upper | (0.434, 15.989, 0.889) | RMVC | 0 | hair back 7b |  |  |  |  | 0 | 0 |
| 614 | hair back 7b | hair back 7b | hair back 7a | (0.431, 15.580, 0.886) | RMVC | 0 | hair back 7c |  |  |  |  | 0 | 0 |
| 615 | hair back 7c | hair back 7c | hair back 7b | (0.429, 15.171, 0.883) | RMVC | 0 | hair back 7d |  |  |  |  | 0 | 0 |
| 616 | hair back 7d | hair back 7d | hair back 7c | (0.426, 14.762, 0.880) | RMVC | 0 | hair back 7e |  |  |  |  | 0 | 0 |
| 617 | hair back 7e | hair back 7e | hair back 7d | (0.423, 14.353, 0.877) | RMVC | 0 | hair back 7f |  |  |  |  | 0 | 0 |
| 618 | hair back 7f | hair back 7f | hair back 7e | (0.421, 13.944, 0.874) | RMVC | 0 | hair back 7g |  |  |  |  | 0 | 0 |
| 619 | hair back 7g | hair back 7g | hair back 7f | (0.418, 13.534, 0.871) | RMVC | 0 | hair back 7h |  |  |  |  | 0 | 0 |
| 620 | hair back 7h | hair back 7h | hair back 7g | (0.416, 13.125, 0.869) | RMVC | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 621 | hair left back 4a | hair left back 4a | unused head neck upper attached-full head neck upper | (0.697, 15.989, 0.640) | RMVC | 0 | hair left back 4b |  |  |  |  | 0 | 0 |
| 622 | hair left back 4b | hair left back 4b | hair left back 4a | (0.694, 15.580, 0.638) | RMVC | 0 | hair left back 4c |  |  |  |  | 0 | 0 |
| 623 | hair left back 4c | hair left back 4c | hair left back 4b | (0.691, 15.171, 0.635) | RMVC | 0 | hair left back 4d |  |  |  |  | 0 | 0 |
| 624 | hair left back 4d | hair left back 4d | hair left back 4c | (0.688, 14.761, 0.633) | RMVC | 0 | hair left back 4e |  |  |  |  | 0 | 0 |
| 625 | hair left back 4e | hair left back 4e | hair left back 4d | (0.685, 14.352, 0.630) | RMVC | 0 | hair left back 4f |  |  |  |  | 0 | 0 |
| 626 | hair left back 4f | hair left back 4f | hair left back 4e | (0.682, 13.943, 0.628) | RMVC | 0 | hair left back 4g |  |  |  |  | 0 | 0 |
| 627 | hair left back 4g | hair left back 4g | hair left back 4f | (0.678, 13.534, 0.625) | RMVC | 0 | hair left back 4h |  |  |  |  | 0 | 0 |
| 628 | hair left back 4h | hair left back 4h | hair left back 4g | (0.675, 13.125, 0.623) | RMVC | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 629 | hair back 1a | hair back 1a | unused head neck upper attached-full head neck upper | (-0.420, 15.996, 0.889) | RMVC | 0 | hair back 1b |  |  |  |  | 0 | 0 |
| 630 | hair back 1b | hair back 1b | hair back 1a | (-0.421, 15.587, 0.888) | RMVC | 0 | hair back 1c |  |  |  |  | 0 | 0 |
| 631 | hair back 1c | hair back 1c | hair back 1b | (-0.423, 15.178, 0.886) | RMVC | 0 | hair back 1d |  |  |  |  | 0 | 0 |
| 632 | hair back 1d | hair back 1d | hair back 1c | (-0.424, 14.769, 0.884) | RMVC | 0 | hair back 1e |  |  |  |  | 0 | 0 |
| 633 | hair back 1e | hair back 1e | hair back 1d | (-0.426, 14.360, 0.883) | RMVC | 0 | hair back 1f |  |  |  |  | 0 | 0 |
| 634 | hair back 1f | hair back 1f | hair back 1e | (-0.427, 13.950, 0.881) | RMVC | 0 | hair back 1g |  |  |  |  | 0 | 0 |
| 635 | hair back 1g | hair back 1g | hair back 1f | (-0.428, 13.541, 0.880) | RMVC | 0 | hair back 1h |  |  |  |  | 0 | 0 |
| 636 | hair back 1h | hair back 1h | hair back 1g | (-0.430, 13.132, 0.878) | RMVC | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 637 | hair right back 5a | hair right back 5a | unused head neck upper attached-full head neck upper | (-0.684, 16.000, 0.640) | RMVC | 0 | hair right back 5b |  |  |  |  | 0 | 0 |
| 638 | hair right back 5b | hair right back 5b | hair right back 5a | (-0.686, 15.591, 0.639) | RMVC | 0 | hair right back 5c |  |  |  |  | 0 | 0 |
| 639 | hair right back 5c | hair right back 5c | hair right back 5b | (-0.688, 15.182, 0.638) | RMVC | 0 | hair right back 5d |  |  |  |  | 0 | 0 |
| 640 | hair right back 5d | hair right back 5d | hair right back 5c | (-0.690, 14.772, 0.637) | RMVC | 0 | hair right back 5e |  |  |  |  | 0 | 0 |
| 641 | hair right back 5e | hair right back 5e | hair right back 5d | (-0.692, 14.363, 0.636) | RMVC | 0 | hair right back 5f |  |  |  |  | 0 | 0 |
| 642 | hair right back 5f | hair right back 5f | hair right back 5e | (-0.694, 13.954, 0.635) | RMVC | 0 | hair right back 5g |  |  |  |  | 0 | 0 |
| 643 | hair right back 5g | hair right back 5g | hair right back 5f | (-0.696, 13.545, 0.634) | RMVC | 0 | hair right back 5h |  |  |  |  | 0 | 0 |
| 644 | hair right back 5h | hair right back 5h | hair right back 5g | (-0.698, 13.136, 0.633) | RMVC | 0 | (-0.00, -0.41, -0.00) |  |  |  |  | 0 | 0 |
| 645 | hair back 6a | hair back 6a | unused head neck upper attached-full head neck upper | (0.348, 16.147, 1.059) | RMVC | 0 | hair back 6b |  |  |  |  | 0 | 0 |
| 646 | hair back 6b | hair back 6b | hair back 6a | (0.345, 15.684, 1.056) | RMVC | 0 | hair back 6c |  |  |  |  | 0 | 0 |
| 647 | hair back 6c | hair back 6c | hair back 6b | (0.343, 15.221, 1.053) | RMVC | 0 | hair back 6d |  |  |  |  | 0 | 0 |
| 648 | hair back 6d | hair back 6d | hair back 6c | (0.340, 14.758, 1.049) | RMVC | 0 | hair back 6e |  |  |  |  | 0 | 0 |
| 649 | hair back 6e | hair back 6e | hair back 6d | (0.338, 14.295, 1.046) | RMVC | 0 | hair back 6f |  |  |  |  | 0 | 0 |
| 650 | hair back 6f | hair back 6f | hair back 6e | (0.335, 13.831, 1.043) | RMVC | 0 | hair back 6g |  |  |  |  | 0 | 0 |
| 651 | hair back 6g | hair back 6g | hair back 6f | (0.333, 13.368, 1.039) | RMVC | 0 | hair back 6h |  |  |  |  | 0 | 0 |
| 652 | hair back 6h | hair back 6h | hair back 6g | (0.330, 12.905, 1.036) | RMVC | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 653 | hair left back 5a | hair left back 5a | unused head neck upper attached-full head neck upper | (0.751, 16.108, 0.477) | RMVC | 0 | hair left back 5b |  |  |  |  | 0 | 0 |
| 654 | hair left back 5b | hair left back 5b | hair left back 5a | (0.748, 15.644, 0.475) | RMVC | 0 | hair left back 5c |  |  |  |  | 0 | 0 |
| 655 | hair left back 5c | hair left back 5c | hair left back 5b | (0.744, 15.181, 0.473) | RMVC | 0 | hair left back 5d |  |  |  |  | 0 | 0 |
| 656 | hair left back 5d | hair left back 5d | hair left back 5c | (0.740, 14.718, 0.470) | RMVC | 0 | hair left back 5e |  |  |  |  | 0 | 0 |
| 657 | hair left back 5e | hair left back 5e | hair left back 5d | (0.736, 14.255, 0.468) | RMVC | 0 | hair left back 5f |  |  |  |  | 0 | 0 |
| 658 | hair left back 5f | hair left back 5f | hair left back 5e | (0.733, 13.792, 0.465) | RMVC | 0 | hair left back 5g |  |  |  |  | 0 | 0 |
| 659 | hair left back 5g | hair left back 5g | hair left back 5f | (0.729, 13.329, 0.463) | RMVC | 0 | hair left back 5h |  |  |  |  | 0 | 0 |
| 660 | hair left back 5h | hair left back 5h | hair left back 5g | (0.725, 12.866, 0.460) | RMVC | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 661 | hair left back 1a | hair left back 1a | unused head neck upper attached-full head neck upper | (0.772, 15.485, 0.282) | RMVC | 0 | hair left back 1b |  |  |  |  | 0 | 0 |
| 662 | hair left back 1b | hair left back 1b | hair left back 1a | (0.768, 15.033, 0.281) | RMVC | 0 | hair left back 1c |  |  |  |  | 0 | 0 |
| 663 | hair left back 1c | hair left back 1c | hair left back 1b | (0.765, 14.581, 0.280) | RMVC | 0 | hair left back 1d |  |  |  |  | 0 | 0 |
| 664 | hair left back 1d | hair left back 1d | hair left back 1c | (0.761, 14.130, 0.278) | RMVC | 0 | hair left back 1e |  |  |  |  | 0 | 0 |
| 665 | hair left back 1e | hair left back 1e | hair left back 1d | (0.757, 13.678, 0.277) | RMVC | 0 | hair left back 1f |  |  |  |  | 0 | 0 |
| 666 | hair left back 1f | hair left back 1f | hair left back 1e | (0.753, 13.226, 0.276) | RMVC | 0 | hair left back 1g |  |  |  |  | 0 | 0 |
| 667 | hair left back 1g | hair left back 1g | hair left back 1f | (0.750, 12.775, 0.275) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 668 | hair back 2a | hair back 2a | unused head neck upper attached-full head neck upper | (-0.332, 16.153, 1.059) | RMVC | 0 | hair back 2b |  |  |  |  | 0 | 0 |
| 669 | hair back 2b | hair back 2b | hair back 2a | (-0.334, 15.689, 1.057) | RMVC | 0 | hair back 2c |  |  |  |  | 0 | 0 |
| 670 | hair back 2c | hair back 2c | hair back 2b | (-0.335, 15.226, 1.055) | RMVC | 0 | hair back 2d |  |  |  |  | 0 | 0 |
| 671 | hair back 2d | hair back 2d | hair back 2c | (-0.337, 14.763, 1.053) | RMVC | 0 | hair back 2e |  |  |  |  | 0 | 0 |
| 672 | hair back 2e | hair back 2e | hair back 2d | (-0.338, 14.300, 1.051) | RMVC | 0 | hair back 2f |  |  |  |  | 0 | 0 |
| 673 | hair back 2f | hair back 2f | hair back 2e | (-0.340, 13.837, 1.048) | RMVC | 0 | hair back 2g |  |  |  |  | 0 | 0 |
| 674 | hair back 2g | hair back 2g | hair back 2f | (-0.342, 13.374, 1.046) | RMVC | 0 | hair back 2h |  |  |  |  | 0 | 0 |
| 675 | hair back 2h | hair back 2h | hair back 2g | (-0.343, 12.911, 1.044) | RMVC | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 676 | hair right back 6a | hair right back 6a | unused head neck upper attached-full head neck upper | (-0.775, 16.118, 0.695) | RMVC | 0 | hair right back 6b |  |  |  |  | 0 | 0 |
| 677 | hair right back 6b | hair right back 6b | hair right back 6a | (-0.777, 15.655, 0.694) | RMVC | 0 | hair right back 6c |  |  |  |  | 0 | 0 |
| 678 | hair right back 6c | hair right back 6c | hair right back 6b | (-0.780, 15.192, 0.692) | RMVC | 0 | hair right back 6d |  |  |  |  | 0 | 0 |
| 679 | hair right back 6d | hair right back 6d | hair right back 6c | (-0.782, 14.729, 0.691) | RMVC | 0 | hair right back 6e |  |  |  |  | 0 | 0 |
| 680 | hair right back 6e | hair right back 6e | hair right back 6d | (-0.784, 14.266, 0.690) | RMVC | 0 | hair right back 6f |  |  |  |  | 0 | 0 |
| 681 | hair right back 6f | hair right back 6f | hair right back 6e | (-0.786, 13.803, 0.689) | RMVC | 0 | hair right back 6g |  |  |  |  | 0 | 0 |
| 682 | hair right back 6g | hair right back 6g | hair right back 6f | (-0.789, 13.340, 0.688) | RMVC | 0 | hair right back 6h |  |  |  |  | 0 | 0 |
| 683 | hair right back 6h | hair right back 6h | hair right back 6g | (-0.791, 12.876, 0.687) | RMVC | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 684 | hair right back 2a | hair right back 2a | unused head neck upper attached-full head neck upper | (-0.817, 15.497, 0.356) | RMVC | 0 | hair right back 2b |  |  |  |  | 0 | 0 |
| 685 | hair right back 2b | hair right back 2b | hair right back 2a | (-0.819, 15.045, 0.356) | RMVC | 0 | hair right back 2c |  |  |  |  | 0 | 0 |
| 686 | hair right back 2c | hair right back 2c | hair right back 2b | (-0.822, 14.594, 0.356) | RMVC | 0 | hair right back 2d |  |  |  |  | 0 | 0 |
| 687 | hair right back 2d | hair right back 2d | hair right back 2c | (-0.825, 14.142, 0.356) | RMVC | 0 | hair right back 2e |  |  |  |  | 0 | 0 |
| 688 | hair right back 2e | hair right back 2e | hair right back 2d | (-0.827, 13.690, 0.356) | RMVC | 0 | hair right back 2f |  |  |  |  | 0 | 0 |
| 689 | hair right back 2f | hair right back 2f | hair right back 2e | (-0.830, 13.238, 0.356) | RMVC | 0 | hair right back 2g |  |  |  |  | 0 | 0 |
| 690 | hair right back 2g | hair right back 2g | hair right back 2f | (-0.832, 12.787, 0.356) | RMVC | 0 | (-0.00, -0.45, 0.00) |  |  |  |  | 0 | 0 |
| 691 | hair right back 1a | hair right back 1a | unused head neck upper attached-full head neck upper | (-0.767, 15.497, 0.282) | RMVC | 0 | hair right back 1b |  |  |  |  | 0 | 0 |
| 692 | hair right back 1b | hair right back 1b | hair right back 1a | (-0.769, 15.045, 0.282) | RMVC | 0 | hair right back 1c |  |  |  |  | 0 | 0 |
| 693 | hair right back 1c | hair right back 1c | hair right back 1b | (-0.772, 14.594, 0.282) | RMVC | 0 | hair right back 1d |  |  |  |  | 0 | 0 |
| 694 | hair right back 1d | hair right back 1d | hair right back 1c | (-0.775, 14.142, 0.282) | RMVC | 0 | hair right back 1e |  |  |  |  | 0 | 0 |
| 695 | hair right back 1e | hair right back 1e | hair right back 1d | (-0.778, 13.690, 0.282) | RMVC | 0 | hair right back 1f |  |  |  |  | 0 | 0 |
| 696 | hair right back 1f | hair right back 1f | hair right back 1e | (-0.781, 13.239, 0.282) | RMVC | 0 | hair right back 1g |  |  |  |  | 0 | 0 |
| 697 | hair right back 1g | hair right back 1g | hair right back 1f | (-0.784, 12.787, 0.282) | RMVC | 0 | (-0.00, -0.45, -0.00) |  |  |  |  | 0 | 0 |
| 698 | hair left back 6a | hair left back 6a | unused head neck upper attached-full head neck upper | (0.774, 16.106, 0.725) | RMVC | 0 | hair left back 6b |  |  |  |  | 0 | 0 |
| 699 | hair left back 6b | hair left back 6b | hair left back 6a | (0.770, 15.643, 0.723) | RMVC | 0 | hair left back 6c |  |  |  |  | 0 | 0 |
| 700 | hair left back 6c | hair left back 6c | hair left back 6b | (0.766, 15.180, 0.720) | RMVC | 0 | hair left back 6d |  |  |  |  | 0 | 0 |
| 701 | hair left back 6d | hair left back 6d | hair left back 6c | (0.763, 14.717, 0.717) | RMVC | 0 | hair left back 6e |  |  |  |  | 0 | 0 |
| 702 | hair left back 6e | hair left back 6e | hair left back 6d | (0.759, 14.254, 0.714) | RMVC | 0 | hair left back 6f |  |  |  |  | 0 | 0 |
| 703 | hair left back 6f | hair left back 6f | hair left back 6e | (0.756, 13.790, 0.711) | RMVC | 0 | hair left back 6g |  |  |  |  | 0 | 0 |
| 704 | hair left back 6g | hair left back 6g | hair left back 6f | (0.752, 13.327, 0.709) | RMVC | 0 | hair left back 6h |  |  |  |  | 0 | 0 |
| 705 | hair left back 6h | hair left back 6h | hair left back 6g | (0.748, 12.864, 0.706) | RMVC | 0 | (-0.00, -0.46, -0.00) |  |  |  |  | 0 | 0 |
| 706 | unusedopt-dummy-head item-honoka hair +3 item-full head | unusedopt-dummy-head item-honoka hair +3 item-full head | unused head neck upper attached-full head neck upper | (-0.000, 14.699, 0.097) | RM-C | 0 | (-0.00, -0.16, -0.05) |  |  |  |  | 0 | 0 |
| 707 | unused pelvis | unused pelvis | センター | (0.000, 10.000, -0.000) | RM-C | 0 | (0.00, 0.04, 0.04) |  |  |  |  | 0 | 0 |
| 708 | unused leg left thigh | unused leg left thigh | unused pelvis | (0.766, 9.647, 0.222) | RM-C | 0 | (0.01, -1.03, -0.09) |  |  |  |  | 0 | 0 |
| 709 | unused leg left knee | unused leg left knee | unused leg left thigh | (1.814, 5.735, 0.222) | RM-C | 0 | (0.54, -2.03, -0.00) |  |  |  |  | 0 | 0 |
| 710 | unused leg left ankle | unused leg left ankle | unused leg left knee | (2.901, 1.679, 0.222) | RM-C | 0 | unused leg left toes |  |  |  |  | 0 | 0 |
| 711 | unused leg left toes | unused leg left toes | unused leg left ankle | (3.114, 0.887, -0.748) | RM-C | 0 | (0.21, -0.79, -0.97) |  |  |  |  | 0 | 0 |
| 712 | unused ctr leg left thigh 4 | unused ctr leg left thigh 4 | unused leg left knee | (1.814, 5.735, 0.212) | RM-C | 0 | (-0.00, 0.00, -0.01) |  |  |  |  | 0 | 0 |
| 713 | unused ctr leg left thigh 2 | unused ctr leg left thigh 2 | unused leg left thigh | (0.767, 9.648, 0.222) | RM-C | 0 | (0.00, 0.00, -0.00) |  |  |  |  | 0 | 0 |
| 714 | unused ctr leg left thigh 3 | unused ctr leg left thigh 3 | unused leg left thigh | (1.290, 7.691, 0.222) | RM-C | 0 | (0.52, -1.96, 0.00) |  |  |  |  | 0 | 0 |
| 715 | unused ribbon left a root | unused ribbon left a root | unused leg left thigh | (0.000, 10.000, -0.000) | RM-C | 0 | unused ribbon left a 1 |  |  |  |  | 0 | 0 |
| 716 | unused ribbon left a 1 | unused ribbon left a 1 | unused ribbon left a root | (1.531, 9.593, -0.775) | RM-C | 0 | unused ribbon left a 2 |  |  |  |  | 0 | 0 |
| 717 | unused ribbon left a 2 | unused ribbon left a 2 | unused ribbon left a 1 | (1.561, 9.515, -0.819) | RM-C | 0 | unused ribbon left a 3 |  |  |  |  | 0 | 0 |
| 718 | unused ribbon left a 3 | unused ribbon left a 3 | unused ribbon left a 2 | (1.593, 9.433, -0.868) | RM-C | 0 | unused ribbon left a 4 |  |  |  |  | 0 | 0 |
| 719 | unused ribbon left a 4 | unused ribbon left a 4 | unused ribbon left a 3 | (1.662, 9.231, -0.985) | RM-C | 0 | unused ribbon left a 5 |  |  |  |  | 0 | 0 |
| 720 | unused ribbon left a 5 | unused ribbon left a 5 | unused ribbon left a 4 | (1.727, 8.940, -1.125) | RM-C | 0 | unused ribbon left a 6 |  |  |  |  | 0 | 0 |
| 721 | unused ribbon left a 6 | unused ribbon left a 6 | unused ribbon left a 5 | (1.779, 8.642, -1.245) | RM-C | 0 | unused ribbon left a 7 |  |  |  |  | 0 | 0 |
| 722 | unused ribbon left a 7 | unused ribbon left a 7 | unused ribbon left a 6 | (1.799, 8.310, -1.356) | RM-C | 0 | (0.02, -0.33, -0.11) |  |  |  |  | 0 | 0 |
| 723 | unused ribbon left b root | unused ribbon left b root | unused leg left thigh | (0.000, 10.000, -0.000) | RM-C | 0 | unused ribbon left b 1 |  |  |  |  | 0 | 0 |
| 724 | unused ribbon left b 1 | unused ribbon left b 1 | unused ribbon left b root | (1.543, 9.627, -0.700) | RM-C | 0 | unused ribbon left b 2 |  |  |  |  | 0 | 0 |
| 725 | unused ribbon left b 2 | unused ribbon left b 2 | unused ribbon left b 1 | (1.667, 9.596, -0.654) | RM-C | 0 | unused ribbon left b 3 |  |  |  |  | 0 | 0 |
| 726 | unused ribbon left b 3 | unused ribbon left b 3 | unused ribbon left b 2 | (1.769, 9.549, -0.599) | RM-C | 0 | unused ribbon left b 4 |  |  |  |  | 0 | 0 |
| 727 | unused ribbon left b 4 | unused ribbon left b 4 | unused ribbon left b 3 | (1.982, 9.421, -0.481) | RM-C | 0 | unused ribbon left b 5 |  |  |  |  | 0 | 0 |
| 728 | unused ribbon left b 5 | unused ribbon left b 5 | unused ribbon left b 4 | (2.190, 9.256, -0.374) | RM-C | 0 | unused ribbon left b 6 |  |  |  |  | 0 | 0 |
| 729 | unused ribbon left b 6 | unused ribbon left b 6 | unused ribbon left b 5 | (2.436, 9.024, -0.253) | RM-C | 0 | unused ribbon left b 7 |  |  |  |  | 0 | 0 |
| 730 | unused ribbon left b 7 | unused ribbon left b 7 | unused ribbon left b 6 | (2.640, 8.764, -0.107) | RM-C | 0 | (0.20, -0.26, 0.15) |  |  |  |  | 0 | 0 |
| 731 | unused leg right thigh | unused leg right thigh | unused pelvis | (-0.766, 9.647, 0.222) | RM-C | 0 | (-0.01, -1.03, -0.09) |  |  |  |  | 0 | 0 |
| 732 | unused leg right knee | unused leg right knee | unused leg right thigh | (-1.814, 5.735, 0.222) | RM-C | 0 | (-0.54, -2.03, -0.00) |  |  |  |  | 0 | 0 |
| 733 | unused leg right ankle | unused leg right ankle | unused leg right knee | (-2.901, 1.679, 0.222) | RM-C | 0 | unused leg right toes |  |  |  |  | 0 | 0 |
| 734 | unused leg right toes | unused leg right toes | unused leg right ankle | (-3.114, 0.887, -0.748) | RM-C | 0 | (-0.21, -0.79, -0.97) |  |  |  |  | 0 | 0 |
| 735 | unused ctr leg right thigh 4 | unused ctr leg right thigh 4 | unused leg right knee | (-1.814, 5.735, 0.212) | RM-C | 0 | (0.00, -0.00, -0.01) |  |  |  |  | 0 | 0 |
| 736 | unused ctr leg right thigh 2 | unused ctr leg right thigh 2 | unused leg right thigh | (-0.767, 9.648, 0.222) | RM-C | 0 | (-0.00, 0.00, -0.00) |  |  |  |  | 0 | 0 |
| 737 | unused ctr leg right thigh 3 | unused ctr leg right thigh 3 | unused leg right thigh | (-1.290, 7.691, 0.222) | RM-C | 0 | (-0.52, -1.96, 0.00) |  |  |  |  | 0 | 0 |
| 738 | unused ribbon right a root | unused ribbon right a root | unused leg right thigh | (-0.000, 10.000, -0.000) | RM-C | 0 | unused ribbon right a 1 |  |  |  |  | 0 | 0 |
| 739 | unused ribbon right a 1 | unused ribbon right a 1 | unused ribbon right a root | (-1.531, 9.593, -0.775) | RM-C | 0 | unused ribbon right a 2 |  |  |  |  | 0 | 0 |
| 740 | unused ribbon right a 2 | unused ribbon right a 2 | unused ribbon right a 1 | (-1.561, 9.515, -0.819) | RM-C | 0 | unused ribbon right a 3 |  |  |  |  | 0 | 0 |
| 741 | unused ribbon right a 3 | unused ribbon right a 3 | unused ribbon right a 2 | (-1.593, 9.433, -0.868) | RM-C | 0 | unused ribbon right a 4 |  |  |  |  | 0 | 0 |
| 742 | unused ribbon right a 4 | unused ribbon right a 4 | unused ribbon right a 3 | (-1.662, 9.231, -0.985) | RM-C | 0 | unused ribbon right a 5 |  |  |  |  | 0 | 0 |
| 743 | unused ribbon right a 5 | unused ribbon right a 5 | unused ribbon right a 4 | (-1.727, 8.940, -1.125) | RM-C | 0 | unused ribbon right a 6 |  |  |  |  | 0 | 0 |
| 744 | unused ribbon right a 6 | unused ribbon right a 6 | unused ribbon right a 5 | (-1.779, 8.642, -1.245) | RM-C | 0 | unused ribbon right a 7 |  |  |  |  | 0 | 0 |
| 745 | unused ribbon right a 7 | unused ribbon right a 7 | unused ribbon right a 6 | (-1.799, 8.310, -1.356) | RM-C | 0 | (-0.02, -0.33, -0.11) |  |  |  |  | 0 | 0 |
| 746 | unused ribbon right b root | unused ribbon right b root | unused leg right thigh | (-0.000, 10.000, -0.000) | RM-C | 0 | unused ribbon right b 1 |  |  |  |  | 0 | 0 |
| 747 | unused ribbon right b 1 | unused ribbon right b 1 | unused ribbon right b root | (-1.543, 9.627, -0.700) | RM-C | 0 | unused ribbon right b 2 |  |  |  |  | 0 | 0 |
| 748 | unused ribbon right b 2 | unused ribbon right b 2 | unused ribbon right b 1 | (-1.667, 9.596, -0.654) | RM-C | 0 | unused ribbon right b 3 |  |  |  |  | 0 | 0 |
| 749 | unused ribbon right b 3 | unused ribbon right b 3 | unused ribbon right b 2 | (-1.769, 9.549, -0.599) | RM-C | 0 | unused ribbon right b 4 |  |  |  |  | 0 | 0 |
| 750 | unused ribbon right b 4 | unused ribbon right b 4 | unused ribbon right b 3 | (-1.982, 9.421, -0.481) | RM-C | 0 | unused ribbon right b 5 |  |  |  |  | 0 | 0 |
| 751 | unused ribbon right b 5 | unused ribbon right b 5 | unused ribbon right b 4 | (-2.190, 9.256, -0.374) | RM-C | 0 | unused ribbon right b 6 |  |  |  |  | 0 | 0 |
| 752 | unused ribbon right b 6 | unused ribbon right b 6 | unused ribbon right b 5 | (-2.436, 9.024, -0.253) | RM-C | 0 | unused ribbon right b 7 |  |  |  |  | 0 | 0 |
| 753 | unused ribbon right b 7 | unused ribbon right b 7 | unused ribbon right b 6 | (-2.640, 8.764, -0.107) | RM-C | 0 | (-0.20, -0.26, 0.15) |  |  |  |  | 0 | 0 |
| 754 | unused ctr leg left thigh 1 | unused ctr leg left thigh 1 | unused pelvis | (0.763, 9.657, 0.222) | RM-C | 0 | (0.76, -0.34, 0.22) |  |  |  |  | 0 | 0 |
| 755 | unused ctr leg right thigh 1 | unused ctr leg right thigh 1 | unused pelvis | (-0.763, 9.657, 0.222) | RM-C | 0 | (-0.76, -0.34, 0.22) |  |  |  |  | 0 | 0 |
| 756 | unused katana ribbon b root | unused katana ribbon b root | unused pelvis | (0.000, 10.824, -0.328) | RM-C | 0 | unused katana ribbon b 1 |  |  |  |  | 0 | 0 |
| 757 | unused katana ribbon b 1 | unused katana ribbon b 1 | unused katana ribbon b root | (-2.592, 11.153, 0.627) | RM-C | 0 | unused katana ribbon b 2 |  |  |  |  | 0 | 0 |
| 758 | unused katana ribbon b 2 | unused katana ribbon b 2 | unused katana ribbon b 1 | (-2.592, 10.829, 0.627) | RM-C | 0 | unused katana ribbon b 3 |  |  |  |  | 0 | 0 |
| 759 | unused katana ribbon b 3 | unused katana ribbon b 3 | unused katana ribbon b 2 | (-2.592, 10.505, 0.627) | RM-C | 0 | unused katana ribbon b 4 |  |  |  |  | 0 | 0 |
| 760 | unused katana ribbon b 4 | unused katana ribbon b 4 | unused katana ribbon b 3 | (-2.592, 10.181, 0.627) | RM-C | 0 | unused katana ribbon b 5 |  |  |  |  | 0 | 0 |
| 761 | unused katana ribbon b 5 | unused katana ribbon b 5 | unused katana ribbon b 4 | (-2.592, 9.857, 0.627) | RM-C | 0 | unused katana ribbon b 6 |  |  |  |  | 0 | 0 |
| 762 | unused katana ribbon b 6 | unused katana ribbon b 6 | unused katana ribbon b 5 | (-2.592, 9.533, 0.627) | RM-C | 0 | unused katana ribbon b 7 |  |  |  |  | 0 | 0 |
| 763 | unused katana ribbon b 7 | unused katana ribbon b 7 | unused katana ribbon b 6 | (-2.592, 9.209, 0.627) | RM-C | 0 | unused katana ribbon b 8 |  |  |  |  | 0 | 0 |
| 764 | unused katana ribbon b 8 | unused katana ribbon b 8 | unused katana ribbon b 7 | (-2.592, 8.885, 0.627) | RM-C | 0 | unused katana ribbon b 9 |  |  |  |  | 0 | 0 |
| 765 | unused katana ribbon b 9 | unused katana ribbon b 9 | unused katana ribbon b 8 | (-2.592, 8.561, 0.627) | RM-C | 0 | unused katana ribbon b 10 |  |  |  |  | 0 | 0 |
| 766 | unused katana ribbon b 10 | unused katana ribbon b 10 | unused katana ribbon b 9 | (-2.592, 8.237, 0.627) | RM-C | 0 | unused katana ribbon b 11 |  |  |  |  | 0 | 0 |
| 767 | unused katana ribbon b 11 | unused katana ribbon b 11 | unused katana ribbon b 10 | (-2.592, 7.913, 0.627) | RM-C | 0 | unused katana ribbon b 12 |  |  |  |  | 0 | 0 |
| 768 | unused katana ribbon b 12 | unused katana ribbon b 12 | unused katana ribbon b 11 | (-2.592, 7.589, 0.627) | RM-C | 0 | unused katana ribbon b 13 |  |  |  |  | 0 | 0 |
| 769 | unused katana ribbon b 13 | unused katana ribbon b 13 | unused katana ribbon b 12 | (-2.592, 7.265, 0.627) | RM-C | 0 | unused katana ribbon b 14 |  |  |  |  | 0 | 0 |
| 770 | unused katana ribbon b 14 | unused katana ribbon b 14 | unused katana ribbon b 13 | (-2.592, 6.941, 0.627) | RM-C | 0 | (0.00, -0.32, 0.00) |  |  |  |  | 0 | 0 |
| 771 | unused katana ribbon a root | unused katana ribbon a root | unused pelvis | (0.000, 10.824, -0.328) | RM-C | 0 | unused katana ribbon a 1 |  |  |  |  | 0 | 0 |
| 772 | unused katana ribbon a 1 | unused katana ribbon a 1 | unused katana ribbon a root | (-2.592, 11.153, 0.672) | RM-C | 0 | unused katana ribbon a 2 |  |  |  |  | 0 | 0 |
| 773 | unused katana ribbon a 2 | unused katana ribbon a 2 | unused katana ribbon a 1 | (-2.592, 10.829, 0.672) | RM-C | 0 | unused katana ribbon a 3 |  |  |  |  | 0 | 0 |
| 774 | unused katana ribbon a 3 | unused katana ribbon a 3 | unused katana ribbon a 2 | (-2.592, 10.505, 0.672) | RM-C | 0 | unused katana ribbon a 4 |  |  |  |  | 0 | 0 |
| 775 | unused katana ribbon a 4 | unused katana ribbon a 4 | unused katana ribbon a 3 | (-2.592, 10.181, 0.672) | RM-C | 0 | unused katana ribbon a 5 |  |  |  |  | 0 | 0 |
| 776 | unused katana ribbon a 5 | unused katana ribbon a 5 | unused katana ribbon a 4 | (-2.592, 9.857, 0.672) | RM-C | 0 | unused katana ribbon a 6 |  |  |  |  | 0 | 0 |
| 777 | unused katana ribbon a 6 | unused katana ribbon a 6 | unused katana ribbon a 5 | (-2.592, 9.533, 0.672) | RM-C | 0 | unused katana ribbon a 7 |  |  |  |  | 0 | 0 |
| 778 | unused katana ribbon a 7 | unused katana ribbon a 7 | unused katana ribbon a 6 | (-2.592, 9.209, 0.672) | RM-C | 0 | unused katana ribbon a 8 |  |  |  |  | 0 | 0 |
| 779 | unused katana ribbon a 8 | unused katana ribbon a 8 | unused katana ribbon a 7 | (-2.592, 8.885, 0.672) | RM-C | 0 | unused katana ribbon a 9 |  |  |  |  | 0 | 0 |
| 780 | unused katana ribbon a 9 | unused katana ribbon a 9 | unused katana ribbon a 8 | (-2.592, 8.561, 0.672) | RM-C | 0 | unused katana ribbon a 10 |  |  |  |  | 0 | 0 |
| 781 | unused katana ribbon a 10 | unused katana ribbon a 10 | unused katana ribbon a 9 | (-2.592, 8.237, 0.672) | RM-C | 0 | (-0.00, -0.32, 0.00) |  |  |  |  | 0 | 0 |
| 782 | unused head tongue 1 | unused head tongue 1 | unused head jaw | (0.000, 14.840, -0.229) | RM-C | 0 | unused head tongue 2 |  |  |  |  | 0 | 0 |
| 783 | unused head tongue 2 | unused head tongue 2 | unused head tongue 1 | (0.000, 14.869, -0.504) | RM-C | 0 | (0.00, 0.03, -0.27) |  |  |  |  | 0 | 0 |
| 784 | unused head cheek left 1 | unused head cheek left 1 | unused face | (0.302, 15.155, -0.697) | RM-C | 0 | (0.30, 0.28, -0.82) |  |  |  |  | 0 | 0 |
| 785 | unused head cheek left 2 | unused head cheek left 2 | unused face | (0.475, 15.163, -0.584) | RM-C | 0 | (0.47, 0.28, -0.70) |  |  |  |  | 0 | 0 |
| 786 | unused head cheek left 3 | unused head cheek left 3 | unused face | (0.517, 14.991, -0.452) | RM-C | 0 | (0.52, 0.11, -0.57) |  |  |  |  | 0 | 0 |
| 787 | unused head eyelid left lower 1 | unused head eyelid left lower 1 | unused face | (0.233, 15.330, -0.677) | RM-C | 0 | (0.23, 0.45, -0.80) |  |  |  |  | 0 | 0 |
| 788 | unused head eyelid left lower 2 | unused head eyelid left lower 2 | unused face | (0.355, 15.322, -0.674) | RM-C | 0 | (0.35, 0.44, -0.79) |  |  |  |  | 0 | 0 |
| 789 | unused head eyebrow left 1 | unused head eyebrow left 1 | unused face | (0.102, 15.523, -0.781) | RM-C | 0 | (0.10, 0.64, -0.90) |  |  |  |  | 0 | 0 |
| 790 | unused head eyebrow left 2 | unused head eyebrow left 2 | unused face | (0.367, 15.617, -0.721) | RM-C | 0 | (0.37, 0.74, -0.84) |  |  |  |  | 0 | 0 |
| 791 | unused head eyebrow left 3 | unused head eyebrow left 3 | unused face | (0.494, 15.567, -0.603) | RM-C | 0 | (0.49, 0.69, -0.72) |  |  |  |  | 0 | 0 |
| 792 | unused head eyelid left upper | unused head eyelid left upper | unused face | (0.295, 15.435, -0.527) | RM-C | 0 | (0.30, 0.56, -0.65) |  |  |  |  | 0 | 0 |
| 793 | unused head nose left 1 | unused head nose left 1 | unused face | (0.114, 15.252, -0.748) | RM-C | 0 | (0.11, 0.37, -0.87) |  |  |  |  | 0 | 0 |
| 794 | unused head nose left 2 | unused head nose left 2 | unused face | (0.138, 15.097, -0.757) | RM-C | 0 | (0.14, 0.22, -0.88) |  |  |  |  | 0 | 0 |
| 795 | unused head nose left 3 | unused head nose left 3 | unused face | (0.236, 15.003, -0.702) | RM-C | 0 | (0.24, 0.12, -0.82) |  |  |  |  | 0 | 0 |
| 796 | unused head nose left 4 | unused head nose left 4 | unused face | (0.301, 14.936, -0.657) | RM-C | 0 | (0.30, 0.06, -0.78) |  |  |  |  | 0 | 0 |
| 797 | unused head cheek right 1 | unused head cheek right 1 | unused face | (-0.302, 15.155, -0.697) | RM-C | 0 | (-0.30, 0.28, -0.82) |  |  |  |  | 0 | 0 |
| 798 | unused head cheek right 2 | unused head cheek right 2 | unused face | (-0.475, 15.163, -0.584) | RM-C | 0 | (-0.47, 0.28, -0.70) |  |  |  |  | 0 | 0 |
| 799 | unused head cheek right 3 | unused head cheek right 3 | unused face | (-0.517, 14.991, -0.452) | RM-C | 0 | (-0.52, 0.11, -0.57) |  |  |  |  | 0 | 0 |
| 800 | unused head eyelid right lower 1 | unused head eyelid right lower 1 | unused face | (-0.233, 15.330, -0.677) | RM-C | 0 | (-0.23, 0.45, -0.80) |  |  |  |  | 0 | 0 |
| 801 | unused head eyelid right lower 2 | unused head eyelid right lower 2 | unused face | (-0.355, 15.322, -0.674) | RM-C | 0 | (-0.35, 0.44, -0.79) |  |  |  |  | 0 | 0 |
| 802 | unused head eyebrow right 1 | unused head eyebrow right 1 | unused face | (-0.102, 15.523, -0.781) | RM-C | 0 | (-0.10, 0.64, -0.90) |  |  |  |  | 0 | 0 |
| 803 | unused head eyebrow right 2 | unused head eyebrow right 2 | unused face | (-0.368, 15.617, -0.721) | RM-C | 0 | (-0.37, 0.74, -0.84) |  |  |  |  | 0 | 0 |
| 804 | unused head eyebrow right 3 | unused head eyebrow right 3 | unused face | (-0.494, 15.567, -0.603) | RM-C | 0 | (-0.49, 0.69, -0.72) |  |  |  |  | 0 | 0 |
| 805 | unused head eyelid right upper | unused head eyelid right upper | unused face | (-0.295, 15.435, -0.527) | RM-C | 0 | (-0.30, 0.56, -0.65) |  |  |  |  | 0 | 0 |
| 806 | unused head nose right 1 | unused head nose right 1 | unused face | (-0.114, 15.252, -0.748) | RM-C | 0 | (-0.11, 0.37, -0.87) |  |  |  |  | 0 | 0 |
| 807 | unused head nose right 2 | unused head nose right 2 | unused face | (-0.138, 15.097, -0.757) | RM-C | 0 | (-0.14, 0.22, -0.88) |  |  |  |  | 0 | 0 |
| 808 | unused head nose right 3 | unused head nose right 3 | unused face | (-0.236, 15.003, -0.702) | RM-C | 0 | (-0.24, 0.12, -0.82) |  |  |  |  | 0 | 0 |
| 809 | unused head nose right 4 | unused head nose right 4 | unused face | (-0.301, 14.936, -0.657) | RM-C | 0 | (-0.30, 0.06, -0.78) |  |  |  |  | 0 | 0 |
| 810 | unused hair root | unused hair root | 頭 | (-0.000, 14.871, 0.062) | RM-C | 0 | (0.00, 0.00, -0.00) |  |  |  |  | 0 | 0 |
| 811 | unused hair root front | unused hair root front | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | (-0.00, 1.52, -0.72) |  |  |  |  | 0 | 0 |
| 812 | unused hair front middle 1 | unused hair front middle 1 | unused hair root front | (-0.000, 16.458, -0.885) | RM-C | 0 | unused hair front middle 2 |  |  |  |  | 0 | 0 |
| 813 | unused hair front middle 2 | unused hair front middle 2 | unused hair front middle 1 | (-0.000, 16.082, -1.082) | RM-C | 0 | unused hair front middle 3 |  |  |  |  | 0 | 0 |
| 814 | unused hair front middle 3 | unused hair front middle 3 | unused hair front middle 2 | (-0.000, 15.711, -1.083) | RM-C | 0 | unused hair front middle 4 |  |  |  |  | 0 | 0 |
| 815 | unused hair front middle 4 | unused hair front middle 4 | unused hair front middle 3 | (0.000, 15.340, -0.970) | RM-C | 0 | (0.00, -0.37, 0.11) |  |  |  |  | 0 | 0 |
| 816 | unused hair front left b 1 | unused hair front left b 1 | unused hair root front | (0.549, 16.457, -0.437) | RM-C | 0 | unused hair front left b 2 |  |  |  |  | 0 | 0 |
| 817 | unused hair front left b 2 | unused hair front left b 2 | unused hair front left b 1 | (0.762, 16.064, -0.402) | RM-C | 0 | unused hair front left b 3 |  |  |  |  | 0 | 0 |
| 818 | unused hair front left b 3 | unused hair front left b 3 | unused hair front left b 2 | (0.795, 15.610, -0.274) | RM-C | 0 | unused hair front left b 4 |  |  |  |  | 0 | 0 |
| 819 | unused hair front left b 4 | unused hair front left b 4 | unused hair front left b 3 | (0.730, 15.155, -0.206) | RM-C | 0 | unused hair front left b 5 |  |  |  |  | 0 | 0 |
| 820 | unused hair front left b 5 | unused hair front left b 5 | unused hair front left b 4 | (0.608, 14.711, -0.289) | RM-C | 0 | (-0.12, -0.44, -0.08) |  |  |  |  | 0 | 0 |
| 821 | unused hair front left a 1 | unused hair front left a 1 | unused hair root front | (0.426, 16.289, -0.752) | RM-C | 0 | unused hair front left a 2 |  |  |  |  | 0 | 0 |
| 822 | unused hair front left a 2 | unused hair front left a 2 | unused hair front left a 1 | (0.491, 15.961, -0.811) | RM-C | 0 | unused hair front left a 3 |  |  |  |  | 0 | 0 |
| 823 | unused hair front left a 3 | unused hair front left a 3 | unused hair front left a 2 | (0.525, 15.647, -0.815) | RM-C | 0 | unused hair front left a 4 |  |  |  |  | 0 | 0 |
| 824 | unused hair front left a 4 | unused hair front left a 4 | unused hair front left a 3 | (0.484, 15.332, -0.724) | RM-C | 0 | (-0.04, -0.31, 0.09) |  |  |  |  | 0 | 0 |
| 825 | unused hair front right a 1 | unused hair front right a 1 | unused hair root front | (-0.426, 16.289, -0.752) | RM-C | 0 | unused hair front right a 2 |  |  |  |  | 0 | 0 |
| 826 | unused hair front right a 2 | unused hair front right a 2 | unused hair front right a 1 | (-0.491, 15.961, -0.811) | RM-C | 0 | unused hair front right a 3 |  |  |  |  | 0 | 0 |
| 827 | unused hair front right a 3 | unused hair front right a 3 | unused hair front right a 2 | (-0.525, 15.647, -0.815) | RM-C | 0 | unused hair front right a 4 |  |  |  |  | 0 | 0 |
| 828 | unused hair front right a 4 | unused hair front right a 4 | unused hair front right a 3 | (-0.484, 15.332, -0.724) | RM-C | 0 | (0.04, -0.31, 0.09) |  |  |  |  | 0 | 0 |
| 829 | unused hair front right b 1 | unused hair front right b 1 | unused hair root front | (-0.549, 16.457, -0.437) | RM-C | 0 | unused hair front right b 2 |  |  |  |  | 0 | 0 |
| 830 | unused hair front right b 2 | unused hair front right b 2 | unused hair front right b 1 | (-0.762, 16.064, -0.402) | RM-C | 0 | unused hair front right b 3 |  |  |  |  | 0 | 0 |
| 831 | unused hair front right b 3 | unused hair front right b 3 | unused hair front right b 2 | (-0.795, 15.610, -0.274) | RM-C | 0 | unused hair front right b 4 |  |  |  |  | 0 | 0 |
| 832 | unused hair front right b 4 | unused hair front right b 4 | unused hair front right b 3 | (-0.730, 15.155, -0.206) | RM-C | 0 | unused hair front right b 5 |  |  |  |  | 0 | 0 |
| 833 | unused hair front right b 5 | unused hair front right b 5 | unused hair front right b 4 | (-0.608, 14.711, -0.289) | RM-C | 0 | (0.12, -0.44, -0.08) |  |  |  |  | 0 | 0 |
| 834 | unused hair root back right a | unused hair root back right a | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right a 1 |  |  |  |  | 0 | 0 |
| 835 | unused hair back right a 1 | unused hair back right a 1 | unused hair root back right a | (-0.269, 16.106, 1.032) | RM-C | 0 | unused hair back right a 2 |  |  |  |  | 0 | 0 |
| 836 | unused hair back right a 2 | unused hair back right a 2 | unused hair back right a 1 | (-0.327, 15.655, 1.105) | RM-C | 0 | unused hair back right a 3 |  |  |  |  | 0 | 0 |
| 837 | unused hair back right a 3 | unused hair back right a 3 | unused hair back right a 2 | (-0.359, 15.150, 1.127) | RM-C | 0 | unused hair back right a 4 |  |  |  |  | 0 | 0 |
| 838 | unused hair back right a 4 | unused hair back right a 4 | unused hair back right a 3 | (-0.385, 14.598, 1.145) | RM-C | 0 | unused hair back right a 5 |  |  |  |  | 0 | 0 |
| 839 | unused hair back right a 5 | unused hair back right a 5 | unused hair back right a 4 | (-0.405, 14.039, 1.153) | RM-C | 0 | unused hair back right a 6 |  |  |  |  | 0 | 0 |
| 840 | unused hair back right a 6 | unused hair back right a 6 | unused hair back right a 5 | (-0.415, 13.495, 1.155) | RM-C | 0 | unused hair back right a 7 |  |  |  |  | 0 | 0 |
| 841 | unused hair back right a 7 | unused hair back right a 7 | unused hair back right a 6 | (-0.415, 12.943, 1.162) | RM-C | 0 | unused hair back right a 8 |  |  |  |  | 0 | 0 |
| 842 | unused hair back right a 8 | unused hair back right a 8 | unused hair back right a 7 | (-0.405, 12.408, 1.159) | RM-C | 0 | unused hair back right a 9 |  |  |  |  | 0 | 0 |
| 843 | unused hair back right a 9 | unused hair back right a 9 | unused hair back right a 8 | (-0.381, 11.842, 1.152) | RM-C | 0 | unused hair back right a 10 |  |  |  |  | 0 | 0 |
| 844 | unused hair back right a 10 | unused hair back right a 10 | unused hair back right a 9 | (-0.358, 11.278, 1.144) | RM-C | 0 | (0.02, -0.56, -0.01) |  |  |  |  | 0 | 0 |
| 845 | unused hair root back left a | unused hair root back left a | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left a 1 |  |  |  |  | 0 | 0 |
| 846 | unused hair back left a 1 | unused hair back left a 1 | unused hair root back left a | (0.269, 16.106, 1.032) | RM-C | 0 | unused hair back left a 2 |  |  |  |  | 0 | 0 |
| 847 | unused hair back left a 2 | unused hair back left a 2 | unused hair back left a 1 | (0.327, 15.655, 1.105) | RM-C | 0 | unused hair back left a 3 |  |  |  |  | 0 | 0 |
| 848 | unused hair back left a 3 | unused hair back left a 3 | unused hair back left a 2 | (0.359, 15.150, 1.127) | RM-C | 0 | unused hair back left a 4 |  |  |  |  | 0 | 0 |
| 849 | unused hair back left a 4 | unused hair back left a 4 | unused hair back left a 3 | (0.385, 14.598, 1.145) | RM-C | 0 | unused hair back left a 5 |  |  |  |  | 0 | 0 |
| 850 | unused hair back left a 5 | unused hair back left a 5 | unused hair back left a 4 | (0.405, 14.039, 1.153) | RM-C | 0 | unused hair back left a 6 |  |  |  |  | 0 | 0 |
| 851 | unused hair back left a 6 | unused hair back left a 6 | unused hair back left a 5 | (0.415, 13.495, 1.155) | RM-C | 0 | unused hair back left a 7 |  |  |  |  | 0 | 0 |
| 852 | unused hair back left a 7 | unused hair back left a 7 | unused hair back left a 6 | (0.415, 12.943, 1.162) | RM-C | 0 | unused hair back left a 8 |  |  |  |  | 0 | 0 |
| 853 | unused hair back left a 8 | unused hair back left a 8 | unused hair back left a 7 | (0.405, 12.408, 1.159) | RM-C | 0 | unused hair back left a 9 |  |  |  |  | 0 | 0 |
| 854 | unused hair back left a 9 | unused hair back left a 9 | unused hair back left a 8 | (0.381, 11.842, 1.152) | RM-C | 0 | unused hair back left a 10 |  |  |  |  | 0 | 0 |
| 855 | unused hair back left a 10 | unused hair back left a 10 | unused hair back left a 9 | (0.358, 11.278, 1.144) | RM-C | 0 | (-0.02, -0.56, -0.01) |  |  |  |  | 0 | 0 |
| 856 | unused hair root back right d | unused hair root back right d | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right d 1 |  |  |  |  | 0 | 0 |
| 857 | unused hair back right d 1 | unused hair back right d 1 | unused hair root back right d | (-0.605, 16.104, 0.795) | RM-C | 0 | unused hair back right d 2 |  |  |  |  | 0 | 0 |
| 858 | unused hair back right d 2 | unused hair back right d 2 | unused hair back right d 1 | (-0.705, 15.633, 0.790) | RM-C | 0 | unused hair back right d 3 |  |  |  |  | 0 | 0 |
| 859 | unused hair back right d 3 | unused hair back right d 3 | unused hair back right d 2 | (-0.746, 15.135, 0.777) | RM-C | 0 | unused hair back right d 4 |  |  |  |  | 0 | 0 |
| 860 | unused hair back right d 4 | unused hair back right d 4 | unused hair back right d 3 | (-0.787, 14.600, 0.764) | RM-C | 0 | unused hair back right d 5 |  |  |  |  | 0 | 0 |
| 861 | unused hair back right d 5 | unused hair back right d 5 | unused hair back right d 4 | (-0.824, 14.039, 0.753) | RM-C | 0 | unused hair back right d 6 |  |  |  |  | 0 | 0 |
| 862 | unused hair back right d 6 | unused hair back right d 6 | unused hair back right d 5 | (-0.844, 13.488, 0.746) | RM-C | 0 | unused hair back right d 7 |  |  |  |  | 0 | 0 |
| 863 | unused hair back right d 7 | unused hair back right d 7 | unused hair back right d 6 | (-0.828, 12.937, 0.741) | RM-C | 0 | unused hair back right d 8 |  |  |  |  | 0 | 0 |
| 864 | unused hair back right d 8 | unused hair back right d 8 | unused hair back right d 7 | (-0.795, 12.399, 0.735) | RM-C | 0 | unused hair back right d 9 |  |  |  |  | 0 | 0 |
| 865 | unused hair back right d 9 | unused hair back right d 9 | unused hair back right d 8 | (-0.751, 11.837, 0.730) | RM-C | 0 | unused hair back right d 10 |  |  |  |  | 0 | 0 |
| 866 | unused hair back right d 10 | unused hair back right d 10 | unused hair back right d 9 | (-0.700, 11.277, 0.721) | RM-C | 0 | (0.05, -0.56, -0.01) |  |  |  |  | 0 | 0 |
| 867 | unused hair root back left d | unused hair root back left d | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left d 1 |  |  |  |  | 0 | 0 |
| 868 | unused hair back left d 1 | unused hair back left d 1 | unused hair root back left d | (0.605, 16.104, 0.795) | RM-C | 0 | unused hair back left d 2 |  |  |  |  | 0 | 0 |
| 869 | unused hair back left d 2 | unused hair back left d 2 | unused hair back left d 1 | (0.705, 15.633, 0.790) | RM-C | 0 | unused hair back left d 3 |  |  |  |  | 0 | 0 |
| 870 | unused hair back left d 3 | unused hair back left d 3 | unused hair back left d 2 | (0.746, 15.135, 0.777) | RM-C | 0 | unused hair back left d 4 |  |  |  |  | 0 | 0 |
| 871 | unused hair back left d 4 | unused hair back left d 4 | unused hair back left d 3 | (0.787, 14.600, 0.764) | RM-C | 0 | unused hair back left d 5 |  |  |  |  | 0 | 0 |
| 872 | unused hair back left d 5 | unused hair back left d 5 | unused hair back left d 4 | (0.824, 14.039, 0.753) | RM-C | 0 | unused hair back left d 6 |  |  |  |  | 0 | 0 |
| 873 | unused hair back left d 6 | unused hair back left d 6 | unused hair back left d 5 | (0.844, 13.488, 0.746) | RM-C | 0 | unused hair back left d 7 |  |  |  |  | 0 | 0 |
| 874 | unused hair back left d 7 | unused hair back left d 7 | unused hair back left d 6 | (0.828, 12.937, 0.741) | RM-C | 0 | unused hair back left d 8 |  |  |  |  | 0 | 0 |
| 875 | unused hair back left d 8 | unused hair back left d 8 | unused hair back left d 7 | (0.795, 12.399, 0.735) | RM-C | 0 | unused hair back left d 9 |  |  |  |  | 0 | 0 |
| 876 | unused hair back left d 9 | unused hair back left d 9 | unused hair back left d 8 | (0.751, 11.837, 0.730) | RM-C | 0 | unused hair back left d 10 |  |  |  |  | 0 | 0 |
| 877 | unused hair back left d 10 | unused hair back left d 10 | unused hair back left d 9 | (0.700, 11.277, 0.721) | RM-C | 0 | (-0.05, -0.56, -0.01) |  |  |  |  | 0 | 0 |
| 878 | unused hair root back right h | unused hair root back right h | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right h 1 |  |  |  |  | 0 | 0 |
| 879 | unused hair back right h 1 | unused hair back right h 1 | unused hair root back right h | (-0.801, 15.595, 0.249) | RM-C | 0 | unused hair back right h 2 |  |  |  |  | 0 | 0 |
| 880 | unused hair back right h 2 | unused hair back right h 2 | unused hair back right h 1 | (-0.809, 15.130, 0.316) | RM-C | 0 | unused hair back right h 3 |  |  |  |  | 0 | 0 |
| 881 | unused hair back right h 3 | unused hair back right h 3 | unused hair back right h 2 | (-0.828, 14.603, 0.283) | RM-C | 0 | unused hair back right h 4 |  |  |  |  | 0 | 0 |
| 882 | unused hair back right h 4 | unused hair back right h 4 | unused hair back right h 3 | (-0.848, 14.030, 0.233) | RM-C | 0 | unused hair back right h 5 |  |  |  |  | 0 | 0 |
| 883 | unused hair back right h 5 | unused hair back right h 5 | unused hair back right h 4 | (-0.851, 13.485, 0.180) | RM-C | 0 | unused hair back right h 6 |  |  |  |  | 0 | 0 |
| 884 | unused hair back right h 6 | unused hair back right h 6 | unused hair back right h 5 | (-0.826, 12.937, 0.144) | RM-C | 0 | unused hair back right h 7 |  |  |  |  | 0 | 0 |
| 885 | unused hair back right h 7 | unused hair back right h 7 | unused hair back right h 6 | (-0.784, 12.397, 0.127) | RM-C | 0 | unused hair back right h 8 |  |  |  |  | 0 | 0 |
| 886 | unused hair back right h 8 | unused hair back right h 8 | unused hair back right h 7 | (-0.731, 11.834, 0.120) | RM-C | 0 | unused hair back right h 9 |  |  |  |  | 0 | 0 |
| 887 | unused hair back right h 9 | unused hair back right h 9 | unused hair back right h 8 | (-0.675, 11.277, 0.121) | RM-C | 0 | (0.06, -0.56, 0.00) |  |  |  |  | 0 | 0 |
| 888 | unused hair root back left h | unused hair root back left h | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left h 1 |  |  |  |  | 0 | 0 |
| 889 | unused hair back left h 1 | unused hair back left h 1 | unused hair root back left h | (0.801, 15.595, 0.249) | RM-C | 0 | unused hair back left h 2 |  |  |  |  | 0 | 0 |
| 890 | unused hair back left h 2 | unused hair back left h 2 | unused hair back left h 1 | (0.809, 15.130, 0.316) | RM-C | 0 | unused hair back left h 3 |  |  |  |  | 0 | 0 |
| 891 | unused hair back left h 3 | unused hair back left h 3 | unused hair back left h 2 | (0.828, 14.603, 0.283) | RM-C | 0 | unused hair back left h 4 |  |  |  |  | 0 | 0 |
| 892 | unused hair back left h 4 | unused hair back left h 4 | unused hair back left h 3 | (0.848, 14.030, 0.233) | RM-C | 0 | unused hair back left h 5 |  |  |  |  | 0 | 0 |
| 893 | unused hair back left h 5 | unused hair back left h 5 | unused hair back left h 4 | (0.851, 13.485, 0.180) | RM-C | 0 | unused hair back left h 6 |  |  |  |  | 0 | 0 |
| 894 | unused hair back left h 6 | unused hair back left h 6 | unused hair back left h 5 | (0.826, 12.937, 0.144) | RM-C | 0 | unused hair back left h 7 |  |  |  |  | 0 | 0 |
| 895 | unused hair back left h 7 | unused hair back left h 7 | unused hair back left h 6 | (0.784, 12.397, 0.127) | RM-C | 0 | unused hair back left h 8 |  |  |  |  | 0 | 0 |
| 896 | unused hair back left h 8 | unused hair back left h 8 | unused hair back left h 7 | (0.731, 11.834, 0.120) | RM-C | 0 | unused hair back left h 9 |  |  |  |  | 0 | 0 |
| 897 | unused hair back left h 9 | unused hair back left h 9 | unused hair back left h 8 | (0.675, 11.277, 0.121) | RM-C | 0 | (-0.06, -0.56, 0.00) |  |  |  |  | 0 | 0 |
| 898 | unused hair root back middle | unused hair root back middle | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back middle 1 |  |  |  |  | 0 | 0 |
| 899 | unused hair back middle 1 | unused hair back middle 1 | unused hair root back middle | (0.000, 16.080, 1.010) | RM-C | 0 | unused hair back middle 2 |  |  |  |  | 0 | 0 |
| 900 | unused hair back middle 2 | unused hair back middle 2 | unused hair back middle 1 | (-0.000, 15.631, 1.071) | RM-C | 0 | unused hair back middle 3 |  |  |  |  | 0 | 0 |
| 901 | unused hair back middle 3 | unused hair back middle 3 | unused hair back middle 2 | (0.000, 15.137, 1.070) | RM-C | 0 | unused hair back middle 4 |  |  |  |  | 0 | 0 |
| 902 | unused hair back middle 4 | unused hair back middle 4 | unused hair back middle 3 | (-0.000, 14.610, 1.067) | RM-C | 0 | unused hair back middle 5 |  |  |  |  | 0 | 0 |
| 903 | unused hair back middle 5 | unused hair back middle 5 | unused hair back middle 4 | (-0.000, 14.048, 1.070) | RM-C | 0 | unused hair back middle 6 |  |  |  |  | 0 | 0 |
| 904 | unused hair back middle 6 | unused hair back middle 6 | unused hair back middle 5 | (-0.000, 13.473, 1.070) | RM-C | 0 | unused hair back middle 7 |  |  |  |  | 0 | 0 |
| 905 | unused hair back middle 7 | unused hair back middle 7 | unused hair back middle 6 | (-0.000, 12.928, 1.066) | RM-C | 0 | unused hair back middle 8 |  |  |  |  | 0 | 0 |
| 906 | unused hair back middle 8 | unused hair back middle 8 | unused hair back middle 7 | (-0.000, 12.400, 1.060) | RM-C | 0 | unused hair back middle 9 |  |  |  |  | 0 | 0 |
| 907 | unused hair back middle 9 | unused hair back middle 9 | unused hair back middle 8 | (-0.000, 11.820, 1.047) | RM-C | 0 | unused hair back middle 10 |  |  |  |  | 0 | 0 |
| 908 | unused hair back middle 10 | unused hair back middle 10 | unused hair back middle 9 | (-0.000, 11.260, 1.022) | RM-C | 0 | (-0.00, -0.56, -0.02) |  |  |  |  | 0 | 0 |
| 909 | unused hair root back right c | unused hair root back right c | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right c 1 |  |  |  |  | 0 | 0 |
| 910 | unused hair back right c 1 | unused hair back right c 1 | unused hair root back right c | (-0.397, 16.089, 0.885) | RM-C | 0 | unused hair back right c 2 |  |  |  |  | 0 | 0 |
| 911 | unused hair back right c 2 | unused hair back right c 2 | unused hair back right c 1 | (-0.449, 15.642, 0.942) | RM-C | 0 | unused hair back right c 3 |  |  |  |  | 0 | 0 |
| 912 | unused hair back right c 3 | unused hair back right c 3 | unused hair back right c 2 | (-0.478, 15.144, 0.954) | RM-C | 0 | unused hair back right c 4 |  |  |  |  | 0 | 0 |
| 913 | unused hair back right c 4 | unused hair back right c 4 | unused hair back right c 3 | (-0.513, 14.612, 0.958) | RM-C | 0 | unused hair back right c 5 |  |  |  |  | 0 | 0 |
| 914 | unused hair back right c 5 | unused hair back right c 5 | unused hair back right c 4 | (-0.548, 14.053, 0.964) | RM-C | 0 | unused hair back right c 6 |  |  |  |  | 0 | 0 |
| 915 | unused hair back right c 6 | unused hair back right c 6 | unused hair back right c 5 | (-0.567, 13.481, 0.968) | RM-C | 0 | unused hair back right c 7 |  |  |  |  | 0 | 0 |
| 916 | unused hair back right c 7 | unused hair back right c 7 | unused hair back right c 6 | (-0.564, 12.936, 0.977) | RM-C | 0 | unused hair back right c 8 |  |  |  |  | 0 | 0 |
| 917 | unused hair back right c 8 | unused hair back right c 8 | unused hair back right c 7 | (-0.542, 12.400, 0.979) | RM-C | 0 | unused hair back right c 9 |  |  |  |  | 0 | 0 |
| 918 | unused hair back right c 9 | unused hair back right c 9 | unused hair back right c 8 | (-0.506, 11.825, 0.980) | RM-C | 0 | unused hair back right c 10 |  |  |  |  | 0 | 0 |
| 919 | unused hair back right c 10 | unused hair back right c 10 | unused hair back right c 9 | (-0.454, 11.274, 0.966) | RM-C | 0 | (0.05, -0.55, -0.01) |  |  |  |  | 0 | 0 |
| 920 | unused hair root back left c | unused hair root back left c | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left c 1 |  |  |  |  | 0 | 0 |
| 921 | unused hair back left c 1 | unused hair back left c 1 | unused hair root back left c | (0.397, 16.089, 0.885) | RM-C | 0 | unused hair back left c 2 |  |  |  |  | 0 | 0 |
| 922 | unused hair back left c 2 | unused hair back left c 2 | unused hair back left c 1 | (0.449, 15.642, 0.942) | RM-C | 0 | unused hair back left c 3 |  |  |  |  | 0 | 0 |
| 923 | unused hair back left c 3 | unused hair back left c 3 | unused hair back left c 2 | (0.478, 15.144, 0.954) | RM-C | 0 | unused hair back left c 4 |  |  |  |  | 0 | 0 |
| 924 | unused hair back left c 4 | unused hair back left c 4 | unused hair back left c 3 | (0.513, 14.612, 0.958) | RM-C | 0 | unused hair back left c 5 |  |  |  |  | 0 | 0 |
| 925 | unused hair back left c 5 | unused hair back left c 5 | unused hair back left c 4 | (0.548, 14.053, 0.964) | RM-C | 0 | unused hair back left c 6 |  |  |  |  | 0 | 0 |
| 926 | unused hair back left c 6 | unused hair back left c 6 | unused hair back left c 5 | (0.567, 13.481, 0.968) | RM-C | 0 | unused hair back left c 7 |  |  |  |  | 0 | 0 |
| 927 | unused hair back left c 7 | unused hair back left c 7 | unused hair back left c 6 | (0.564, 12.936, 0.977) | RM-C | 0 | unused hair back left c 8 |  |  |  |  | 0 | 0 |
| 928 | unused hair back left c 8 | unused hair back left c 8 | unused hair back left c 7 | (0.542, 12.400, 0.979) | RM-C | 0 | unused hair back left c 9 |  |  |  |  | 0 | 0 |
| 929 | unused hair back left c 9 | unused hair back left c 9 | unused hair back left c 8 | (0.506, 11.825, 0.980) | RM-C | 0 | unused hair back left c 10 |  |  |  |  | 0 | 0 |
| 930 | unused hair back left c 10 | unused hair back left c 10 | unused hair back left c 9 | (0.454, 11.274, 0.966) | RM-C | 0 | (-0.05, -0.55, -0.01) |  |  |  |  | 0 | 0 |
| 931 | unused hair root back right e | unused hair root back right e | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right e 1 |  |  |  |  | 0 | 0 |
| 932 | unused hair back right e 1 | unused hair back right e 1 | unused hair root back right e | (-0.663, 16.097, 0.606) | RM-C | 0 | unused hair back right e 2 |  |  |  |  | 0 | 0 |
| 933 | unused hair back right e 2 | unused hair back right e 2 | unused hair back right e 1 | (-0.744, 15.636, 0.659) | RM-C | 0 | unused hair back right e 3 |  |  |  |  | 0 | 0 |
| 934 | unused hair back right e 3 | unused hair back right e 3 | unused hair back right e 2 | (-0.766, 15.143, 0.668) | RM-C | 0 | unused hair back right e 4 |  |  |  |  | 0 | 0 |
| 935 | unused hair back right e 4 | unused hair back right e 4 | unused hair back right e 3 | (-0.789, 14.610, 0.668) | RM-C | 0 | unused hair back right e 5 |  |  |  |  | 0 | 0 |
| 936 | unused hair back right e 5 | unused hair back right e 5 | unused hair back right e 4 | (-0.801, 14.054, 0.669) | RM-C | 0 | unused hair back right e 6 |  |  |  |  | 0 | 0 |
| 937 | unused hair back right e 6 | unused hair back right e 6 | unused hair back right e 5 | (-0.804, 13.480, 0.668) | RM-C | 0 | unused hair back right e 7 |  |  |  |  | 0 | 0 |
| 938 | unused hair back right e 7 | unused hair back right e 7 | unused hair back right e 6 | (-0.789, 12.937, 0.666) | RM-C | 0 | unused hair back right e 8 |  |  |  |  | 0 | 0 |
| 939 | unused hair back right e 8 | unused hair back right e 8 | unused hair back right e 7 | (-0.758, 12.405, 0.663) | RM-C | 0 | unused hair back right e 9 |  |  |  |  | 0 | 0 |
| 940 | unused hair back right e 9 | unused hair back right e 9 | unused hair back right e 8 | (-0.702, 11.826, 0.658) | RM-C | 0 | unused hair back right e 10 |  |  |  |  | 0 | 0 |
| 941 | unused hair back right e 10 | unused hair back right e 10 | unused hair back right e 9 | (-0.635, 11.268, 0.649) | RM-C | 0 | (0.07, -0.56, -0.01) |  |  |  |  | 0 | 0 |
| 942 | unused hair root back left e | unused hair root back left e | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left e 1 |  |  |  |  | 0 | 0 |
| 943 | unused hair back left e 1 | unused hair back left e 1 | unused hair root back left e | (0.663, 16.097, 0.606) | RM-C | 0 | unused hair back left e 2 |  |  |  |  | 0 | 0 |
| 944 | unused hair back left e 2 | unused hair back left e 2 | unused hair back left e 1 | (0.744, 15.636, 0.659) | RM-C | 0 | unused hair back left e 3 |  |  |  |  | 0 | 0 |
| 945 | unused hair back left e 3 | unused hair back left e 3 | unused hair back left e 2 | (0.766, 15.143, 0.668) | RM-C | 0 | unused hair back left e 4 |  |  |  |  | 0 | 0 |
| 946 | unused hair back left e 4 | unused hair back left e 4 | unused hair back left e 3 | (0.789, 14.610, 0.668) | RM-C | 0 | unused hair back left e 5 |  |  |  |  | 0 | 0 |
| 947 | unused hair back left e 5 | unused hair back left e 5 | unused hair back left e 4 | (0.801, 14.054, 0.669) | RM-C | 0 | unused hair back left e 6 |  |  |  |  | 0 | 0 |
| 948 | unused hair back left e 6 | unused hair back left e 6 | unused hair back left e 5 | (0.804, 13.480, 0.668) | RM-C | 0 | unused hair back left e 7 |  |  |  |  | 0 | 0 |
| 949 | unused hair back left e 7 | unused hair back left e 7 | unused hair back left e 6 | (0.789, 12.937, 0.666) | RM-C | 0 | unused hair back left e 8 |  |  |  |  | 0 | 0 |
| 950 | unused hair back left e 8 | unused hair back left e 8 | unused hair back left e 7 | (0.758, 12.405, 0.663) | RM-C | 0 | unused hair back left e 9 |  |  |  |  | 0 | 0 |
| 951 | unused hair back left e 9 | unused hair back left e 9 | unused hair back left e 8 | (0.702, 11.826, 0.658) | RM-C | 0 | unused hair back left e 10 |  |  |  |  | 0 | 0 |
| 952 | unused hair back left e 10 | unused hair back left e 10 | unused hair back left e 9 | (0.635, 11.268, 0.649) | RM-C | 0 | (-0.07, -0.56, -0.01) |  |  |  |  | 0 | 0 |
| 953 | unused hair root back left b | unused hair root back left b | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left b 1 |  |  |  |  | 0 | 0 |
| 954 | unused hair back left b 1 | unused hair back left b 1 | unused hair root back left b | (0.332, 15.361, 0.959) | RM-C | 0 | unused hair back left b 2 |  |  |  |  | 0 | 0 |
| 955 | unused hair back left b 2 | unused hair back left b 2 | unused hair back left b 1 | (0.325, 14.815, 0.940) | RM-C | 0 | unused hair back left b 3 |  |  |  |  | 0 | 0 |
| 956 | unused hair back left b 3 | unused hair back left b 3 | unused hair back left b 2 | (0.317, 14.205, 0.923) | RM-C | 0 | unused hair back left b 4 |  |  |  |  | 0 | 0 |
| 957 | unused hair back left b 4 | unused hair back left b 4 | unused hair back left b 3 | (0.305, 13.636, 0.907) | RM-C | 0 | unused hair back left b 5 |  |  |  |  | 0 | 0 |
| 958 | unused hair back left b 5 | unused hair back left b 5 | unused hair back left b 4 | (0.289, 13.036, 0.891) | RM-C | 0 | unused hair back left b 6 |  |  |  |  | 0 | 0 |
| 959 | unused hair back left b 6 | unused hair back left b 6 | unused hair back left b 5 | (0.267, 12.476, 0.870) | RM-C | 0 | unused hair back left b 7 |  |  |  |  | 0 | 0 |
| 960 | unused hair back left b 7 | unused hair back left b 7 | unused hair back left b 6 | (0.244, 11.880, 0.848) | RM-C | 0 | unused hair back left b 8 |  |  |  |  | 0 | 0 |
| 961 | unused hair back left b 8 | unused hair back left b 8 | unused hair back left b 7 | (0.216, 11.291, 0.819) | RM-C | 0 | (-0.03, -0.59, -0.03) |  |  |  |  | 0 | 0 |
| 962 | unused hair root back right b | unused hair root back right b | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right b 1 |  |  |  |  | 0 | 0 |
| 963 | unused hair back right b 1 | unused hair back right b 1 | unused hair root back right b | (-0.332, 15.361, 0.959) | RM-C | 0 | unused hair back right b 2 |  |  |  |  | 0 | 0 |
| 964 | unused hair back right b 2 | unused hair back right b 2 | unused hair back right b 1 | (-0.325, 14.815, 0.940) | RM-C | 0 | unused hair back right b 3 |  |  |  |  | 0 | 0 |
| 965 | unused hair back right b 3 | unused hair back right b 3 | unused hair back right b 2 | (-0.317, 14.205, 0.923) | RM-C | 0 | unused hair back right b 4 |  |  |  |  | 0 | 0 |
| 966 | unused hair back right b 4 | unused hair back right b 4 | unused hair back right b 3 | (-0.305, 13.636, 0.907) | RM-C | 0 | unused hair back right b 5 |  |  |  |  | 0 | 0 |
| 967 | unused hair back right b 5 | unused hair back right b 5 | unused hair back right b 4 | (-0.289, 13.036, 0.891) | RM-C | 0 | unused hair back right b 6 |  |  |  |  | 0 | 0 |
| 968 | unused hair back right b 6 | unused hair back right b 6 | unused hair back right b 5 | (-0.267, 12.476, 0.870) | RM-C | 0 | unused hair back right b 7 |  |  |  |  | 0 | 0 |
| 969 | unused hair back right b 7 | unused hair back right b 7 | unused hair back right b 6 | (-0.244, 11.880, 0.848) | RM-C | 0 | unused hair back right b 8 |  |  |  |  | 0 | 0 |
| 970 | unused hair back right b 8 | unused hair back right b 8 | unused hair back right b 7 | (-0.216, 11.291, 0.819) | RM-C | 0 | (0.03, -0.59, -0.03) |  |  |  |  | 0 | 0 |
| 971 | unused hair root back left f | unused hair root back left f | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left f 1 |  |  |  |  | 0 | 0 |
| 972 | unused hair back left f 1 | unused hair back left f 1 | unused hair root back left f | (0.666, 15.363, 0.655) | RM-C | 0 | unused hair back left f 2 |  |  |  |  | 0 | 0 |
| 973 | unused hair back left f 2 | unused hair back left f 2 | unused hair back left f 1 | (0.653, 14.815, 0.643) | RM-C | 0 | unused hair back left f 3 |  |  |  |  | 0 | 0 |
| 974 | unused hair back left f 3 | unused hair back left f 3 | unused hair back left f 2 | (0.636, 14.205, 0.627) | RM-C | 0 | unused hair back left f 4 |  |  |  |  | 0 | 0 |
| 975 | unused hair back left f 4 | unused hair back left f 4 | unused hair back left f 3 | (0.617, 13.635, 0.617) | RM-C | 0 | unused hair back left f 5 |  |  |  |  | 0 | 0 |
| 976 | unused hair back left f 5 | unused hair back left f 5 | unused hair back left f 4 | (0.590, 13.036, 0.605) | RM-C | 0 | unused hair back left f 6 |  |  |  |  | 0 | 0 |
| 977 | unused hair back left f 6 | unused hair back left f 6 | unused hair back left f 5 | (0.558, 12.475, 0.594) | RM-C | 0 | unused hair back left f 7 |  |  |  |  | 0 | 0 |
| 978 | unused hair back left f 7 | unused hair back left f 7 | unused hair back left f 6 | (0.524, 11.879, 0.585) | RM-C | 0 | unused hair back left f 8 |  |  |  |  | 0 | 0 |
| 979 | unused hair back left f 8 | unused hair back left f 8 | unused hair back left f 7 | (0.487, 11.291, 0.572) | RM-C | 0 | (-0.04, -0.59, -0.01) |  |  |  |  | 0 | 0 |
| 980 | unused hair root back right f | unused hair root back right f | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right f 1 |  |  |  |  | 0 | 0 |
| 981 | unused hair back right f 1 | unused hair back right f 1 | unused hair root back right f | (-0.666, 15.363, 0.655) | RM-C | 0 | unused hair back right f 2 |  |  |  |  | 0 | 0 |
| 982 | unused hair back right f 2 | unused hair back right f 2 | unused hair back right f 1 | (-0.653, 14.815, 0.643) | RM-C | 0 | unused hair back right f 3 |  |  |  |  | 0 | 0 |
| 983 | unused hair back right f 3 | unused hair back right f 3 | unused hair back right f 2 | (-0.636, 14.205, 0.627) | RM-C | 0 | unused hair back right f 4 |  |  |  |  | 0 | 0 |
| 984 | unused hair back right f 4 | unused hair back right f 4 | unused hair back right f 3 | (-0.617, 13.635, 0.617) | RM-C | 0 | unused hair back right f 5 |  |  |  |  | 0 | 0 |
| 985 | unused hair back right f 5 | unused hair back right f 5 | unused hair back right f 4 | (-0.590, 13.036, 0.605) | RM-C | 0 | unused hair back right f 6 |  |  |  |  | 0 | 0 |
| 986 | unused hair back right f 6 | unused hair back right f 6 | unused hair back right f 5 | (-0.558, 12.475, 0.594) | RM-C | 0 | unused hair back right f 7 |  |  |  |  | 0 | 0 |
| 987 | unused hair back right f 7 | unused hair back right f 7 | unused hair back right f 6 | (-0.524, 11.879, 0.585) | RM-C | 0 | unused hair back right f 8 |  |  |  |  | 0 | 0 |
| 988 | unused hair back right f 8 | unused hair back right f 8 | unused hair back right f 7 | (-0.487, 11.291, 0.572) | RM-C | 0 | (0.04, -0.59, -0.01) |  |  |  |  | 0 | 0 |
| 989 | unused hair root back left g | unused hair root back left g | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back left g 1 |  |  |  |  | 0 | 0 |
| 990 | unused hair back left g 1 | unused hair back left g 1 | unused hair root back left g | (0.768, 15.349, 0.393) | RM-C | 0 | unused hair back left g 2 |  |  |  |  | 0 | 0 |
| 991 | unused hair back left g 2 | unused hair back left g 2 | unused hair back left g 1 | (0.775, 14.813, 0.390) | RM-C | 0 | unused hair back left g 3 |  |  |  |  | 0 | 0 |
| 992 | unused hair back left g 3 | unused hair back left g 3 | unused hair back left g 2 | (0.782, 14.205, 0.380) | RM-C | 0 | unused hair back left g 4 |  |  |  |  | 0 | 0 |
| 993 | unused hair back left g 4 | unused hair back left g 4 | unused hair back left g 3 | (0.781, 13.636, 0.371) | RM-C | 0 | unused hair back left g 5 |  |  |  |  | 0 | 0 |
| 994 | unused hair back left g 5 | unused hair back left g 5 | unused hair back left g 4 | (0.758, 13.036, 0.358) | RM-C | 0 | unused hair back left g 6 |  |  |  |  | 0 | 0 |
| 995 | unused hair back left g 6 | unused hair back left g 6 | unused hair back left g 5 | (0.720, 12.476, 0.348) | RM-C | 0 | unused hair back left g 7 |  |  |  |  | 0 | 0 |
| 996 | unused hair back left g 7 | unused hair back left g 7 | unused hair back left g 6 | (0.680, 11.880, 0.334) | RM-C | 0 | unused hair back left g 8 |  |  |  |  | 0 | 0 |
| 997 | unused hair back left g 8 | unused hair back left g 8 | unused hair back left g 7 | (0.629, 11.291, 0.319) | RM-C | 0 | (-0.05, -0.59, -0.01) |  |  |  |  | 0 | 0 |
| 998 | unused hair root back right g | unused hair root back right g | unused hair root | (-0.000, 14.871, 0.062) | RM-C | 0 | unused hair back right g 1 |  |  |  |  | 0 | 0 |
| 999 | unused hair back right g 1 | unused hair back right g 1 | unused hair root back right g | (-0.768, 15.349, 0.393) | RM-C | 0 | unused hair back right g 2 |  |  |  |  | 0 | 0 |
| 1000 | unused hair back right g 2 | unused hair back right g 2 | unused hair back right g 1 | (-0.775, 14.813, 0.390) | RM-C | 0 | unused hair back right g 3 |  |  |  |  | 0 | 0 |
| 1001 | unused hair back right g 3 | unused hair back right g 3 | unused hair back right g 2 | (-0.782, 14.205, 0.380) | RM-C | 0 | unused hair back right g 4 |  |  |  |  | 0 | 0 |
| 1002 | unused hair back right g 4 | unused hair back right g 4 | unused hair back right g 3 | (-0.781, 13.636, 0.371) | RM-C | 0 | unused hair back right g 5 |  |  |  |  | 0 | 0 |
| 1003 | unused hair back right g 5 | unused hair back right g 5 | unused hair back right g 4 | (-0.758, 13.036, 0.358) | RM-C | 0 | unused hair back right g 6 |  |  |  |  | 0 | 0 |
| 1004 | unused hair back right g 6 | unused hair back right g 6 | unused hair back right g 5 | (-0.720, 12.476, 0.348) | RM-C | 0 | unused hair back right g 7 |  |  |  |  | 0 | 0 |
| 1005 | unused hair back right g 7 | unused hair back right g 7 | unused hair back right g 6 | (-0.680, 11.880, 0.334) | RM-C | 0 | unused hair back right g 8 |  |  |  |  | 0 | 0 |
| 1006 | unused hair back right g 8 | unused hair back right g 8 | unused hair back right g 7 | (-0.629, 11.291, 0.319) | RM-C | 0 | (0.05, -0.59, -0.01) |  |  |  |  | 0 | 0 |
| 1007 | unused glasses | unused glasses | 頭 | (-0.000, 14.861, 0.072) | RM-C | 0 | (-0.00, -0.02, -0.05) |  |  |  |  | 0 | 0 |
| 1008 | unused arm left shoulder 1 | unused arm left shoulder 1 | 上半身2 | (0.666, 13.839, 0.265) | RM-C | 0 | unused arm left shoulder 2 |  |  |  |  | 0 | 0 |
| 1009 | unused arm left shoulder 2 | unused arm left shoulder 2 | unused arm left shoulder 1 | (1.212, 13.839, 0.265) | RM-C | 0 | (0.85, -0.85, 0.00) |  |  |  |  | 0 | 0 |
| 1010 | unused arm left elbow | unused arm left elbow | unused arm left shoulder 2 | (2.909, 12.142, 0.265) | RM-C | 0 | (0.84, -0.84, 0.00) |  |  |  |  | 0 | 0 |
| 1011 | unused arm left wrist | unused arm left wrist | unused arm left elbow | (4.592, 10.459, 0.265) | RM-C | 0 | unused ctr arm left wrist 1 |  |  |  |  | 0 | 0 |
| 1012 | unused ctr arm left wrist 1 | unused ctr arm left wrist 1 | unused arm left wrist | (4.592, 10.459, 0.265) | RM-C | 0 | (0.29, -0.21, -0.16) |  |  |  |  | 0 | 0 |
| 1013 | unused arm left finger 2a | unused arm left finger 2a | unused ctr arm left wrist 1 | (5.181, 10.050, -0.020) | RM-C | 0 | unused arm left finger 2b |  |  |  |  | 0 | 0 |
| 1014 | unused arm left finger 2b | unused arm left finger 2b | unused arm left finger 2a | (5.412, 9.819, -0.054) | RM-C | 0 | unused arm left finger 2c |  |  |  |  | 0 | 0 |
| 1015 | unused arm left finger 2c | unused arm left finger 2c | unused arm left finger 2b | (5.555, 9.676, -0.075) | RM-C | 0 | (0.14, -0.14, -0.02) |  |  |  |  | 0 | 0 |
| 1016 | unused ctr arm left wrist 2 | unused ctr arm left wrist 2 | unused ctr arm left wrist 1 | (4.514, 10.592, 0.235) | RM-C | 0 | (0.62, -0.54, 0.26) |  |  |  |  | 0 | 0 |
| 1017 | unused arm left finger 5a | unused arm left finger 5a | unused ctr arm left wrist 2 | (5.105, 10.049, 0.577) | RM-C | 0 | unused arm left finger 5b |  |  |  |  | 0 | 0 |
| 1018 | unused arm left finger 5b | unused arm left finger 5b | unused arm left finger 5a | (5.278, 9.869, 0.633) | RM-C | 0 | unused arm left finger 5c |  |  |  |  | 0 | 0 |
| 1019 | unused arm left finger 5c | unused arm left finger 5c | unused arm left finger 5b | (5.388, 9.755, 0.669) | RM-C | 0 | (0.11, -0.11, 0.04) |  |  |  |  | 0 | 0 |
| 1020 | unused arm left finger 4a | unused arm left finger 4a | unused ctr arm left wrist 2 | (5.170, 10.050, 0.404) | RM-C | 0 | unused arm left finger 4b |  |  |  |  | 0 | 0 |
| 1021 | unused arm left finger 4b | unused arm left finger 4b | unused arm left finger 4a | (5.393, 9.827, 0.435) | RM-C | 0 | unused arm left finger 4c |  |  |  |  | 0 | 0 |
| 1022 | unused arm left finger 4c | unused arm left finger 4c | unused arm left finger 4b | (5.546, 9.674, 0.456) | RM-C | 0 | (0.15, -0.15, 0.02) |  |  |  |  | 0 | 0 |
| 1023 | unused arm left finger 3a | unused arm left finger 3a | unused ctr arm left wrist 1 | (5.216, 10.050, 0.191) | RM-C | 0 | unused arm left finger 3b |  |  |  |  | 0 | 0 |
| 1024 | unused arm left finger 3b | unused arm left finger 3b | unused arm left finger 3a | (5.467, 9.799, 0.191) | RM-C | 0 | unused arm left finger 3c |  |  |  |  | 0 | 0 |
| 1025 | unused arm left finger 3c | unused arm left finger 3c | unused arm left finger 3b | (5.621, 9.645, 0.191) | RM-C | 0 | (0.15, -0.15, 0.00) |  |  |  |  | 0 | 0 |
| 1026 | unused arm left finger 1a | unused arm left finger 1a | unused ctr arm left wrist 1 | (4.627, 10.298, 0.016) | RM-C | 0 | unused arm left finger 1b |  |  |  |  | 0 | 0 |
| 1027 | unused arm left finger 1b | unused arm left finger 1b | unused arm left finger 1a | (4.654, 9.992, -0.161) | RM-C | 0 | unused arm left finger 1c |  |  |  |  | 0 | 0 |
| 1028 | unused arm left finger 1c | unused arm left finger 1c | unused arm left finger 1b | (4.676, 9.742, -0.306) | RM-C | 0 | (0.02, -0.25, -0.14) |  |  |  |  | 0 | 0 |
| 1029 | unused ctr arm left elbow 1 | unused ctr arm left elbow 1 | unused arm left elbow | (2.909, 12.142, 0.275) | RM-C | 0 | (0.00, 0.00, 0.01) |  |  |  |  | 0 | 0 |
| 1030 | unused ctr arm left elbow 2 | unused ctr arm left elbow 2 | unused arm left elbow | (3.470, 11.581, 0.265) | RM-C | 0 | (0.56, -0.56, 0.00) |  |  |  |  | 0 | 0 |
| 1031 | unused ctr arm left elbow 3 | unused ctr arm left elbow 3 | unused arm left elbow | (4.031, 11.020, 0.265) | RM-C | 0 | (1.12, -1.12, 0.00) |  |  |  |  | 0 | 0 |
| 1032 | unused ctr arm left shoulder 1 | unused ctr arm left shoulder 1 | unused arm left shoulder 2 | (1.213, 13.838, 0.265) | RM-C | 0 | (0.00, -0.00, -0.00) |  |  |  |  | 0 | 0 |
| 1033 | unused ctr arm left shoulder 2 | unused ctr arm left shoulder 2 | unused arm left shoulder 2 | (2.061, 12.990, 0.265) | RM-C | 0 | (0.85, -0.85, 0.00) |  |  |  |  | 0 | 0 |
| 1034 | unused arm right shoulder 1 | unused arm right shoulder 1 | 上半身2 | (-0.666, 13.839, 0.265) | RM-C | 0 | unused arm right shoulder 2 |  |  |  |  | 0 | 0 |
| 1035 | unused arm right shoulder 2 | unused arm right shoulder 2 | unused arm right shoulder 1 | (-1.212, 13.839, 0.265) | RM-C | 0 | (-0.85, -0.85, 0.00) |  |  |  |  | 0 | 0 |
| 1036 | unused arm right elbow | unused arm right elbow | unused arm right shoulder 2 | (-2.909, 12.142, 0.265) | RM-C | 0 | (-0.84, -0.84, 0.00) |  |  |  |  | 0 | 0 |
| 1037 | unused arm right wrist | unused arm right wrist | unused arm right elbow | (-4.592, 10.459, 0.265) | RM-C | 0 | unused ctr arm right wrist 1 |  |  |  |  | 0 | 0 |
| 1038 | unused ctr arm right wrist 1 | unused ctr arm right wrist 1 | unused arm right wrist | (-4.592, 10.459, 0.265) | RM-C | 0 | (-0.29, -0.21, -0.16) |  |  |  |  | 0 | 0 |
| 1039 | unused arm right finger 2a | unused arm right finger 2a | unused ctr arm right wrist 1 | (-5.181, 10.050, -0.020) | RM-C | 0 | unused arm right finger 2b |  |  |  |  | 0 | 0 |
| 1040 | unused arm right finger 2b | unused arm right finger 2b | unused arm right finger 2a | (-5.412, 9.819, -0.054) | RM-C | 0 | unused arm right finger 2c |  |  |  |  | 0 | 0 |
| 1041 | unused arm right finger 2c | unused arm right finger 2c | unused arm right finger 2b | (-5.555, 9.676, -0.075) | RM-C | 0 | (-0.14, -0.14, -0.02) |  |  |  |  | 0 | 0 |
| 1042 | unused ctr arm right wrist 2 | unused ctr arm right wrist 2 | unused ctr arm right wrist 1 | (-4.514, 10.592, 0.235) | RM-C | 0 | (-0.62, -0.54, 0.26) |  |  |  |  | 0 | 0 |
| 1043 | unused arm right finger 5a | unused arm right finger 5a | unused ctr arm right wrist 2 | (-5.105, 10.049, 0.577) | RM-C | 0 | unused arm right finger 5b |  |  |  |  | 0 | 0 |
| 1044 | unused arm right finger 5b | unused arm right finger 5b | unused arm right finger 5a | (-5.278, 9.869, 0.633) | RM-C | 0 | unused arm right finger 5c |  |  |  |  | 0 | 0 |
| 1045 | unused arm right finger 5c | unused arm right finger 5c | unused arm right finger 5b | (-5.388, 9.755, 0.669) | RM-C | 0 | (-0.11, -0.11, 0.04) |  |  |  |  | 0 | 0 |
| 1046 | unused arm right finger 4a | unused arm right finger 4a | unused ctr arm right wrist 2 | (-5.170, 10.050, 0.404) | RM-C | 0 | unused arm right finger 4b |  |  |  |  | 0 | 0 |
| 1047 | unused arm right finger 4b | unused arm right finger 4b | unused arm right finger 4a | (-5.393, 9.827, 0.435) | RM-C | 0 | unused arm right finger 4c |  |  |  |  | 0 | 0 |
| 1048 | unused arm right finger 4c | unused arm right finger 4c | unused arm right finger 4b | (-5.546, 9.674, 0.456) | RM-C | 0 | (-0.15, -0.15, 0.02) |  |  |  |  | 0 | 0 |
| 1049 | unused arm right finger 3a | unused arm right finger 3a | unused ctr arm right wrist 1 | (-5.216, 10.050, 0.191) | RM-C | 0 | unused arm right finger 3b |  |  |  |  | 0 | 0 |
| 1050 | unused arm right finger 3b | unused arm right finger 3b | unused arm right finger 3a | (-5.467, 9.799, 0.191) | RM-C | 0 | unused arm right finger 3c |  |  |  |  | 0 | 0 |
| 1051 | unused arm right finger 3c | unused arm right finger 3c | unused arm right finger 3b | (-5.621, 9.645, 0.191) | RM-C | 0 | (-0.15, -0.15, 0.00) |  |  |  |  | 0 | 0 |
| 1052 | unused arm right finger 1a | unused arm right finger 1a | unused ctr arm right wrist 1 | (-4.627, 10.298, 0.016) | RM-C | 0 | unused arm right finger 1b |  |  |  |  | 0 | 0 |
| 1053 | unused arm right finger 1b | unused arm right finger 1b | unused arm right finger 1a | (-4.654, 9.992, -0.161) | RM-C | 0 | unused arm right finger 1c |  |  |  |  | 0 | 0 |
| 1054 | unused arm right finger 1c | unused arm right finger 1c | unused arm right finger 1b | (-4.676, 9.742, -0.306) | RM-C | 0 | (-0.02, -0.25, -0.14) |  |  |  |  | 0 | 0 |
| 1055 | unused ctr arm right elbow 1 | unused ctr arm right elbow 1 | unused arm right elbow | (-2.909, 12.142, 0.275) | RM-C | 0 | (0.00, 0.00, 0.01) |  |  |  |  | 0 | 0 |
| 1056 | unused ctr arm right elbow 2 | unused ctr arm right elbow 2 | unused arm right elbow | (-3.470, 11.581, 0.265) | RM-C | 0 | (-0.56, -0.56, 0.00) |  |  |  |  | 0 | 0 |
| 1057 | unused ctr arm right elbow 3 | unused ctr arm right elbow 3 | unused arm right elbow | (-4.031, 11.020, 0.265) | RM-C | 0 | (-1.12, -1.12, 0.00) |  |  |  |  | 0 | 0 |
| 1058 | unused ctr arm right shoulder 1 | unused ctr arm right shoulder 1 | unused arm right shoulder 2 | (-1.213, 13.838, 0.265) | RM-C | 0 | (-0.00, -0.00, -0.00) |  |  |  |  | 0 | 0 |
| 1059 | unused ctr arm right shoulder 2 | unused ctr arm right shoulder 2 | unused arm right shoulder 2 | (-2.061, 12.990, 0.265) | RM-C | 0 | (-0.85, -0.85, 0.00) |  |  |  |  | 0 | 0 |
| 1060 | unused breast left base | unused breast left base | 上半身2 | (0.550, 12.803, -0.549) | RM-C | 0 | unused breast left tip |  |  |  |  | 0 | 0 |
| 1061 | unused breast left tip | unused breast left tip | unused breast left base | (0.797, 12.803, -1.383) | RM-C | 0 | (-0.14, 0.29, 0.49) |  |  |  |  | 0 | 0 |
| 1062 | unused breast left 1 | unused breast left 1 | unused breast left tip | (0.072, 12.803, -1.067) | RM-C | 0 | (-0.72, 0.00, 0.32) |  |  |  |  | 0 | 0 |
| 1063 | unused breast left 2 | unused breast left 2 | unused breast left tip | (0.242, 13.231, -1.017) | RM-C | 0 | (-0.55, 0.43, 0.37) |  |  |  |  | 0 | 0 |
| 1064 | unused breast left 3 | unused breast left 3 | unused breast left tip | (0.653, 13.408, -0.895) | RM-C | 0 | (-0.14, 0.60, 0.49) |  |  |  |  | 0 | 0 |
| 1065 | unused breast left 4 | unused breast left 4 | unused breast left tip | (1.063, 13.231, -0.774) | RM-C | 0 | (0.27, 0.43, 0.61) |  |  |  |  | 0 | 0 |
| 1066 | unused breast left 5 | unused breast left 5 | unused breast left tip | (1.233, 12.803, -0.724) | RM-C | 0 | (0.44, 0.00, 0.66) |  |  |  |  | 0 | 0 |
| 1067 | unused breast right base | unused breast right base | 上半身2 | (-0.550, 12.803, -0.549) | RM-C | 0 | unused breast right tip |  |  |  |  | 0 | 0 |
| 1068 | unused breast right tip | unused breast right tip | unused breast right base | (-0.797, 12.803, -1.383) | RM-C | 0 | (0.14, 0.29, 0.49) |  |  |  |  | 0 | 0 |
| 1069 | unused breast right 1 | unused breast right 1 | unused breast right tip | (-0.072, 12.803, -1.067) | RM-C | 0 | (0.72, 0.00, 0.32) |  |  |  |  | 0 | 0 |
| 1070 | unused breast right 2 | unused breast right 2 | unused breast right tip | (-0.242, 13.231, -1.017) | RM-C | 0 | (0.55, 0.43, 0.37) |  |  |  |  | 0 | 0 |
| 1071 | unused breast right 3 | unused breast right 3 | unused breast right tip | (-0.653, 13.408, -0.895) | RM-C | 0 | (0.14, 0.61, 0.49) |  |  |  |  | 0 | 0 |
| 1072 | unused breast right 4 | unused breast right 4 | unused breast right tip | (-1.063, 13.231, -0.774) | RM-C | 0 | (-0.27, 0.43, 0.61) |  |  |  |  | 0 | 0 |
| 1073 | unused breast right 5 | unused breast right 5 | unused breast right tip | (-1.233, 12.803, -0.724) | RM-C | 0 | (-0.44, 0.00, 0.66) |  |  |  |  | 0 | 0 |
| 1074 | unused ribbon front root | unused ribbon front root | 上半身2 | (0.000, 10.000, -0.000) | RM-C | 0 | (0.00, 1.88, -1.03) |  |  |  |  | 0 | 0 |
| 1075 | unused ribbon front c 1 | unused ribbon front c 1 | unused ribbon front root | (0.151, 11.884, -1.026) | RM-C | 0 | unused ribbon front c 2 |  |  |  |  | 0 | 0 |
| 1076 | unused ribbon front c 2 | unused ribbon front c 2 | unused ribbon front c 1 | (0.151, 11.653, -1.026) | RM-C | 0 | unused ribbon front c 3 |  |  |  |  | 0 | 0 |
| 1077 | unused ribbon front c 3 | unused ribbon front c 3 | unused ribbon front c 2 | (0.151, 11.421, -1.026) | RM-C | 0 | unused ribbon front c 4 |  |  |  |  | 0 | 0 |
| 1078 | unused ribbon front c 4 | unused ribbon front c 4 | unused ribbon front c 3 | (0.151, 11.190, -1.026) | RM-C | 0 | unused ribbon front c 5 |  |  |  |  | 0 | 0 |
| 1079 | unused ribbon front c 5 | unused ribbon front c 5 | unused ribbon front c 4 | (0.151, 10.959, -1.026) | RM-C | 0 | unused ribbon front c 6 |  |  |  |  | 0 | 0 |
| 1080 | unused ribbon front c 6 | unused ribbon front c 6 | unused ribbon front c 5 | (0.151, 10.727, -1.026) | RM-C | 0 | unused ribbon front c 7 |  |  |  |  | 0 | 0 |
| 1081 | unused ribbon front c 7 | unused ribbon front c 7 | unused ribbon front c 6 | (0.151, 10.496, -1.026) | RM-C | 0 | (0.00, -0.23, 0.00) |  |  |  |  | 0 | 0 |
| 1082 | unused ribbon front a 1 | unused ribbon front a 1 | unused ribbon front root | (-0.151, 11.884, -1.026) | RM-C | 0 | unused ribbon front a 2 |  |  |  |  | 0 | 0 |
| 1083 | unused ribbon front a 2 | unused ribbon front a 2 | unused ribbon front a 1 | (-0.151, 11.653, -1.026) | RM-C | 0 | unused ribbon front a 3 |  |  |  |  | 0 | 0 |
| 1084 | unused ribbon front a 3 | unused ribbon front a 3 | unused ribbon front a 2 | (-0.151, 11.421, -1.026) | RM-C | 0 | unused ribbon front a 4 |  |  |  |  | 0 | 0 |
| 1085 | unused ribbon front a 4 | unused ribbon front a 4 | unused ribbon front a 3 | (-0.151, 11.190, -1.026) | RM-C | 0 | unused ribbon front a 5 |  |  |  |  | 0 | 0 |
| 1086 | unused ribbon front a 5 | unused ribbon front a 5 | unused ribbon front a 4 | (-0.151, 10.959, -1.026) | RM-C | 0 | unused ribbon front a 6 |  |  |  |  | 0 | 0 |
| 1087 | unused ribbon front a 6 | unused ribbon front a 6 | unused ribbon front a 5 | (-0.151, 10.727, -1.026) | RM-C | 0 | unused ribbon front a 7 |  |  |  |  | 0 | 0 |
| 1088 | unused ribbon front a 7 | unused ribbon front a 7 | unused ribbon front a 6 | (-0.151, 10.496, -1.026) | RM-C | 0 | (0.00, -0.23, 0.00) |  |  |  |  | 0 | 0 |
| 1089 | unused ribbon front b 1 | unused ribbon front b 1 | unused ribbon front root | (0.000, 11.884, -1.026) | RM-C | 0 | unused ribbon front b 2 |  |  |  |  | 0 | 0 |
| 1090 | unused ribbon front b 2 | unused ribbon front b 2 | unused ribbon front b 1 | (0.000, 11.653, -1.026) | RM-C | 0 | unused ribbon front b 3 |  |  |  |  | 0 | 0 |
| 1091 | unused ribbon front b 3 | unused ribbon front b 3 | unused ribbon front b 2 | (0.000, 11.421, -1.026) | RM-C | 0 | unused ribbon front b 4 |  |  |  |  | 0 | 0 |
| 1092 | unused ribbon front b 4 | unused ribbon front b 4 | unused ribbon front b 3 | (0.000, 11.190, -1.026) | RM-C | 0 | unused ribbon front b 5 |  |  |  |  | 0 | 0 |
| 1093 | unused ribbon front b 5 | unused ribbon front b 5 | unused ribbon front b 4 | (0.000, 10.959, -1.026) | RM-C | 0 | unused ribbon front b 6 |  |  |  |  | 0 | 0 |
| 1094 | unused ribbon front b 6 | unused ribbon front b 6 | unused ribbon front b 5 | (0.000, 10.727, -1.026) | RM-C | 0 | unused ribbon front b 7 |  |  |  |  | 0 | 0 |
| 1095 | unused ribbon front b 7 | unused ribbon front b 7 | unused ribbon front b 6 | (0.000, 10.496, -1.026) | RM-C | 0 | (0.00, -0.23, 0.00) |  |  |  |  | 0 | 0 |
| 1096 |  |  | - | (0.000, 0.000, 0.000) | RMVC | 0 | (0.00, 0.00, 0.00) |  |  |  |  | 0 | 0 |
| 1097 |  |  | - | (0.000, 0.000, 0.000) | RMVC | 0 | (0.00, 0.00, 0.00) |  |  |  |  | 0 | 0 |
| 1098 | 左つま先ＩＫ | toe IK_L |  | (3.217, 0.463, -0.814) | RMVC,IK | 1 | (0.00, -1.00, 0.00) |  |  |  | T=- loop=0 unit=57.30° links:  | 0 | 0 |
| 1099 | 右つま先ＩＫ | toe IK_R |  | (-3.217, 0.463, -0.814) | RMVC,IK | 1 | (0.00, -1.00, 0.00) |  |  |  | T=- loop=0 unit=57.30° links:  | 0 | 0 |

Standard/semi-standard presence: 全ての親:Y, センター:Y, グルーブ:-, 腰:-, 上半身:Y, 上半身1:-, 上半身2:Y, 上半身3:-, 下半身:-, 首:Y, 首1:-, 頭:Y, 両目:-, 左目:Y, 右目:Y, 操作中心:-, 左肩P:-, 右肩P:-, 左肩:Y, 右肩:Y, 左肩C:-, 右肩C:-, 左腕:Y, 右腕:Y, 左腕捩:-, 右腕捩:-, 左腕捩1:-, 右腕捩1:-, 左腕捩2:-, 右腕捩2:-, 左腕捩3:-, 右腕捩3:-, 左ひじ:Y, 右ひじ:Y, 左手捩:-, 右手捩:-, 左手捩1:-, 右手捩1:-, 左手捩2:-, 右手捩2:-, 左手捩3:-, 右手捩3:-, 左手首:Y, 右手首:Y, 左ダミー:-, 右ダミー:-, 左親指０:Y, 右親指０:Y, 左親指１:Y, 右親指１:Y, 左親指２:Y, 右親指２:Y, 左人指１:Y, 右人指１:Y, 左人指２:Y, 右人指２:Y, 左人指３:Y, 右人指３:Y, 左中指１:Y, 右中指１:Y, 左中指２:Y, 右中指２:Y, 左中指３:Y, 右中指３:Y, 左薬指１:Y, 右薬指１:Y, 左薬指２:Y, 右薬指２:Y, 左薬指３:Y, 右薬指３:Y, 左小指１:Y, 右小指１:Y, 左小指２:Y, 右小指２:Y, 左小指３:Y, 右小指３:Y, 左足:Y, 右足:Y, 左ひざ:Y, 右ひざ:Y, 左足首:-, 右足首:-, 左つま先:Y, 右つま先:Y, 左足D:-, 右足D:-, 左ひざD:-, 右ひざD:-, 左足首D:-, 右足首D:-, 左足先EX:-, 右足先EX:-, 腰キャンセル左:-, 腰キャンセル右:-, 左足IK親:-, 右足IK親:-, 左足ＩＫ:-, 右足ＩＫ:-, 左つま先ＩＫ:Y, 右つま先ＩＫ:Y

## 5. Weights
weight types: BDEF1=0 BDEF2=0 BDEF4=45424 SDEF=0; distinct influences/vertex: {1: 6857, 2: 7437, 3: 22790, 4: 8340}; sum!=1: 0; negative: 0

| # | bone | nV(w>0) | Σw | ymin | ymax |
|---|---|---|---|---|---|
| 218 | leg right thigh ctr | 15578 | 3115.6 | 6.45 | 10.92 |
| 219 | leg right thigh ctr2 | 14523 | 8159.9 | 4.38 | 9.16 |
| 213 | 右足 | 14442 | 3253.7 | 4.43 | 8.81 |
| 3 | 上半身2 | 5483 | 2291.8 | 10.29 | 14.70 |
| 1 | センター | 4315 | 2582.2 | 6.78 | 11.79 |
| 5 | 頭 | 4071 | 2756.1 | 14.04 | 16.67 |
| 2 | 上半身 | 3113 | 474.4 | 9.04 | 13.21 |
| 4 | 首 | 1879 | 403.8 | 13.61 | 15.27 |
| 245 | 右肩 | 1785 | 202.4 | 12.00 | 14.60 |
| 220 | 左肩 | 1774 | 200.7 | 12.00 | 14.60 |
| 211 | leg left thigh ctr | 1758 | 330.2 | 6.45 | 10.92 |
| 248 | 右手首 | 1646 | 559.4 | 9.37 | 10.89 |
| 223 | 左手首 | 1640 | 561.5 | 9.37 | 10.89 |
| 268 | arm right shoulder 2 ctr | 1516 | 546.8 | 11.72 | 14.33 |
| 243 | arm left shoulder 2 ctr | 1506 | 545.5 | 11.72 | 14.34 |
| 214 | 右ひざ | 1474 | 1058.5 | 0.72 | 7.13 |
| 207 | 左ひざ | 1448 | 1058.4 | 0.72 | 6.98 |
| 50 | unused dummy | 1369 | 1032.8 | 13.37 | 16.76 |
| 6 | unused face | 1276 | 670.9 | 14.46 | 16.70 |
| 246 | 右腕 | 1167 | 366.1 | 10.69 | 13.24 |
| 221 | 左腕 | 1165 | 364.5 | 10.69 | 13.24 |
| 10 | head jaw | 1150 | 655.6 | 14.51 | 15.34 |
| 267 | arm right wrist ctr | 1077 | 674.0 | 9.70 | 11.32 |
| 242 | arm left wrist ctr | 1077 | 674.7 | 9.70 | 11.32 |
| 244 | arm left shoulder 2 ctr2 | 964 | 292.1 | 11.58 | 13.55 |
| 269 | arm right shoulder 2 ctr2 | 964 | 292.1 | 11.58 | 13.55 |
| 241 | arm left elbow ctr2 | 946 | 209.0 | 10.20 | 11.86 |
| 266 | arm right elbow ctr2 | 943 | 208.6 | 10.20 | 11.86 |
| 208 | leg left foot | 749 | 214.0 | 0.11 | 2.93 |
| 215 | leg right foot | 749 | 214.0 | 0.11 | 2.93 |
| 212 | leg left thigh ctr2 | 699 | 149.0 | 4.38 | 9.16 |
| 284 | leg left butt ctr | 685 | 41.6 | 7.95 | 10.49 |
| 222 | 左ひじ | 683 | 212.6 | 10.79 | 12.31 |
| 247 | 右ひじ | 683 | 211.6 | 10.79 | 12.31 |
| 285 | leg right butt ctr | 682 | 41.8 | 7.95 | 10.34 |
| 206 | 左足 | 618 | 228.9 | 4.43 | 8.49 |
| 252 | unused arm right metacarpal | 612 | 234.1 | 9.38 | 10.28 |
| 227 | unused arm left metacarpal | 608 | 235.0 | 9.38 | 10.28 |
| 42 | head eyelid right upper | 529 | 304.3 | 15.29 | 15.61 |
| 25 | head eyelid left upper | 528 | 305.5 | 15.29 | 15.61 |
| 262 | 右親指０ | 459 | 115.3 | 9.34 | 10.20 |
| 271 | breast left tip | 458 | 275.1 | 11.66 | 13.47 |
| 251 | 右人指３ | 457 | 374.3 | 9.07 | 9.45 |
| 278 | breast right tip | 456 | 274.5 | 11.66 | 13.47 |
| 237 | 左親指０ | 455 | 117.8 | 9.33 | 10.23 |
| 226 | 左人指３ | 455 | 372.4 | 9.07 | 9.45 |
| 270 | breast left base | 406 | 18.7 | 11.33 | 13.68 |
| 277 | breast right base | 406 | 18.6 | 11.33 | 13.70 |
| 280 | breast right b | 371 | 53.3 | 12.46 | 13.71 |
| 273 | breast left b | 371 | 52.9 | 12.46 | 13.71 |
| 258 | 右薬指３ | 360 | 281.4 | 9.09 | 9.49 |
| 263 | 右親指１ | 357 | 157.5 | 9.24 | 9.91 |
| 233 | 左薬指３ | 355 | 280.5 | 9.09 | 9.49 |
| 238 | 左親指１ | 347 | 153.0 | 9.24 | 9.91 |
| 236 | 左中指３ | 342 | 272.8 | 9.05 | 9.43 |
| 274 | breast left c | 341 | 38.1 | 12.59 | 13.84 |
| 281 | breast right c | 339 | 38.1 | 12.59 | 13.84 |
| 261 | 右中指３ | 339 | 272.7 | 9.05 | 9.43 |
| 224 | 左人指１ | 319 | 99.6 | 9.30 | 9.78 |
| 264 | 右親指２ | 316 | 255.2 | 9.09 | 9.51 |
| 250 | 右人指２ | 315 | 119.7 | 9.15 | 9.64 |
| 255 | 右小指３ | 314 | 269.2 | 9.18 | 9.54 |
| 230 | 左小指３ | 314 | 267.5 | 9.18 | 9.54 |
| 225 | 左人指２ | 313 | 120.8 | 9.16 | 9.64 |
| 239 | 左親指２ | 312 | 256.5 | 9.09 | 9.51 |
| 249 | 右人指１ | 301 | 99.8 | 9.28 | 9.79 |
| 217 | leg right knee ctr | 299 | 27.1 | 4.48 | 6.48 |
| 210 | leg left knee ctr | 299 | 27.1 | 4.48 | 6.48 |
| 259 | 右中指１ | 277 | 82.2 | 9.24 | 9.85 |
| 8 | head lip upper middle | 274 | 66.3 | 14.86 | 15.09 |
| 234 | 左中指１ | 272 | 84.2 | 9.21 | 9.85 |
| 253 | 右小指１ | 261 | 75.3 | 9.36 | 9.92 |
| 228 | 左小指１ | 259 | 76.4 | 9.34 | 9.84 |
| 256 | 右薬指１ | 252 | 71.2 | 9.31 | 9.85 |
| 231 | 左薬指１ | 249 | 70.0 | 9.31 | 9.85 |
| 44 | head lip corner right | 238 | 59.3 | 14.64 | 15.01 |
| 27 | head lip corner left | 237 | 59.3 | 14.64 | 15.01 |
| 276 | breast left e | 234 | 43.2 | 11.86 | 13.35 |
| 283 | breast right e | 234 | 43.1 | 11.86 | 13.35 |
| 260 | 右中指２ | 225 | 70.6 | 9.11 | 9.62 |
| 235 | 左中指２ | 218 | 70.0 | 9.12 | 9.62 |
| 257 | 右薬指２ | 201 | 83.2 | 9.18 | 9.60 |
| 232 | 左薬指２ | 201 | 82.0 | 9.18 | 9.60 |
| 254 | 右小指２ | 193 | 70.0 | 9.25 | 9.63 |
| 21 | head eyelid left lower 2 | 190 | 51.7 | 15.25 | 15.54 |
| 38 | head eyelid right lower 2 | 190 | 47.5 | 15.25 | 15.54 |
| 229 | 左小指２ | 189 | 70.4 | 9.26 | 9.63 |
| 265 | arm right elbow ctr | 188 | 19.9 | 11.05 | 12.02 |
| 240 | arm left elbow ctr | 182 | 20.2 | 11.10 | 12.02 |
| 282 | breast right d | 178 | 15.3 | 12.51 | 13.70 |
| 275 | breast left d | 178 | 15.3 | 12.51 | 13.70 |
| 279 | breast right a | 177 | 19.9 | 11.94 | 13.43 |
| 272 | breast left a | 176 | 19.9 | 11.94 | 13.43 |
| 30 | head nose left 2 | 166 | 47.6 | 14.95 | 15.30 |
| 47 | head nose right 2 | 164 | 51.4 | 14.95 | 15.30 |
| 14 | head lip lower left | 158 | 47.0 | 14.58 | 14.90 |
| 15 | head lip lower right | 157 | 44.8 | 14.58 | 14.90 |
| 28 | head lip upper left | 153 | 47.9 | 14.83 | 15.08 |
| 45 | head lip upper right | 149 | 47.9 | 14.83 | 15.08 |
| 9 | head nose middle | 146 | 34.3 | 15.01 | 15.24 |
| 40 | head eyebrow right 2 | 142 | 21.0 | 15.42 | 15.79 |
| 23 | head eyebrow left 2 | 142 | 20.0 | 15.42 | 15.79 |
| 11 | head lip lower middle | 136 | 54.1 | 14.65 | 15.09 |
| 37 | head eyelid right lower 1 | 135 | 27.2 | 15.30 | 15.47 |
| 20 | head eyelid left lower 1 | 135 | 28.3 | 15.30 | 15.47 |
| 17 | head cheek left 2 | 132 | 16.1 | 14.89 | 15.62 |
| 34 | head cheek right 2 | 132 | 18.8 | 14.89 | 15.62 |
| 18 | head cheek left 3 | 129 | 28.5 | 14.58 | 15.34 |
| 35 | head cheek right 3 | 129 | 26.3 | 14.58 | 15.34 |
| 36 | 右目 | 129 | 129.0 | 15.30 | 15.61 |
| 19 | 左目 | 129 | 129.0 | 15.30 | 15.61 |
| 16 | head cheek left 1 | 127 | 27.6 | 14.96 | 15.51 |
| 33 | head cheek right 1 | 125 | 29.1 | 14.96 | 15.51 |
| 202 | hair front side left 3 | 121 | 55.4 | 13.08 | 15.15 |
| 209 | 左つま先 | 106 | 58.4 | 0.11 | 1.03 |
| 216 | 右つま先 | 106 | 58.4 | 0.11 | 1.03 |
| 39 | head eyebrow right 1 | 102 | 21.4 | 15.32 | 15.79 |
| 22 | head eyebrow left 1 | 102 | 20.9 | 15.32 | 15.79 |
| 190 | hair front right 2 | 95 | 34.1 | 15.68 | 16.76 |
| 41 | head eyebrow right 3 | 88 | 16.3 | 15.46 | 15.84 |
| 24 | head eyebrow left 3 | 88 | 17.3 | 15.46 | 15.84 |
| 29 | head nose left 1 | 85 | 17.5 | 15.07 | 15.41 |
| 46 | head nose right 1 | 79 | 15.7 | 15.09 | 15.41 |
| 191 | hair front right 3 | 78 | 35.3 | 15.46 | 16.51 |
| 197 | hair front side right 3 | 75 | 13.9 | 13.37 | 16.04 |
| 162 | hair back c side left 1 | 71 | 13.7 | 14.49 | 16.44 |
| 192 | hair front right 4 | 70 | 33.9 | 15.36 | 16.33 |
| 185 | hair front left 2 | 66 | 23.8 | 15.52 | 16.63 |
| 196 | hair front side right 2 | 65 | 9.6 | 13.62 | 16.04 |
| 164 | hair back c side left 3 | 65 | 18.5 | 13.88 | 15.88 |
| 12 | head tongue 1 | 64 | 31.8 | 14.77 | 14.92 |
| 203 | hair front side left 4 | 64 | 17.9 | 13.10 | 14.67 |
| 13 | head tongue 2 | 63 | 32.2 | 14.79 | 14.92 |
| 31 | head nose left 3 | 61 | 10.1 | 14.93 | 15.14 |
| 48 | head nose right 3 | 61 | 11.1 | 14.93 | 15.14 |
| 198 | hair front side right 4 | 58 | 15.7 | 13.37 | 15.57 |
| 163 | hair back c side left 2 | 58 | 14.3 | 14.49 | 16.27 |
| 204 | hair front side left 5 | 56 | 9.2 | 13.08 | 13.31 |
| 117 | hair back b side left 2 | 56 | 11.9 | 14.27 | 16.27 |
| 64 | hair back a left 6 | 56 | 31.2 | 10.91 | 12.64 |
| 145 | hair back c left 2 | 55 | 8.5 | 13.89 | 16.33 |
| 173 | hair back c side right 3 | 55 | 20.3 | 13.97 | 15.90 |
| 189 | hair front right 1 | 55 | 25.7 | 15.91 | 16.76 |
| 62 | hair back a left 4 | 54 | 19.9 | 12.50 | 14.51 |
| 71 | hair back a right 6 | 54 | 31.8 | 10.91 | 12.64 |
| 118 | hair back b side left 3 | 54 | 14.5 | 14.11 | 15.90 |
| 63 | hair back a left 5 | 53 | 20.5 | 11.75 | 13.73 |
| 146 | hair back c left 3 | 53 | 11.7 | 13.72 | 16.13 |
| 193 | hair front right 5 | 52 | 23.1 | 14.94 | 15.99 |
| 201 | hair front side left 2 | 51 | 16.3 | 14.27 | 15.24 |
| 126 | hair back b side right 2 | 51 | 11.5 | 14.26 | 16.14 |
| 127 | hair back b side right 3 | 51 | 14.5 | 14.08 | 15.79 |
| 128 | hair back b side right 4 | 50 | 17.6 | 13.48 | 15.43 |
| 69 | hair back a right 4 | 50 | 18.6 | 12.50 | 14.38 |
| 65 | hair back a left 7 | 50 | 30.5 | 10.25 | 11.97 |
| 136 | hair back c middle 3 | 50 | 11.3 | 13.30 | 15.90 |
| 171 | hair back c side right 1 | 50 | 7.5 | 14.58 | 16.37 |
| 172 | hair back c side right 2 | 50 | 11.4 | 14.43 | 16.36 |
| 160 | hair back c right 8 | 50 | 18.2 | 9.77 | 12.15 |
| 70 | hair back a right 5 | 49 | 21.0 | 11.88 | 13.63 |
| 116 | hair back b side left 1 | 49 | 6.6 | 14.75 | 16.30 |
| 165 | hair back c side left 4 | 48 | 17.7 | 13.42 | 15.10 |
| 155 | hair back c right 3 | 48 | 11.2 | 13.72 | 16.12 |
| 174 | hair back c side right 4 | 48 | 17.9 | 13.22 | 14.87 |
| 135 | hair back c middle 2 | 47 | 8.9 | 13.92 | 16.12 |
| 154 | hair back c right 2 | 47 | 7.4 | 13.88 | 16.35 |
| 205 | hair front side left 6 | 46 | 29.2 | 13.08 | 13.31 |
| 72 | hair back a right 7 | 46 | 29.7 | 10.25 | 11.82 |
| 151 | hair back c left 8 | 46 | 17.3 | 9.80 | 11.99 |
| 119 | hair back b side left 4 | 46 | 19.6 | 13.47 | 15.30 |
| 68 | hair back a right 3 | 45 | 17.8 | 13.19 | 14.73 |
| 129 | hair back b side right 5 | 44 | 20.0 | 12.95 | 14.60 |
| 120 | hair back b side left 5 | 44 | 14.8 | 12.98 | 14.59 |
| 61 | hair back a left 3 | 44 | 15.7 | 13.19 | 14.73 |
| 184 | hair front left 1 | 42 | 16.7 | 15.79 | 16.63 |
| 43 | head forehead right | 42 | 6.5 | 15.56 | 15.95 |
| 26 | head forehead left | 42 | 6.6 | 15.56 | 15.95 |
| 109 | hair back b right 3 | 42 | 13.3 | 14.02 | 15.79 |
| 147 | hair back c left 4 | 42 | 14.0 | 13.07 | 15.20 |
| 100 | hair back b left 3 | 42 | 13.7 | 13.89 | 15.78 |
| 90 | hair back b middle 2 | 41 | 10.7 | 14.18 | 15.89 |
| 178 | hair back c side right 8 | 41 | 16.8 | 10.34 | 12.16 |
| 195 | hair front side right 1 | 41 | 12.8 | 14.17 | 16.21 |
| 125 | hair back b side right 1 | 41 | 8.6 | 14.67 | 16.14 |
| 60 | hair back a left 2 | 40 | 7.5 | 13.41 | 14.82 |
| 89 | hair back b middle 1 | 40 | 15.3 | 14.46 | 16.11 |
| 110 | hair back b right 4 | 40 | 12.9 | 13.31 | 15.18 |
| 176 | hair back c side right 6 | 40 | 16.3 | 12.16 | 13.53 |
| 186 | hair front left 3 | 39 | 17.9 | 15.28 | 16.02 |
| 108 | hair back b right 2 | 39 | 9.6 | 14.31 | 15.91 |
| 83 | hair back a side right 3 | 39 | 10.7 | 13.54 | 15.43 |
| 82 | hair back a side right 2 | 39 | 6.0 | 13.68 | 15.64 |
| 121 | hair back b side left 6 | 38 | 16.3 | 12.19 | 13.79 |
| 122 | hair back b side left 7 | 38 | 16.1 | 11.56 | 13.14 |
| 98 | hair back b left 1 | 38 | 10.7 | 14.60 | 16.11 |
| 101 | hair back b left 4 | 38 | 12.2 | 13.32 | 15.04 |
| 107 | hair back b right 1 | 38 | 12.4 | 14.45 | 16.10 |
| 76 | hair back a side left 4 | 38 | 14.0 | 12.99 | 14.66 |
| 74 | hair back a side left 2 | 38 | 7.5 | 13.54 | 15.44 |
| 84 | hair back a side right 4 | 38 | 14.4 | 12.99 | 14.66 |
| 81 | hair back a side right 1 | 38 | 8.8 | 13.95 | 15.79 |
| 150 | hair back c left 7 | 37 | 16.6 | 11.18 | 12.57 |
| 159 | hair back c right 7 | 37 | 14.3 | 11.13 | 12.58 |
| 156 | hair back c right 4 | 37 | 14.5 | 13.07 | 15.04 |
| 158 | hair back c right 6 | 37 | 15.3 | 11.70 | 13.23 |
| 91 | hair back b middle 3 | 37 | 14.4 | 13.76 | 15.54 |
| 130 | hair back b side right 6 | 37 | 10.2 | 12.33 | 13.74 |
| 67 | hair back a right 2 | 37 | 6.4 | 13.52 | 14.82 |
| 32 | head nose left 4 | 36 | 6.2 | 14.86 | 15.30 |
| 132 | hair back b side right 8 | 36 | 14.9 | 10.94 | 12.51 |
| 131 | hair back b side right 7 | 36 | 18.7 | 11.71 | 13.00 |
| 99 | hair back b left 2 | 36 | 10.6 | 14.45 | 15.90 |
| 105 | hair back b left 8 | 36 | 15.4 | 10.61 | 12.24 |
| 167 | hair back c side left 6 | 36 | 17.8 | 12.20 | 13.46 |
| 77 | hair back a side left 5 | 36 | 17.4 | 12.43 | 14.00 |
| 75 | hair back a side left 3 | 36 | 9.7 | 13.54 | 15.17 |
| 169 | hair back c side left 8 | 36 | 14.7 | 10.34 | 12.06 |
| 49 | head nose right 4 | 36 | 6.3 | 14.86 | 15.30 |
| 123 | hair back b side left 8 | 35 | 15.1 | 10.93 | 12.49 |
| 134 | hair back c middle 1 | 35 | 4.6 | 14.54 | 16.12 |
| 175 | hair back c side right 5 | 35 | 14.3 | 12.77 | 13.98 |
| 157 | hair back c right 5 | 34 | 13.0 | 12.43 | 14.22 |
| 148 | hair back c left 5 | 34 | 12.9 | 12.43 | 14.23 |
| 177 | hair back c side right 7 | 34 | 15.6 | 11.56 | 12.77 |
| 104 | hair back b left 7 | 34 | 14.7 | 11.24 | 12.88 |
| 114 | hair back b right 8 | 34 | 21.6 | 10.27 | 12.07 |
| 133 | hair back b side right 9 | 34 | 22.5 | 10.45 | 11.87 |
| 124 | hair back b side left 9 | 33 | 22.3 | 10.42 | 11.85 |
| 168 | hair back c side left 7 | 33 | 15.8 | 11.59 | 12.81 |
| 166 | hair back c side left 5 | 33 | 15.5 | 12.81 | 14.03 |
| 149 | hair back c left 6 | 33 | 14.3 | 11.84 | 13.24 |
| 103 | hair back b left 6 | 31 | 12.6 | 11.99 | 13.47 |
| 112 | hair back b right 6 | 31 | 12.1 | 12.07 | 13.60 |
| 111 | hair back b right 5 | 31 | 11.8 | 12.72 | 14.17 |
| 85 | hair back a side right 5 | 31 | 12.3 | 12.43 | 13.87 |
| 102 | hair back b left 5 | 30 | 12.3 | 12.72 | 14.17 |
| 87 | hair back a side right 7 | 30 | 9.7 | 11.48 | 12.81 |
| 59 | hair back a left 1 | 29 | 1.8 | 13.74 | 14.73 |
| 53 | hair back a middle 3 | 29 | 13.6 | 13.14 | 14.63 |
| 180 | hair front middle 1 | 28 | 16.6 | 15.35 | 16.56 |
| 181 | hair front middle 2 | 28 | 12.5 | 15.49 | 16.37 |
| 152 | hair back c left 9 | 28 | 17.5 | 9.80 | 11.25 |
| 106 | hair back b left 9 | 28 | 18.1 | 9.77 | 11.46 |
| 115 | hair back b right 9 | 28 | 12.3 | 9.77 | 11.46 |
| 113 | hair back b right 7 | 28 | 15.1 | 11.24 | 12.73 |
| 161 | hair back c right 9 | 28 | 16.9 | 9.77 | 11.28 |
| 92 | hair back b middle 4 | 27 | 5.5 | 13.21 | 14.74 |
| 137 | hair back c middle 4 | 27 | 9.6 | 13.30 | 14.89 |
| 88 | hair back a side right 8 | 27 | 21.4 | 10.93 | 12.15 |
| 66 | hair back a right 1 | 27 | 1.6 | 13.84 | 14.73 |
| 144 | hair back c left 1 | 27 | 1.4 | 15.31 | 16.33 |
| 86 | hair back a side right 6 | 27 | 11.6 | 12.03 | 13.21 |
| 73 | hair back a side left 1 | 26 | 6.2 | 14.09 | 15.44 |
| 57 | hair back a middle 7 | 26 | 11.9 | 10.50 | 11.83 |
| 55 | hair back a middle 5 | 26 | 11.9 | 11.82 | 13.15 |
| 56 | hair back a middle 6 | 26 | 12.0 | 11.16 | 12.49 |
| 54 | hair back a middle 4 | 26 | 12.1 | 12.48 | 13.81 |
| 7 | head eyebrow middle | 25 | 6.1 | 15.46 | 15.65 |
| 79 | hair back a side left 7 | 25 | 11.1 | 11.35 | 12.55 |
| 80 | hair back a side left 8 | 24 | 19.2 | 10.93 | 12.02 |
| 200 | hair front side left 1 | 24 | 7.6 | 14.93 | 15.61 |
| 179 | hair back c side right 9 | 24 | 16.9 | 10.34 | 11.42 |
| 138 | hair back c middle 5 | 24 | 7.9 | 12.68 | 14.39 |
| 78 | hair back a side left 6 | 24 | 8.2 | 12.03 | 13.08 |
| 58 | hair back a middle 8 | 24 | 19.0 | 10.00 | 11.16 |
| 194 | hair front right 6 | 23 | 10.9 | 14.75 | 15.45 |
| 199 | hair front side right 5 | 22 | 5.5 | 13.37 | 14.71 |
| 153 | hair back c right 1 | 22 | 1.5 | 15.17 | 16.33 |
| 182 | hair front middle 3 | 21 | 10.3 | 15.35 | 16.10 |
| 142 | hair back c middle 9 | 21 | 6.0 | 9.59 | 11.47 |
| 187 | hair front left 4 | 20 | 11.0 | 14.93 | 15.51 |
| 170 | hair back c side left 9 | 20 | 13.3 | 10.34 | 11.44 |
| 139 | hair back c middle 6 | 18 | 6.3 | 12.06 | 13.62 |
| 52 | hair back a middle 2 | 17 | 3.3 | 13.80 | 14.63 |
| 143 | hair back c middle 10 | 15 | 9.5 | 9.59 | 10.86 |
| 140 | hair back c middle 7 | 15 | 5.5 | 11.44 | 12.70 |
| 95 | hair back b middle 7 | 15 | 3.7 | 11.23 | 12.65 |
| 94 | hair back b middle 6 | 15 | 8.8 | 11.98 | 13.21 |
| 141 | hair back c middle 8 | 15 | 6.5 | 10.83 | 12.09 |
| 93 | hair back b middle 5 | 14 | 5.1 | 12.64 | 13.77 |
| 97 | hair back b middle 9 | 12 | 10.6 | 9.73 | 10.89 |
| 51 | hair back a middle 1 | 12 | 0.8 | 14.14 | 14.63 |
| 96 | hair back b middle 8 | 11 | 5.9 | 10.52 | 11.62 |
| 188 | hair front left 5 | 7 | 3.5 | 14.76 | 15.15 |
| 183 | hair front middle 4 | 6 | 1.7 | 15.47 | 15.91 |

## 6. Morphs
| # | name | name_e | panel | type | nOff | detail |
|---|---|---|---|---|---|---|

## 7. Rigid bodies
| # | name | name_e | bone | shape | size | pos | pos-bone | rot° | mass | linD | angD | rest | fric | mode | grp | non-coll | mask |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### Joints
| # | name | name_e | type | A | B | pos | rot° | move min~max | rot min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|---|---|---|---|---|---|

## 8. Materials
textures: [0]kok_face_base.png; [1]l.png; [2]kok_face_nrm_VLH2_PP1.png; [3]kokoro_front_new_hair_base.png; [4]n.png; [5]kokoro_backhair_base.png; [6]kokoro_backhair_bump_N.png; [7]kokoro_uematug2.png; [8]kokoro_sitamatuge_base.png; [9]kokoro_eye_sdw00.png; [10]acs_base.png; [11]acs_nrm.png; [12]acs_spec.png; [13]suita_base.png; [14]suita_nrm.png; [15]suita_spec.png; [16]suitb_base.png; [17]suitb_nrm.png; [18]suitb_spec.png; [19]body_base.png; [20]body_nrm.png; [21]body_spec.png; [22]L_16.dds; [23]L_16n.dds

| # | name | name_e | tex | sphere(mode) | toon | diffuse | specular | shin | ambient | flags D/G/M/S/E | edge | edge color | faces | memo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | eyes | eyes | kok_face_base.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 480 |  RenderGroup:	24 Parameters:	5, 1, 1 |
| 1 | face | face | kok_face_base.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 6782 |  RenderGroup:	24 Parameters:	0.6, 1, 1 |
| 2 | alpha2 | alpha2 | kokoro_front_new_hair_base.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 974 |  RenderGroup:	25 Parameters:	0.5, 1, 1 |
| 3 | alpha4 | alpha4 | kokoro_backhair_base.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 3277 |  RenderGroup:	25 Parameters:	0.5, 1, 1 |
| 4 | alpha5 | alpha5 | kokoro_uematug2.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 266 |  RenderGroup:	25 Parameters:	1, 1, 1 |
| 5 | alpha6 | alpha6 | kokoro_uematug2.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 266 |  RenderGroup:	25 Parameters:	1, 1, 1 |
| 6 | alpha7 | alpha7 | kokoro_sitamatuge_base.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 48 |  RenderGroup:	25 Parameters:	1, 1, 1 |
| 7 | alpha8 | alpha8 | kokoro_sitamatuge_base.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 48 |  RenderGroup:	25 Parameters:	1, 1, 1 |
| 8 | alpha9 | alpha9 | kokoro_eye_sdw00.png | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 416 |  RenderGroup:	25 Parameters:	1, 1, 1 |
| 9 | suit acs b | suit acs b | acs_base.png | acs_nrm.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 10025 |  RenderGroup:	40 Parameters:	0.1, 16, 16 |
| 10 | suit shoes | suit shoes | suita_base.png | suita_nrm.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 1038 |  RenderGroup:	40 Parameters:	0.1, 16, 16 |
| 11 | suit acs a | suit acs a | suitb_base.png | suitb_nrm.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 4120 |  RenderGroup:	40 Parameters:	0.1, 16, 16 |
| 12 | suit b | suit b | suitb_base.png | suitb_nrm.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 19068 |  RenderGroup:	40 Parameters:	0.1, 16, 16 |
| 13 | +suit a.suit a | +suit a.suit a | suita_base.png | suita_nrm.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 12304 |  RenderGroup:	40 Parameters:	0.1, 16, 16 |
| 14 | -body.body | -body.body | body_base.png | body_nrm.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 4880 |  RenderGroup:	40 Parameters:	0.1, 16, 16 |
| 15 | -suit neck.suit neck | -suit neck.suit neck | suita_base.png | suita_nrm.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 1416 |  RenderGroup:	40 Parameters:	0.1, 16, 16 |
| 16 | +mask.mask | +mask.mask | L_16.dds | l.png (off) | shared toon01 | (1.00, 1.00, 1.00, 1.00) | (1.00, 1.00, 1.00) | 10 | (0.50, 0.50, 0.50) | ----- | 1 | (0.00, 0.00, 0.00, 1.00) | 648 |  RenderGroup:	24 Parameters:	0.1, 0, 0 |

## 9. Display frames
- **Root** / Root special=True n=0: 
- **袆情** / Exp special=True n=0: 

## 10. Validation smells
- dup_bones: {'': 2}
- dup_morphs: {}
- dup_mats: {}
- dup_rigids: {}
- dup_joints: {}
- bone_gt15: [('head eyebrow middle', 19), ('head lip upper middle', 21), ('head nose middle', 16), ('head lip lower middle', 21), ('head lip lower left', 19), ('head lip lower right', 20), ('head cheek left 1', 17), ('head cheek left 2', 17), ('head cheek left 3', 17), ('head eyelid left lower 1', 24), ('head eyelid left lower 2', 24), ('head eyebrow left 1', 19), ('head eyebrow left 2', 19), ('head eyebrow left 3', 19), ('head eyelid left upper', 22), ('head forehead left', 18), ('head lip corner left', 20), ('head lip upper left', 19), ('head nose left 1', 16), ('head nose left 2', 16), ('head nose left 3', 16), ('head nose left 4', 16), ('head cheek right 1', 18), ('head cheek right 2', 18), ('head cheek right 3', 18), ('head eyelid right lower 1', 25), ('head eyelid right lower 2', 25), ('head eyebrow right 1', 20), ('head eyebrow right 2', 20), ('head eyebrow right 3', 20), ('head eyelid right upper', 23), ('head forehead right', 19), ('head lip corner right', 21), ('head lip upper right', 20), ('head nose right 1', 17), ('head nose right 2', 17), ('head nose right 3', 17), ('head nose right 4', 17), ('hair back a middle 1', 20), ('hair back a middle 2', 20), ('hair back a middle 3', 20), ('hair back a middle 4', 20), ('hair back a middle 5', 20), ('hair back a middle 6', 20), ('hair back a middle 7', 20), ('hair back a middle 8', 20), ('hair back a left 1', 18), ('hair back a left 2', 18), ('hair back a left 3', 18), ('hair back a left 4', 18), ('hair back a left 5', 18), ('hair back a left 6', 18), ('hair back a left 7', 18), ('hair back a right 1', 19), ('hair back a right 2', 19), ('hair back a right 3', 19), ('hair back a right 4', 19), ('hair back a right 5', 19), ('hair back a right 6', 19), ('hair back a right 7', 19)] ... (969)
- morph_gt15: []
- non_cp932_bones: []
- non_cp932_morphs: []
- non_cp932_mats: []
- empty_name_e_bones: 2
- unused_leaf_bones_noweight: ['unused head eyebrow middle', 'unused head lip upper middle', 'unused head nose middle', 'unused head lip lower middle', 'unused head lip lower left', 'unused head lip lower right', 'unused head cheek left a', 'unused head cheek left b', 'unused head cheek left c', 'unused head eyeball left', 'unused head eyelid lower left a', 'unused head eyelid lower left b', 'unused head eyebrow left a', 'unused head eyebrow left b', 'unused head eyebrow left c', 'unused head eyelid upper left', 'unused head forehead left', 'unused head lip corner left', 'unused head lip upper left', 'unused head nose left a', 'unused head nose left b', 'unused head nose left c', 'unused head nose left d', 'unused head cheek right a', 'unused head cheek right b', 'unused head cheek right c', 'unused head eyeball right', 'unused head eyelid lower right a', 'unused head eyelid lower right b', 'unused head eyebrow right a', 'unused head eyebrow right b', 'unused head eyebrow right c', 'unused head eyelid upper right', 'unused head forehead right', 'unused head lip corner right', 'unused head lip upper right', 'unused head nose right a', 'unused head nose right b', 'unused head nose right c', 'unused head nose right d', 'unusedopt-dummy-head item-honoka hair +3 item-full head +4', 'head cheek left a', 'head cheek left b', 'head cheek left c', 'head eyelid lower left a', 'head eyelid lower left b', 'head eyebrow left a', 'head eyebrow left b', 'head eyebrow left c', 'head eyelid upper left', 'head nose left a', 'head nose left b', 'head nose left c', 'head nose left d', 'head cheek right a', 'head cheek right b', 'head cheek right c', 'head eyelid lower right a', 'head eyelid lower right b', 'head eyebrow right a'] ... (123)
- weighted_but_nonrot: []
- weighted_bones: 285
- wsum_bad: 0
- rigid_no_bone: []
- joint_bad: []
- missing_textures: []
- parent_after_child: ['head eyebrow middle', 'head lip upper middle', 'head nose middle', 'head jaw', '左目', 'head forehead left', 'head lip corner left', 'head lip upper left', '右目', 'head forehead right', 'head lip corner right', 'head lip upper right']
- ctrl_visible_not_in_frames: ['センター', '上半身', '上半身2', '首', '頭', 'head eyebrow middle', 'head lip upper middle', 'head nose middle', 'head jaw', 'head lip lower middle', 'head tongue 1', 'head tongue 2', 'head lip lower left', 'head lip lower right', 'head cheek left 1', 'head cheek left 2', 'head cheek left 3', '左目', 'head eyelid left lower 1', 'head eyelid left lower 2', 'head eyebrow left 1', 'head eyebrow left 2', 'head eyebrow left 3', 'head eyelid left upper', 'head forehead left', 'head lip corner left', 'head lip upper left', 'head nose left 1', 'head nose left 2', 'head nose left 3', 'head nose left 4', 'head cheek right 1', 'head cheek right 2', 'head cheek right 3', '右目', 'head eyelid right lower 1', 'head eyelid right lower 2', 'head eyebrow right 1', 'head eyebrow right 2', 'head eyebrow right 3', 'head eyelid right upper', 'head forehead right', 'head lip corner right', 'head lip upper right', 'head nose right 1', 'head nose right 2', 'head nose right 3', 'head nose right 4', 'hair back a middle 1', 'hair back a middle 2', 'hair back a middle 3', 'hair back a middle 4', 'hair back a middle 5', 'hair back a middle 6', 'hair back a middle 7', 'hair back a middle 8', 'hair back a left 1', 'hair back a left 2', 'hair back a left 3', 'hair back a left 4'] ... (485)
