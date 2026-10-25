
## Inase18_V1: 35 rigid bodies, 16 joints
category counts: body=19, hair=14, breast=2
- body: group/non-collide sets: g1 nc=[1, 16] ×19
- hair: group/non-collide sets: g10 nc=[2, 9, 10, 11, 12, 16] ×14
- breast: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2

| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |
|---|---|---|---|---|---|---|---|---|---|
| body | 19 | {'capsule': 19} | {'static': 19} | r/w 0.335~1.39; h 0.492~5.17; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| hair | 14 | {'capsule': 14} | {'dynamic': 14} | r/w 0.0656~0.149; h 0.22~0.901; d - | 1 | 0.9 | 0.99 | 0 | 0 |
| breast | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.597491; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |

| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|
| hair | 14 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 14} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 14} | {(0.0, 0.0, 0.0): 14} | {(0.0, 0.0, 0.0): 14} |
| breast | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(0.0, 0.0, 0.0): 2} |

chains (root → … ; mode letters s=static d=dynamic b=dyn+bone):
- [hair] 頭(s) → hair front left 1(d) → hair front left 2(d) → hair front left 3(d)  segments(dynamic)=3
- [hair] 頭(s) → hair front right 1(d) → hair front right 2(d) → hair front right 3(d)  segments(dynamic)=3
- [hair] 頭(s) → head hair left 1(d) → head hair left 2(d)  segments(dynamic)=2
- [hair] 頭(s) → head hair front right 1(d) → head hair front right 2(d)  segments(dynamic)=2
- [hair] 頭(s) → head hair front right 3(d) → head hair front right 4(d)  segments(dynamic)=2
- [hair] 頭(s) → hair back left 1(d) → hair back left 2(d)  segments(dynamic)=2
- [breast] 上半身2(s) → 左乳奶(d)  segments(dynamic)=1
- [breast] 上半身2(s) → 右乳奶(d)  segments(dynamic)=1

## Reika18_None: 83 rigid bodies, 64 joints
category counts: body=19, hair=58, breast=2, clothing=4
- body: group/non-collide sets: g1 nc=[1, 16] ×19
- hair: group/non-collide sets: g10 nc=[2, 9, 10, 11, 12, 16] ×53; g2 nc=[1, 2, 3, 9, 10, 11, 12, 16] ×5
- breast: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2
- clothing: group/non-collide sets: g11 nc=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×4

| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |
|---|---|---|---|---|---|---|---|---|---|
| body | 19 | {'capsule': 19} | {'static': 19} | r/w 0.594~1.5; h 0.56~5.32; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| hair | 58 | {'capsule': 20, 'box': 38} | {'dynamic': 58} | r/w 0.0781~1; h 0.391~0.929; d 0.2 | 1 | 0.9 | 0.99 | 0 | 0 |
| breast | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.6; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| clothing | 4 | {'capsule': 4} | {'dynamic': 4} | r/w 0.0872~0.103; h 0.436~0.517; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |

| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|
| hair | 58 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 58} | {((-30.0, -10.0, -30.0), (30.0, 30.0, 30.0)): 8, ((-30.0, -30.0, -30.0), (30.0, 30.0, 30.0)): 38, ((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 12} | {(0.0, 0.0, 0.0): 58} | {(30.0, 30.0, 30.0): 46, (0.0, 0.0, 0.0): 12} |
| breast | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-30.0, -10.0, -30.0), (30.0, 30.0, 30.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(30.0, 30.0, 30.0): 2} |
| clothing | 4 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 4} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 4} | {(0.0, 0.0, 0.0): 4} | {(0.0, 0.0, 0.0): 4} |

chains (root → … ; mode letters s=static d=dynamic b=dyn+bone):
- [hair] 頭(s) → Hair-01.r(d) → Hair-02.r(d) → Hair-03.r(d) → Hair-04.r(d)  segments(dynamic)=4
- [hair] 頭(s) → Hair-01.l(d) → Hair-02.l(d) → Hair-03.l(d) → Hair-04.l(d)  segments(dynamic)=4
- [hair] 頭(s) → Hair-Back-01.x(d) → Hair-Back-02.x(d) → Hair-Back-03.x(d) → Hair-Back-04.x(d) → Hair-Back-05.x(d) → Hair-Back-06.x(d) → Hair-Back-07.x(d) → Hair-Back-08.x(d)  segments(dynamic)=8
- [hair] 頭(s) → Hair-Back-01.l(d) → Hair-Back-02.l(d) → Hair-Back-03.l(d) → Hair-Back-04.l(d) → Hair-Back-05.l(d) → Hair-Back-06.l(d) → Hair-Back-07.l(d) → Hair-Back-08.l(d)  segments(dynamic)=8
- [hair] 頭(s) → Hair-Back-01.r(d) → Hair-Back-02.r(d) → Hair-Back-03.r(d) → Hair-Back-04.r(d) → Hair-Back-05.r(d) → Hair-Back-06.r(d) → Hair-Back-07.r(d)  segments(dynamic)=7
- [hair] 頭(s) → Hair-Back-01.l.001(d) → Hair-Back-02.l.001(d) → Hair-Back-03.l.001(d) → Hair-Back-04.l.001(d) → Hair-Back-05.l.001(d) → Hair-Back-06.l.001(d) → Hair-Back-07.l.001(d)  segments(dynamic)=7
- [hair] 頭(s) → Hair-Back-01.r.001(d) → Hair-Back-02.r.001(d) → Hair-Back-03.r.001(d) → Hair-Back-04.r.001(d) → Hair-Back-05.r.001(d) → Hair-Back-06.r.001(d) → Hair-Back-07.r.001(d) → Hair-Back-08.r.001(d)  segments(dynamic)=8
- [hair] 頭(s) → Hair-Front-01.l(d) → Hair-Front-02.l(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair-Front-01.r(d) → Hair-Front-02.r(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair-Front-2-01.l(d) → Hair-Front-2-02.l(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair-Front-2-01.r(d) → Hair-Front-2-02.r(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair-03(d) → Hair-04(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair-01(d) → Hair-02(d)  segments(dynamic)=2
- [breast] 上半身2(s) → 左乳奶(d) → Bone.L(d) → Bone.001.L(d)  segments(dynamic)=3
- [breast] 上半身2(s) → 右乳奶(d) → Bone.R(d) → Bone.001.R(d)  segments(dynamic)=3

## Bunny18_None: 58 rigid bodies, 40 joints
category counts: body=18, hair?=18, hair=18, breast=2, butt=2
- body: group/non-collide sets: g1 nc=[1, 16] ×18
- hair?: group/non-collide sets: g10 nc=[1, 2, 9, 10, 11, 12, 16] ×2; g10 nc=[2, 9, 10, 11, 12, 16] ×16
- hair: group/non-collide sets: g10 nc=[2, 9, 10, 11, 12, 16] ×18
- breast: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2
- butt: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2

| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |
|---|---|---|---|---|---|---|---|---|---|
| body | 18 | {'capsule': 18} | {'static': 18} | r/w 0.591~2; h 0.359~5.12; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| hair? | 18 | {'capsule': 18} | {'static': 2, 'dynamic': 16} | r/w 0.3; h 0.87~1.53; d - | 1 | 0.9 | 0.99 | 0 | 0 |
| hair | 18 | {'capsule': 18} | {'dynamic': 18} | r/w 0.13; h 0.259~0.521; d - | 1 | 0.9 | 0.99 | 0 | 0 |
| breast | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.6; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| butt | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.6; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |

| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|
| hair? | 18 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 18} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 18} | {(0.0, 0.0, 0.0): 18} | {(0.0, 0.0, 0.0): 18} |
| hair | 18 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 18} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 18} | {(0.0, 0.0, 0.0): 18} | {(0.0, 0.0, 0.0): 18} |
| breast | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(0.0, 0.0, 0.0): 2} |
| butt | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(0.0, 0.0, 0.0): 2} |

chains (root → … ; mode letters s=static d=dynamic b=dyn+bone):
- [hair?] 頭(s) → DEF-ult_hair.L(s) → DEF-ult_hair.L.001(d) → DEF-ult_hair.L.002(d) → DEF-ult_hair.L.003(d) → DEF-ult_hair.L.004(d) → DEF-ult_hair.L.005(d) → DEF-ult_hair.L.006(d) → DEF-ult_hair.L.007(d) → DEF-ult_hair.L.008(d)  segments(dynamic)=8
- [hair?] 頭(s) → DEF-ult_hair.R(s) → DEF-ult_hair.R.001(d) → DEF-ult_hair.R.002(d) → DEF-ult_hair.R.003(d) → DEF-ult_hair.R.004(d) → DEF-ult_hair.R.005(d) → DEF-ult_hair.R.006(d) → DEF-ult_hair.R.007(d) → DEF-ult_hair.R.008(d)  segments(dynamic)=8
- [hair] 頭(s) → Hair Short 1(d) → Hair Short 2(d) → Hair Short 3(d)  segments(dynamic)=3
- [hair] 頭(s) → Hair Short 4(d) → Hair Short 5(d) → Hair Short 6(d)  segments(dynamic)=3
- [hair] 頭(s) → Hair Short 7(d) → Hair Short 8(d) → Hair Short 9(d)  segments(dynamic)=3
- [hair] 頭(s) → Hair Short 10(d) → Hair Short 11(d) → Hair Short 12(d)  segments(dynamic)=3
- [hair] 頭(s) → Hair Short 13(d) → Hair Short 14(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair front L1(d) → Hair front L2(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair front R1(d) → Hair front R2(d)  segments(dynamic)=2
- [hair?] DEF-ult_hair.L(s) → DEF-ult_hair.L.001(d) → DEF-ult_hair.L.002(d) → DEF-ult_hair.L.003(d) → DEF-ult_hair.L.004(d) → DEF-ult_hair.L.005(d) → DEF-ult_hair.L.006(d) → DEF-ult_hair.L.007(d) → DEF-ult_hair.L.008(d)  segments(dynamic)=8
- [hair?] DEF-ult_hair.R(s) → DEF-ult_hair.R.001(d) → DEF-ult_hair.R.002(d) → DEF-ult_hair.R.003(d) → DEF-ult_hair.R.004(d) → DEF-ult_hair.R.005(d) → DEF-ult_hair.R.006(d) → DEF-ult_hair.R.007(d) → DEF-ult_hair.R.008(d)  segments(dynamic)=8
- [butt] 下半身(s) → 左屁股(d)  segments(dynamic)=1
- [butt] 下半身(s) → 右屁股(d)  segments(dynamic)=1
- [breast] 上半身2(s) → 左乳奶(d)  segments(dynamic)=1
- [breast] 上半身2(s) → 右乳奶(d)  segments(dynamic)=1

## Czern18_V1: 33 rigid bodies, 14 joints
category counts: body=19, hair=12, breast=2
- body: group/non-collide sets: g1 nc=[1, 16] ×19
- hair: group/non-collide sets: g10 nc=[2, 9, 10, 11, 12, 16] ×12
- breast: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2

| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |
|---|---|---|---|---|---|---|---|---|---|
| body | 19 | {'capsule': 19} | {'static': 19} | r/w 0.334~1.5; h 0.523~5.19; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| hair | 12 | {'capsule': 12} | {'dynamic': 12} | r/w 0.15~0.35; h 0.52~1.75; d - | 1 | 0.9 | 0.99 | 0 | 0 |
| breast | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.6; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |

| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|
| hair | 12 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 12} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 12} | {(0.0, 0.0, 0.0): 12} | {(0.0, 0.0, 0.0): 12} |
| breast | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(0.0, 0.0, 0.0): 2} |

chains (root → … ; mode letters s=static d=dynamic b=dyn+bone):
- [hair] 頭(s) → L_Side_1(d) → L_Side_2(d) → L_Side_3(d) → L_Side_4(d)  segments(dynamic)=4
- [hair] 頭(s) → Hair_1(d) → Hair_2(d) → Hair_3(d) → Hair_4(d)  segments(dynamic)=4
- [hair] 頭(s) → R_Side_1(d) → R_Side_2(d) → R_Side_3(d) → R_Side_4(d)  segments(dynamic)=4
- [breast] 上半身2(s) → 左乳奶(d)  segments(dynamic)=1
- [breast] 上半身2(s) → 右乳奶(d)  segments(dynamic)=1

## Lucy18_V1: 36 rigid bodies, 17 joints
category counts: body=19, hair=15, breast=2
- body: group/non-collide sets: g1 nc=[1, 16] ×19
- hair: group/non-collide sets: g10 nc=[2, 9, 10, 11, 16] ×15
- breast: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2

| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |
|---|---|---|---|---|---|---|---|---|---|
| body | 19 | {'capsule': 19} | {'static': 19} | r/w 0.334~1.5; h 0.475~5.25; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| hair | 15 | {'capsule': 15} | {'dynamic': 15} | r/w 0.17; h 0.599~0.892; d - | 1 | 0.9 | 0.99 | 0 | 0 |
| breast | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.6; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |

| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|
| hair | 15 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 15} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 15} | {(0.0, 0.0, 0.0): 15} | {(0.0, 0.0, 0.0): 15} |
| breast | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(0.0, 0.0, 0.0): 2} |

chains (root → … ; mode letters s=static d=dynamic b=dyn+bone):
- [hair] 頭(s) → Hair_001_R(d) → Hair_002_R(d) → Hair_003_R(d) → Hair_004_R(d)  segments(dynamic)=4
- [hair] 頭(s) → Hair_001_L(d) → Hair_002_L(d) → Hair_003_L(d)  segments(dynamic)=3
- [hair] 頭(s) → Hair_004_L(d) → Hair_005_L(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair_001_N(d) → Hair_002_N(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair_007_R(d) → Hair_008_R(d)  segments(dynamic)=2
- [hair] 頭(s) → Hair_005_R.002(d) → Hair_006_R.001(d)  segments(dynamic)=2
- [breast] 上半身2(s) → 左乳奶(d)  segments(dynamic)=1
- [breast] 上半身2(s) → 右乳奶(d)  segments(dynamic)=1

## Own_TifaGantz: 75 rigid bodies, 56 joints
category counts: body=19, hair=52, breast=2, butt=2
- body: group/non-collide sets: g1 nc=[1, 16] ×19
- hair: group/non-collide sets: g10 nc=[2, 9, 10, 11, 16] ×52
- breast: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2
- butt: group/non-collide sets: g16 nc=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16] ×2

| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |
|---|---|---|---|---|---|---|---|---|---|
| body | 19 | {'capsule': 19} | {'static': 19} | r/w 0.226~1.5; h 0.5~5.73; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| hair | 52 | {'sphere': 1, 'capsule': 30, 'box': 21} | {'static': 1, 'dynamic': 51} | r/w 0~1; h 0.39~1; d 0.23 | 1 | 0.9 | 0.9 | 0 | 0 |
| breast | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.6; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |
| butt | 2 | {'sphere': 2} | {'dynamic': 2} | r/w 0.6; h -; d - | 1 | 0.5 | 0.5 | 0 | 0.5 |

| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|
| hair | 52 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 52} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 52} | {(0.0, 0.0, 0.0): 52} | {(0.0, 0.0, 0.0): 52} |
| breast | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(0.0, 0.0, 0.0): 2} |
| butt | 2 | {((0.0, 0.0, 0.0), (0.0, 0.0, 0.0)): 2} | {((-10.0, -10.0, -10.0), (10.0, 10.0, 10.0)): 2} | {(0.0, 0.0, 0.0): 2} | {(0.0, 0.0, 0.0): 2} |

chains (root → … ; mode letters s=static d=dynamic b=dyn+bone):
- [hair] 頭(s) → C_HairBase_a(s) …(branches)  segments(dynamic)=0
- [hair] C_HairBase_a(s) → L_HairD_a_Phy(d) → L_HairD_b_Phy(d) → L_HairD_c_Phy(d)  segments(dynamic)=3
- [hair] C_HairBase_a(s) → L_HairA_a_Phy(d) → L_HairA_b_Phy(d)  segments(dynamic)=2
- [hair] C_HairBase_a(s) → R_HairA_a_Phy(d) → R_HairA_b_Phy(d) → R_HairA_c_Phy(d)  segments(dynamic)=3
- [hair] C_HairBase_a(s) → R_PrplHairE_a_Phy(d) → R_PrplHairE_b_Phy(d) → R_PrplHairE_c_Phy(d) → R_PrplHairE_d_Phy(d) → R_PrplHairE_e_Phy(d) → R_PrplHairE_f_Phy(d) → R_PrplHairE_g_Phy(d) → R_PrplHairE_h_Phy(d)  segments(dynamic)=8
- [hair] C_HairBase_a(s) → L_HairC_a_Phy(d)  segments(dynamic)=1
- [hair] C_HairBase_a(s) → C_HairC_a_Phy(d) → C_HairC_b_Phy(d) → C_HairC_c_Phy(d)  segments(dynamic)=3
- [hair] C_HairBase_a(s) → L_PrplHairE_a_Phy(d) → L_PrplHairE_b_Phy(d) → L_PrplHairE_c_Phy(d) → L_PrplHairE_d_Phy(d) → L_PrplHairE_e_Phy(d) → L_PrplHairE_f_Phy(d) → L_PrplHairE_g_Phy(d) → L_PrplHairE_h_Phy(d)  segments(dynamic)=8
- [hair] C_HairBase_a(s) → R_HairC_a_Phy(d) → R_HairC_b_Phy(d)  segments(dynamic)=2
- [hair] C_HairBase_a(s) → C_HairB_a_Phy(d) → C_HairB_b_Phy(d)  segments(dynamic)=2
- [hair] C_HairBase_a(s) → C_HairA_a_Phy(d) → C_HairA_b_Phy(d)  segments(dynamic)=2
- [hair] C_HairBase_a(s) → C_PrplHairD_a_Phy(d) → C_PrplHairD_b_Phy(d) → C_PrplHairD_c_Phy(d) → C_PrplHairD_d_Phy(d) → C_PrplHairD_e_Phy(d) → C_PrplHairD_f_Phy(d) → C_PrplHairD_g_Phy(d) → C_PrplHairD_h_Phy(d)  segments(dynamic)=8
- [hair] C_HairBase_a(s) → R_HairD_a_Phy(d) → R_HairD_b_Phy(d) → R_HairD_c_Phy(d)  segments(dynamic)=3
- [hair] C_HairBase_a(s) → L_HairB_a_Phy(d) → L_HairB_b_Phy(d)  segments(dynamic)=2
- [hair] C_HairBase_a(s) → R_HairB_a_Phy(d) → R_HairB_b_Phy(d) → R_HairB_c_Phy(d) → R_HairB_d_Phy(d)  segments(dynamic)=4
- [butt] 下半身(s) → 左屁股(d)  segments(dynamic)=1
- [butt] 下半身(s) → 右屁股(d)  segments(dynamic)=1
- [breast] 上半身2(s) → 左乳奶(d)  segments(dynamic)=1
- [breast] 上半身2(s) → 右乳奶(d)  segments(dynamic)=1

## Own_inase430: 4 rigid bodies, 2 joints
category counts: other=4
- other: group/non-collide sets: g3 nc=[] ×4

| category | n | shapes | modes | size (r/w, h/…) range | mass | linD | angD | rest | fric |
|---|---|---|---|---|---|---|---|---|---|
| other | 4 | {'sphere': 4} | {'static': 2, 'dynamic': 2} | r/w 0.0794~0.227; h -; d - | 0.5~1 | 0.04~0.75 | 0.1~0.75 | 0 | 0.5 |

| joint category (by B) | n | move limits | rot limits min~max (deg) | spring T | spring R |
|---|---|---|---|---|---|
| other | 2 | {((-1.5, -1.5, -1.5), (1.5, 1.5, 1.5)): 2} | {((-15.0, -15.0, -15.0), (15.0, 15.0, 15.0)): 2} | {(100.0, 100.0, 100.0): 2} | {(100.0, 100.0, 100.0): 2} |

chains (root → … ; mode letters s=static d=dynamic b=dyn+bone):
- [other] 上半身2(s) → breast.L(d)  segments(dynamic)=1
- [other] 上半身2(s) → breast.R(d)  segments(dynamic)=1