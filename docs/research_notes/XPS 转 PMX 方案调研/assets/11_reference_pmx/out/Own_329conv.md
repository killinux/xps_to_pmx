# Own_329conv

E:/mywork/mymodel/Purifier (Inase)/329_converted.pmx

name='test' name_e='test eng'

comment:
~~~
exported by mmd_tools
~~~
comment_e:
~~~
exported by mmd_tools
~~~
V=112878 F=199734 Tex=10 Mat=15 Bone=177 Morph=0 Disp=2 RB=0 J=0 addUV=0 idx(v,t,m,b,mo,r)=4,1,1,2,1,1

## 1. Scale
bbox min=(-0.799, -0.003, -0.137) max=(0.799, 1.904, 0.144) size=(1.598, 1.907, 0.281) height=1.907 ground(minY)=-0.0028

| bone | pos | Y/height (from ground) |
|---|---|---|

## 2. Rest pose angles
| side | segment | deg below horizontal (or angle) | deg forward(-Z) |
|---|---|---|---|
| 左 | elbow bend(3D) | nan |  |
| 左 | knee bend(3D) | nan |  |
| 左 | leg spread (足→足首 from vertical, +outward) | - |  |
| 右 | elbow bend(3D) | nan |  |
| 右 | knee bend(3D) | nan |  |
| 右 | leg spread (足→足首 from vertical, +outward) | - |  |

## 3. Bones (full)
| # | name_j | name_e | parent | pos | flags | 層 | tail | 付与 | 軸 | ローカル軸 | IK | nV | Σw |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | root |  | - | (0.000, 0.084, 0.000) | RMVC | 0 | (0.00, 0.00, -0.50) |  |  |  |  | 0 | 0 |
| 1 | hip |  | root | (0.000, 1.180, -0.011) | RMVC | 0 | (-0.00, 0.02, 0.01) |  |  |  |  | 0 | 0 |
| 2 | pelvis |  | hip | (-0.000, 1.197, -0.012) | RMVC | 0 | (-0.00, -0.13, 0.03) |  |  |  |  | 11098 | 5336 |
| 3 | lThighBend |  | pelvis | (0.078, 1.095, 0.002) | RMVC | 0 | (0.01, -0.34, 0.01) |  |  |  |  | 3584 | 538 |
| 4 | lThighTwist |  | lThighBend | (0.082, 0.882, 0.006) | RMVC | 0 | (-0.01, 0.13, -0.00) |  |  |  |  | 4443 | 1470 |
| 5 | lShin |  | lThighBend | (0.092, 0.622, 0.011) | RMVC | 0 | lFoot |  |  |  |  | 5390 | 3104 |
| 6 | lFoot |  | lShin | (0.098, 0.167, 0.046) | RMVC | 0 | lMetatarsals |  |  |  |  | 3334 | 1037 |
| 7 | lMetatarsals |  | lFoot | (0.098, 0.167, 0.055) | RMVC | 0 | lToe |  |  |  |  | 2348 | 1113 |
| 8 | lToe |  | lMetatarsals | (0.102, 0.057, 0.026) | RMVC | 0 | (0.00, 0.00, -0.00) |  |  |  |  | 1960 | 297 |
| 9 | lSmallToe4 |  | lToe | (0.134, 0.056, 0.033) | RMVC | 0 | lSmallToe4_2 |  |  |  |  | 373 | 150 |
| 10 | lSmallToe4_2 |  | lSmallToe4 | (0.135, 0.051, 0.025) | RMVC | 0 | (0.00, -0.00, -0.01) |  |  |  |  | 627 | 540 |
| 11 | lSmallToe3 |  | lToe | (0.119, 0.058, 0.027) | RMVC | 0 | lSmallToe3_2 |  |  |  |  | 359 | 129 |
| 12 | lSmallToe3_2 |  | lSmallToe3 | (0.123, 0.052, 0.016) | RMVC | 0 | (0.00, -0.01, -0.01) |  |  |  |  | 585 | 526 |
| 13 | lSmallToe2 |  | lToe | (0.109, 0.061, 0.021) | RMVC | 0 | lSmallToe2_2 |  |  |  |  | 360 | 131 |
| 14 | lSmallToe2_2 |  | lSmallToe2 | (0.114, 0.053, 0.007) | RMVC | 0 | (0.00, -0.01, -0.01) |  |  |  |  | 584 | 520 |
| 15 | lSmallToe1 |  | lToe | (0.095, 0.060, 0.018) | RMVC | 0 | lSmallToe1_2 |  |  |  |  | 387 | 136 |
| 16 | lSmallToe1_2 |  | lSmallToe1 | (0.100, 0.053, 0.002) | RMVC | 0 | (0.01, -0.01, -0.02) |  |  |  |  | 612 | 534 |
| 17 | lBigToe |  | lToe | (0.074, 0.057, 0.017) | RMVC | 0 | lBigToe_2 |  |  |  |  | 587 | 257 |
| 18 | lBigToe_2 |  | lBigToe | (0.079, 0.048, -0.001) | RMVC | 0 | (0.01, -0.01, -0.02) |  |  |  |  | 771 | 642 |
| 19 | rThighBend |  | pelvis | (-0.078, 1.095, 0.002) | RMVC | 0 | (-0.01, -0.34, 0.01) |  |  |  |  | 4356 | 548 |
| 20 | rThighTwist |  | rThighBend | (-0.082, 0.882, 0.006) | RMVC | 0 | (0.01, 0.13, -0.00) |  |  |  |  | 4715 | 1471 |
| 21 | rShin |  | rThighBend | (-0.093, 0.622, 0.011) | RMVC | 0 | rFoot |  |  |  |  | 5390 | 3104 |
| 22 | rFoot |  | rShin | (-0.098, 0.167, 0.046) | RMVC | 0 | rMetatarsals |  |  |  |  | 3334 | 1037 |
| 23 | rMetatarsals |  | rFoot | (-0.098, 0.167, 0.055) | RMVC | 0 | rToe |  |  |  |  | 2349 | 1113 |
| 24 | rToe |  | rMetatarsals | (-0.102, 0.057, 0.026) | RMVC | 0 | (-0.00, 0.00, -0.00) |  |  |  |  | 1960 | 297 |
| 25 | rSmallToe4 |  | rToe | (-0.134, 0.056, 0.033) | RMVC | 0 | rSmallToe4_2 |  |  |  |  | 373 | 150 |
| 26 | rSmallToe4_2 |  | rSmallToe4 | (-0.135, 0.051, 0.025) | RMVC | 0 | (-0.00, -0.00, -0.01) |  |  |  |  | 627 | 540 |
| 27 | rSmallToe3 |  | rToe | (-0.119, 0.058, 0.027) | RMVC | 0 | rSmallToe3_2 |  |  |  |  | 359 | 129 |
| 28 | rSmallToe3_2 |  | rSmallToe3 | (-0.123, 0.052, 0.016) | RMVC | 0 | (-0.00, -0.01, -0.01) |  |  |  |  | 585 | 526 |
| 29 | rSmallToe2 |  | rToe | (-0.109, 0.061, 0.021) | RMVC | 0 | rSmallToe2_2 |  |  |  |  | 360 | 131 |
| 30 | rSmallToe2_2 |  | rSmallToe2 | (-0.114, 0.053, 0.007) | RMVC | 0 | (-0.00, -0.01, -0.01) |  |  |  |  | 584 | 520 |
| 31 | rSmallToe1 |  | rToe | (-0.095, 0.060, 0.018) | RMVC | 0 | rSmallToe1_2 |  |  |  |  | 387 | 136 |
| 32 | rSmallToe1_2 |  | rSmallToe1 | (-0.100, 0.053, 0.002) | RMVC | 0 | (-0.01, -0.01, -0.02) |  |  |  |  | 612 | 534 |
| 33 | rBigToe |  | rToe | (-0.074, 0.057, 0.017) | RMVC | 0 | rBigToe_2 |  |  |  |  | 587 | 257 |
| 34 | rBigToe_2 |  | rBigToe | (-0.079, 0.048, -0.001) | RMVC | 0 | (-0.01, -0.01, -0.02) |  |  |  |  | 771 | 642 |
| 35 | Anus |  | pelvis | (0.000, 1.040, 0.045) | RMVC | 0 | (0.00, -0.03, 0.03) |  |  |  |  | 2932 | 2752 |
| 36 | Genitals |  | pelvis | (0.000, 1.030, 0.006) | RMVC | 0 | (0.00, -0.03, -0.01) |  |  |  |  | 11930 | 11527 |
| 37 | abdomenLower |  | hip | (-0.000, 1.196, 0.004) | RMVC | 0 | abdomenUpper |  |  |  |  | 8136 | 3866 |
| 38 | abdomenUpper |  | abdomenLower | (-0.000, 1.270, -0.012) | RMVC | 0 | chestLower |  |  |  |  | 4184 | 1146 |
| 39 | chestLower |  | abdomenUpper | (-0.000, 1.342, -0.012) | RMVC | 0 | (0.00, 0.09, 0.06) |  |  |  |  | 8455 | 2894 |
| 40 | chestUpper |  | chestLower | (0.000, 1.463, 0.020) | RMVC | 0 | (-0.00, 0.13, 0.02) |  |  |  |  | 7715 | 3007 |
| 41 | lCollar |  | chestUpper | (0.034, 1.565, 0.038) | RMVC | 0 | lShldrBend |  |  |  |  | 5716 | 1010 |
| 42 | lShldrBend |  | lCollar | (0.146, 1.547, 0.050) | RMVC | 0 | (0.18, -0.00, 0.00) |  |  |  |  | 1583 | 570 |
| 43 | lShldrTwist |  | lShldrBend | (0.256, 1.549, 0.050) | RMVC | 0 | (-0.07, 0.00, -0.00) |  |  |  |  | 1879 | 734 |
| 44 | lForearmBend |  | lShldrBend | (0.391, 1.545, 0.052) | RMVC | 0 | (0.17, -0.01, -0.05) |  |  |  |  | 1999 | 729 |
| 45 | lForearmTwist |  | lForearmBend | (0.500, 1.543, 0.022) | RMVC | 0 | (-0.06, 0.00, 0.02) |  |  |  |  | 2002 | 729 |
| 46 | lHand |  | lForearmBend | (0.628, 1.535, -0.014) | RMVC | 0 | (0.01, 0.00, -0.00) |  |  |  |  | 1261 | 428 |
| 47 | lThumb1 |  | lHand | (0.642, 1.529, -0.030) | RMVC | 0 | lThumb2 |  |  |  |  | 777 | 319 |
| 48 | lThumb2 |  | lThumb1 | (0.663, 1.522, -0.063) | RMVC | 0 | lThumb3 |  |  |  |  | 641 | 276 |
| 49 | lThumb3 |  | lThumb2 | (0.685, 1.513, -0.080) | RMVC | 0 | (0.02, -0.01, -0.02) |  |  |  |  | 786 | 632 |
| 50 | lCarpal1 |  | lHand | (0.631, 1.539, -0.025) | RMVC | 0 | lIndex1 |  |  |  |  | 640 | 264 |
| 51 | lIndex1 |  | lCarpal1 | (0.703, 1.539, -0.046) | RMVC | 0 | lIndex2 |  |  |  |  | 602 | 264 |
| 52 | lIndex2 |  | lIndex1 | (0.741, 1.535, -0.053) | RMVC | 0 | lIndex3 |  |  |  |  | 440 | 185 |
| 53 | lIndex3 |  | lIndex2 | (0.762, 1.531, -0.055) | RMVC | 0 | (0.02, -0.00, -0.00) |  |  |  |  | 684 | 611 |
| 54 | lCarpal2 |  | lHand | (0.634, 1.540, -0.017) | RMVC | 0 | lMid1 |  |  |  |  | 540 | 194 |
| 55 | lMid1 |  | lCarpal2 | (0.707, 1.540, -0.026) | RMVC | 0 | lMid2 |  |  |  |  | 627 | 246 |
| 56 | lMid2 |  | lMid1 | (0.750, 1.538, -0.030) | RMVC | 0 | lMid3 |  |  |  |  | 416 | 199 |
| 57 | lMid3 |  | lMid2 | (0.775, 1.533, -0.032) | RMVC | 0 | (0.03, -0.01, -0.00) |  |  |  |  | 684 | 609 |
| 58 | lCarpal3 |  | lHand | (0.635, 1.540, -0.007) | RMVC | 0 | lRing1 |  |  |  |  | 576 | 199 |
| 59 | lRing1 |  | lCarpal3 | (0.702, 1.539, -0.008) | RMVC | 0 | lRing2 |  |  |  |  | 665 | 244 |
| 60 | lRing2 |  | lRing1 | (0.742, 1.536, -0.007) | RMVC | 0 | lRing3 |  |  |  |  | 424 | 198 |
| 61 | lRing3 |  | lRing2 | (0.764, 1.532, -0.006) | RMVC | 0 | (0.02, -0.00, 0.00) |  |  |  |  | 684 | 608 |
| 62 | lCarpal4 |  | lHand | (0.635, 1.540, 0.002) | RMVC | 0 | lPinky1 |  |  |  |  | 480 | 213 |
| 63 | lPinky1 |  | lCarpal4 | (0.698, 1.534, 0.012) | RMVC | 0 | lPinky2 |  |  |  |  | 571 | 238 |
| 64 | lPinky2 |  | lPinky1 | (0.725, 1.531, 0.014) | RMVC | 0 | lPinky3 |  |  |  |  | 418 | 208 |
| 65 | lPinky3 |  | lPinky2 | (0.742, 1.529, 0.016) | RMVC | 0 | (0.02, -0.00, 0.00) |  |  |  |  | 684 | 606 |
| 66 | rCollar |  | chestUpper | (-0.034, 1.565, 0.038) | RMVC | 0 | rShldrBend |  |  |  |  | 4537 | 753 |
| 67 | rShldrBend |  | rCollar | (-0.146, 1.547, 0.050) | RMVC | 0 | (-0.18, 0.00, 0.00) |  |  |  |  | 1583 | 570 |
| 68 | rShldrTwist |  | rShldrBend | (-0.256, 1.549, 0.050) | RMVC | 0 | (0.07, 0.00, -0.00) |  |  |  |  | 1879 | 734 |
| 69 | rForearmBend |  | rShldrBend | (-0.391, 1.545, 0.052) | RMVC | 0 | (-0.17, -0.01, -0.05) |  |  |  |  | 2820 | 888 |
| 70 | rForearmTwist |  | rForearmBend | (-0.500, 1.543, 0.022) | RMVC | 0 | (0.06, 0.00, 0.02) |  |  |  |  | 2822 | 1391 |
| 71 | rHand |  | rForearmBend | (-0.628, 1.536, -0.015) | RMVC | 0 | (-0.01, 0.00, -0.00) |  |  |  |  | 1266 | 427 |
| 72 | rThumb1 |  | rHand | (-0.642, 1.529, -0.030) | RMVC | 0 | rThumb2 |  |  |  |  | 776 | 319 |
| 73 | rThumb2 |  | rThumb1 | (-0.663, 1.522, -0.064) | RMVC | 0 | rThumb3 |  |  |  |  | 641 | 276 |
| 74 | rThumb3 |  | rThumb2 | (-0.685, 1.514, -0.080) | RMVC | 0 | (-0.02, -0.01, -0.02) |  |  |  |  | 786 | 632 |
| 75 | rCarpal1 |  | rHand | (-0.631, 1.539, -0.026) | RMVC | 0 | rIndex1 |  |  |  |  | 640 | 264 |
| 76 | rIndex1 |  | rCarpal1 | (-0.702, 1.539, -0.046) | RMVC | 0 | rIndex2 |  |  |  |  | 602 | 264 |
| 77 | rIndex2 |  | rIndex1 | (-0.741, 1.534, -0.053) | RMVC | 0 | rIndex3 |  |  |  |  | 440 | 185 |
| 78 | rIndex3 |  | rIndex2 | (-0.762, 1.531, -0.056) | RMVC | 0 | (-0.02, -0.00, -0.00) |  |  |  |  | 684 | 611 |
| 79 | rCarpal2 |  | rHand | (-0.634, 1.540, -0.017) | RMVC | 0 | rMid1 |  |  |  |  | 540 | 194 |
| 80 | rMid1 |  | rCarpal2 | (-0.706, 1.540, -0.027) | RMVC | 0 | rMid2 |  |  |  |  | 627 | 246 |
| 81 | rMid2 |  | rMid1 | (-0.750, 1.539, -0.030) | RMVC | 0 | rMid3 |  |  |  |  | 416 | 199 |
| 82 | rMid3 |  | rMid2 | (-0.775, 1.533, -0.032) | RMVC | 0 | (-0.03, -0.01, -0.00) |  |  |  |  | 684 | 609 |
| 83 | rCarpal3 |  | rHand | (-0.635, 1.540, -0.008) | RMVC | 0 | rRing1 |  |  |  |  | 576 | 199 |
| 84 | rRing1 |  | rCarpal3 | (-0.702, 1.540, -0.008) | RMVC | 0 | rRing2 |  |  |  |  | 665 | 244 |
| 85 | rRing2 |  | rRing1 | (-0.742, 1.536, -0.007) | RMVC | 0 | rRing3 |  |  |  |  | 424 | 198 |
| 86 | rRing3 |  | rRing2 | (-0.764, 1.532, -0.006) | RMVC | 0 | (-0.02, -0.00, 0.00) |  |  |  |  | 684 | 608 |
| 87 | rCarpal4 |  | rHand | (-0.635, 1.540, 0.001) | RMVC | 0 | rPinky1 |  |  |  |  | 480 | 213 |
| 88 | rPinky1 |  | rCarpal4 | (-0.697, 1.535, 0.012) | RMVC | 0 | rPinky2 |  |  |  |  | 571 | 238 |
| 89 | rPinky2 |  | rPinky1 | (-0.725, 1.532, 0.013) | RMVC | 0 | rPinky3 |  |  |  |  | 418 | 208 |
| 90 | rPinky3 |  | rPinky2 | (-0.742, 1.529, 0.015) | RMVC | 0 | (-0.02, -0.00, 0.00) |  |  |  |  | 684 | 606 |
| 91 | neckLower |  | chestUpper | (-0.000, 1.637, 0.035) | RMVC | 0 | neckUpper |  |  |  |  | 3157 | 384 |
| 92 | neckUpper |  | neckLower | (-0.000, 1.668, 0.021) | RMVC | 0 | head |  |  |  |  | 1934 | 427 |
| 93 | head |  | neckUpper | (-0.000, 1.714, 0.013) | RMVC | 0 | (-0.00, 0.04, -0.08) |  |  |  |  | 20414 | 16227 |
| 94 | upperTeeth |  | head | (-0.000, 1.712, -0.055) | RMVC | 0 | (0.00, -0.04, 0.02) |  |  |  |  | 3916 | 3828 |
| 95 | lowerJaw |  | head | (0.000, 1.726, 0.004) | RMVC | 0 | (0.00, -0.03, -0.07) |  |  |  |  | 1677 | 636 |
| 96 | lowerTeeth |  | lowerJaw | (0.000, 1.701, -0.052) | RMVC | 0 | tongue01 |  |  |  |  | 3990 | 3774 |
| 97 | tongue01 |  | lowerTeeth | (0.000, 1.688, -0.034) | RMVC | 0 | tongue02 |  |  |  |  | 439 | 134 |
| 98 | tongue02 |  | tongue01 | (0.000, 1.697, -0.044) | RMVC | 0 | tongue03 |  |  |  |  | 523 | 136 |
| 99 | tongue03 |  | tongue02 | (0.000, 1.699, -0.056) | RMVC | 0 | tongue04 |  |  |  |  | 439 | 103 |
| 100 | tongue04 |  | tongue03 | (0.000, 1.699, -0.067) | RMVC | 0 | (0.00, -0.00, -0.01) |  |  |  |  | 314 | 111 |
| 101 | lNasolabialLower |  | lowerJaw | (0.027, 1.687, -0.066) | RMVC | 0 | (0.03, -0.01, -0.00) |  |  |  |  | 248 | 57 |
| 102 | rNasolabialLower |  | lowerJaw | (-0.027, 1.687, -0.066) | RMVC | 0 | (-0.03, -0.01, -0.00) |  |  |  |  | 248 | 57 |
| 103 | lNasolabialMouthCorner |  | lowerJaw | (0.036, 1.705, -0.072) | RMVC | 0 | (0.04, 0.01, -0.01) |  |  |  |  | 227 | 43 |
| 104 | rNasolabialMouthCorner |  | lowerJaw | (-0.036, 1.705, -0.072) | RMVC | 0 | (-0.04, 0.01, -0.01) |  |  |  |  | 227 | 43 |
| 105 | lLipCorner |  | lowerJaw | (0.027, 1.703, -0.074) | RMVC | 0 | (0.03, 0.01, -0.01) |  |  |  |  | 455 | 96 |
| 106 | lLipLowerOuter |  | lowerJaw | (0.018, 1.696, -0.079) | RMVC | 0 | (0.02, 0.00, -0.01) |  |  |  |  | 314 | 89 |
| 107 | lLipLowerInner |  | lowerJaw | (0.010, 1.694, -0.080) | RMVC | 0 | (0.01, -0.00, -0.02) |  |  |  |  | 320 | 66 |
| 108 | LipLowerMiddle |  | lowerJaw | (0.000, 1.692, -0.083) | RMVC | 0 | (-0.00, -0.00, -0.02) |  |  |  |  | 526 | 175 |
| 109 | rLipLowerInner |  | lowerJaw | (-0.010, 1.694, -0.080) | RMVC | 0 | (-0.01, -0.00, -0.02) |  |  |  |  | 321 | 67 |
| 110 | rLipLowerOuter |  | lowerJaw | (-0.018, 1.696, -0.079) | RMVC | 0 | (-0.02, 0.00, -0.01) |  |  |  |  | 314 | 90 |
| 111 | rLipCorner |  | lowerJaw | (-0.027, 1.703, -0.074) | RMVC | 0 | (-0.03, 0.01, -0.01) |  |  |  |  | 455 | 96 |
| 112 | LipBelow |  | lowerJaw | (0.000, 1.680, -0.079) | RMVC | 0 | (-0.00, -0.01, -0.02) |  |  |  |  | 277 | 94 |
| 113 | Chin |  | lowerJaw | (0.000, 1.671, -0.068) | RMVC | 0 | (-0.00, -0.02, -0.00) |  |  |  |  | 330 | 121 |
| 114 | lCheekLower |  | lowerJaw | (0.052, 1.709, -0.059) | RMVC | 0 | (0.05, 0.01, 0.01) |  |  |  |  | 284 | 54 |
| 115 | rCheekLower |  | lowerJaw | (-0.052, 1.709, -0.059) | RMVC | 0 | (-0.05, 0.01, 0.01) |  |  |  |  | 274 | 54 |
| 116 | BelowJaw |  | lowerJaw | (0.000, 1.664, -0.042) | RMVC | 0 | (-0.00, -0.03, 0.02) |  |  |  |  | 592 | 134 |
| 117 | lJawClench |  | lowerJaw | (0.057, 1.709, -0.020) | RMVC | 0 | (0.06, 0.01, 0.04) |  |  |  |  | 333 | 52 |
| 118 | rJawClench |  | lowerJaw | (-0.057, 1.709, -0.020) | RMVC | 0 | (-0.06, 0.01, 0.04) |  |  |  |  | 263 | 42 |
| 119 | rBrowInner |  | head | (-0.024, 1.784, -0.085) | RMVC | 0 | (-0.02, 0.03, -0.01) |  |  |  |  | 337 | 74 |
| 120 | rBrowMid |  | head | (-0.040, 1.784, -0.082) | RMVC | 0 | (-0.04, 0.04, -0.01) |  |  |  |  | 381 | 92 |
| 121 | rBrowOuter |  | head | (-0.051, 1.780, -0.073) | RMVC | 0 | (-0.05, 0.03, -0.00) |  |  |  |  | 398 | 96 |
| 122 | lBrowInner |  | head | (0.024, 1.784, -0.085) | RMVC | 0 | (0.02, 0.03, -0.01) |  |  |  |  | 337 | 74 |
| 123 | lBrowMid |  | head | (0.040, 1.784, -0.082) | RMVC | 0 | (0.04, 0.04, -0.01) |  |  |  |  | 382 | 93 |
| 124 | lBrowOuter |  | head | (0.051, 1.780, -0.072) | RMVC | 0 | (0.05, 0.03, -0.00) |  |  |  |  | 398 | 96 |
| 125 | CenterBrow |  | head | (0.000, 1.783, -0.092) | RMVC | 0 | (0.00, 0.03, -0.02) |  |  |  |  | 395 | 116 |
| 126 | MidNoseBridge |  | head | (0.000, 1.762, -0.088) | RMVC | 0 | (0.00, 0.01, -0.02) |  |  |  |  | 203 | 26 |
| 127 | lEyelidInner |  | head | (0.021, 1.765, -0.075) | RMVC | 0 | (0.02, 0.02, -0.00) |  |  |  |  | 423 | 125 |
| 128 | lEyelidUpper |  | head | (0.034, 1.767, -0.059) | RMVC | 0 | (-0.00, 0.00, -0.01) |  |  |  |  | 269 | 93 |
| 129 | lEyelidUpperInner |  | lEyelidUpper | (0.021, 1.768, -0.076) | RMVC | 0 | (-0.01, -0.00, -0.00) |  |  |  |  | 258 | 88 |
| 130 | lEyelidUpperOuter |  | lEyelidUpper | (0.046, 1.771, -0.073) | RMVC | 0 | (0.01, 0.00, 0.00) |  |  |  |  | 362 | 113 |
| 131 | lEyelidOuter |  | head | (0.047, 1.769, -0.071) | RMVC | 0 | (0.05, 0.02, 0.00) |  |  |  |  | 402 | 149 |
| 132 | lEyelidLower |  | head | (0.034, 1.766, -0.059) | RMVC | 0 | (0.00, -0.00, -0.01) |  |  |  |  | 185 | 63 |
| 133 | lEyelidLowerOuter |  | lEyelidLower | (0.047, 1.765, -0.071) | RMVC | 0 | (0.01, 0.00, 0.00) |  |  |  |  | 324 | 71 |
| 134 | lEyelidLowerInner |  | lEyelidLower | (0.022, 1.762, -0.075) | RMVC | 0 | (-0.01, -0.00, -0.00) |  |  |  |  | 255 | 49 |
| 135 | rEyelidInner |  | head | (-0.021, 1.765, -0.075) | RMVC | 0 | (-0.02, 0.02, -0.00) |  |  |  |  | 423 | 125 |
| 136 | rEyelidUpper |  | head | (-0.034, 1.767, -0.059) | RMVC | 0 | (0.00, 0.00, -0.01) |  |  |  |  | 271 | 92 |
| 137 | rEyelidUpperInner |  | rEyelidUpper | (-0.021, 1.768, -0.076) | RMVC | 0 | (0.01, -0.00, -0.00) |  |  |  |  | 258 | 88 |
| 138 | rEyelidUpperOuter |  | rEyelidUpper | (-0.046, 1.771, -0.073) | RMVC | 0 | (-0.01, 0.00, 0.00) |  |  |  |  | 362 | 114 |
| 139 | rEyelidOuter |  | head | (-0.047, 1.769, -0.071) | RMVC | 0 | (-0.05, 0.02, 0.00) |  |  |  |  | 403 | 150 |
| 140 | rEyelidLower |  | head | (-0.034, 1.766, -0.059) | RMVC | 0 | (-0.00, -0.00, -0.01) |  |  |  |  | 185 | 63 |
| 141 | rEyelidLowerOuter |  | rEyelidLower | (-0.047, 1.765, -0.071) | RMVC | 0 | (-0.01, 0.00, 0.00) |  |  |  |  | 324 | 70 |
| 142 | rEyelidLowerInner |  | rEyelidLower | (-0.022, 1.762, -0.075) | RMVC | 0 | (0.01, -0.00, -0.00) |  |  |  |  | 255 | 49 |
| 143 | lSquintInner |  | head | (0.028, 1.754, -0.077) | RMVC | 0 | (0.03, 0.01, -0.01) |  |  |  |  | 229 | 60 |
| 144 | lSquintOuter |  | head | (0.048, 1.758, -0.070) | RMVC | 0 | (0.05, 0.01, 0.00) |  |  |  |  | 213 | 57 |
| 145 | rSquintInner |  | head | (-0.028, 1.754, -0.077) | RMVC | 0 | (-0.03, 0.01, -0.01) |  |  |  |  | 229 | 60 |
| 146 | rSquintOuter |  | head | (-0.049, 1.758, -0.070) | RMVC | 0 | (-0.05, 0.01, 0.00) |  |  |  |  | 213 | 57 |
| 147 | lCheekUpper |  | head | (0.050, 1.739, -0.071) | RMVC | 0 | (0.05, -0.01, 0.00) |  |  |  |  | 436 | 112 |
| 148 | rCheekUpper |  | head | (-0.050, 1.739, -0.071) | RMVC | 0 | (-0.05, -0.01, 0.00) |  |  |  |  | 436 | 112 |
| 149 | Nose |  | head | (0.000, 1.729, -0.098) | RMVC | 0 | (0.00, -0.02, -0.03) |  |  |  |  | 881 | 320 |
| 150 | lNostril |  | head | (0.009, 1.727, -0.093) | RMVC | 0 | (0.01, -0.02, -0.02) |  |  |  |  | 515 | 262 |
| 151 | rNostril |  | head | (-0.009, 1.727, -0.093) | RMVC | 0 | (-0.01, -0.02, -0.02) |  |  |  |  | 515 | 262 |
| 152 | lLipBelowNose |  | head | (0.011, 1.717, -0.083) | RMVC | 0 | (0.01, -0.03, -0.01) |  |  |  |  | 261 | 29 |
| 153 | rLipBelowNose |  | head | (-0.012, 1.717, -0.083) | RMVC | 0 | (-0.01, -0.03, -0.01) |  |  |  |  | 255 | 29 |
| 154 | lLipNasolabialCrease |  | head | (0.021, 1.711, -0.085) | RMVC | 0 | (0.02, -0.04, -0.01) |  |  |  |  | 202 | 30 |
| 155 | rLipNasolabialCrease |  | head | (-0.022, 1.711, -0.085) | RMVC | 0 | (-0.02, -0.04, -0.01) |  |  |  |  | 202 | 30 |
| 156 | lNasolabialUpper |  | head | (0.017, 1.744, -0.084) | RMVC | 0 | (0.02, -0.01, -0.01) |  |  |  |  | 282 | 48 |
| 157 | rNasolabialUpper |  | head | (-0.017, 1.744, -0.084) | RMVC | 0 | (-0.02, -0.01, -0.01) |  |  |  |  | 282 | 48 |
| 158 | lNasolabialMiddle |  | head | (0.027, 1.726, -0.082) | RMVC | 0 | (0.03, -0.02, -0.01) |  |  |  |  | 298 | 72 |
| 159 | rNasolabialMiddle |  | head | (-0.027, 1.726, -0.082) | RMVC | 0 | (-0.03, -0.02, -0.01) |  |  |  |  | 298 | 72 |
| 160 | LipUpperMiddle |  | head | (-0.000, 1.708, -0.088) | RMVC | 0 | (0.00, -0.04, -0.02) |  |  |  |  | 611 | 218 |
| 161 | lLipUpperOuter |  | head | (0.018, 1.705, -0.082) | RMVC | 0 | (0.02, -0.04, -0.01) |  |  |  |  | 336 | 82 |
| 162 | lLipUpperInner |  | head | (0.010, 1.705, -0.084) | RMVC | 0 | (0.01, -0.04, -0.01) |  |  |  |  | 415 | 100 |
| 163 | rLipUpperInner |  | head | (-0.010, 1.705, -0.084) | RMVC | 0 | (-0.01, -0.04, -0.01) |  |  |  |  | 414 | 99 |
| 164 | rLipUpperOuter |  | head | (-0.018, 1.705, -0.082) | RMVC | 0 | (-0.02, -0.04, -0.01) |  |  |  |  | 333 | 81 |
| 165 | lEye |  | head | (0.032, 1.768, -0.059) | RMVC | 0 | (0.03, 0.02, 0.01) |  |  |  |  | 914 | 914 |
| 166 | rEye |  | head | (-0.032, 1.768, -0.059) | RMVC | 0 | (-0.03, 0.02, 0.01) |  |  |  |  | 914 | 914 |
| 167 | lEar |  | head | (0.068, 1.753, -0.004) | RMVC | 0 | (0.07, 0.00, 0.07) |  |  |  |  | 1126 | 473 |
| 168 | rEar |  | head | (-0.068, 1.753, -0.004) | RMVC | 0 | (-0.07, 0.00, 0.07) |  |  |  |  | 1043 | 461 |
| 169 | head hair left 1 |  | head | (0.076, 1.768, -0.024) | RMVC | 0 | head hair left 2 |  |  |  |  | 512 | 218 |
| 170 | head hair left 2 |  | head hair left 1 | (0.072, 1.718, -0.014) | RMVC | 0 | (-0.00, -0.05, 0.01) |  |  |  |  | 400 | 217 |
| 171 | head hair front right 1 |  | head | (-0.023, 1.837, -0.089) | RMVC | 0 | head hair front right 2 |  |  |  |  | 752 | 370 |
| 172 | head hair front right 2 |  | head hair front right 1 | (-0.064, 1.766, -0.079) | RMVC | 0 | (-0.04, -0.07, 0.01) |  |  |  |  | 501 | 235 |
| 173 | head hair front right 3 |  | head | (-0.078, 1.736, -0.045) | RMVC | 0 | head hair front right 4 |  |  |  |  | 814 | 309 |
| 174 | head hair front right 4 |  | head hair front right 3 | (-0.068, 1.674, -0.040) | RMVC | 0 | (0.01, -0.06, 0.01) |  |  |  |  | 583 | 334 |
| 175 | lPectoral |  | chestLower | (0.030, 1.422, 0.064) | RMVC | 0 | (0.03, -0.01, 0.01) |  |  |  |  | 2500 | 1228 |
| 176 | rPectoral |  | chestLower | (-0.030, 1.422, 0.064) | RMVC | 0 | (-0.03, -0.01, 0.01) |  |  |  |  | 2500 | 1225 |

Standard/semi-standard presence: 全ての親:-, センター:-, グルーブ:-, 腰:-, 上半身:-, 上半身1:-, 上半身2:-, 上半身3:-, 下半身:-, 首:-, 首1:-, 頭:-, 両目:-, 左目:-, 右目:-, 操作中心:-, 左肩P:-, 右肩P:-, 左肩:-, 右肩:-, 左肩C:-, 右肩C:-, 左腕:-, 右腕:-, 左腕捩:-, 右腕捩:-, 左腕捩1:-, 右腕捩1:-, 左腕捩2:-, 右腕捩2:-, 左腕捩3:-, 右腕捩3:-, 左ひじ:-, 右ひじ:-, 左手捩:-, 右手捩:-, 左手捩1:-, 右手捩1:-, 左手捩2:-, 右手捩2:-, 左手捩3:-, 右手捩3:-, 左手首:-, 右手首:-, 左ダミー:-, 右ダミー:-, 左親指０:-, 右親指０:-, 左親指１:-, 右親指１:-, 左親指２:-, 右親指２:-, 左人指１:-, 右人指１:-, 左人指２:-, 右人指２:-, 左人指３:-, 右人指３:-, 左中指１:-, 右中指１:-, 左中指２:-, 右中指２:-, 左中指３:-, 右中指３:-, 左薬指１:-, 右薬指１:-, 左薬指２:-, 右薬指２:-, 左薬指３:-, 右薬指３:-, 左小指１:-, 右小指１:-, 左小指２:-, 右小指２:-, 左小指３:-, 右小指３:-, 左足:-, 右足:-, 左ひざ:-, 右ひざ:-, 左足首:-, 右足首:-, 左つま先:-, 右つま先:-, 左足D:-, 右足D:-, 左ひざD:-, 右ひざD:-, 左足首D:-, 右足首D:-, 左足先EX:-, 右足先EX:-, 腰キャンセル左:-, 腰キャンセル右:-, 左足IK親:-, 右足IK親:-, 左足ＩＫ:-, 右足ＩＫ:-, 左つま先ＩＫ:-, 右つま先ＩＫ:-

## 5. Weights
weight types: BDEF1=46727 BDEF2=27719 BDEF4=38432 SDEF=0; distinct influences/vertex: {1: 46727, 2: 27719, 3: 24750, 4: 13682}; sum!=1: 0; negative: 0

| # | bone | nV(w>0) | Σw | ymin | ymax |
|---|---|---|---|---|---|
| 93 | head | 20414 | 16226.6 | 1.62 | 1.90 |
| 36 | Genitals | 11930 | 11527.0 | 1.02 | 1.11 |
| 2 | pelvis | 11098 | 5336.1 | 0.91 | 1.26 |
| 39 | chestLower | 8455 | 2893.5 | 1.25 | 1.60 |
| 37 | abdomenLower | 8136 | 3866.2 | 1.08 | 1.35 |
| 40 | chestUpper | 7715 | 3006.6 | 1.40 | 1.72 |
| 41 | lCollar | 5716 | 1010.0 | 1.33 | 1.66 |
| 21 | rShin | 5390 | 3103.8 | 0.06 | 0.86 |
| 5 | lShin | 5390 | 3103.6 | 0.06 | 0.86 |
| 20 | rThighTwist | 4715 | 1471.2 | 0.47 | 1.21 |
| 66 | rCollar | 4537 | 753.2 | 1.33 | 1.66 |
| 4 | lThighTwist | 4443 | 1469.8 | 0.47 | 1.20 |
| 19 | rThighBend | 4356 | 548.1 | 0.72 | 1.22 |
| 38 | abdomenUpper | 4184 | 1146.4 | 1.22 | 1.45 |
| 96 | lowerTeeth | 3990 | 3774.2 | 1.69 | 1.71 |
| 94 | upperTeeth | 3916 | 3827.9 | 1.70 | 1.72 |
| 3 | lThighBend | 3584 | 538.3 | 0.72 | 1.22 |
| 6 | lFoot | 3334 | 1036.5 | 0.06 | 0.28 |
| 22 | rFoot | 3334 | 1036.8 | 0.06 | 0.28 |
| 91 | neckLower | 3157 | 384.1 | 1.56 | 1.69 |
| 35 | Anus | 2932 | 2751.9 | 1.03 | 1.10 |
| 70 | rForearmTwist | 2822 | 1391.2 | 1.50 | 1.58 |
| 69 | rForearmBend | 2820 | 887.6 | 1.50 | 1.58 |
| 176 | rPectoral | 2500 | 1224.5 | 1.36 | 1.58 |
| 175 | lPectoral | 2500 | 1228.5 | 1.36 | 1.58 |
| 23 | rMetatarsals | 2349 | 1112.9 | -0.00 | 0.22 |
| 7 | lMetatarsals | 2348 | 1113.4 | -0.00 | 0.22 |
| 45 | lForearmTwist | 2002 | 729.1 | 1.50 | 1.58 |
| 44 | lForearmBend | 1999 | 728.8 | 1.50 | 1.58 |
| 8 | lToe | 1960 | 297.2 | -0.00 | 0.11 |
| 24 | rToe | 1960 | 297.3 | -0.00 | 0.11 |
| 92 | neckUpper | 1934 | 426.6 | 1.60 | 1.77 |
| 43 | lShldrTwist | 1879 | 734.5 | 1.49 | 1.59 |
| 68 | rShldrTwist | 1879 | 734.5 | 1.49 | 1.59 |
| 95 | lowerJaw | 1677 | 635.9 | 1.63 | 1.74 |
| 67 | rShldrBend | 1583 | 569.8 | 1.47 | 1.60 |
| 42 | lShldrBend | 1583 | 569.8 | 1.47 | 1.60 |
| 71 | rHand | 1266 | 426.9 | 1.51 | 1.56 |
| 46 | lHand | 1261 | 427.6 | 1.51 | 1.56 |
| 167 | lEar | 1126 | 472.8 | 1.71 | 1.79 |
| 168 | rEar | 1043 | 461.3 | 1.71 | 1.79 |
| 165 | lEye | 914 | 914.0 | 1.75 | 1.79 |
| 166 | rEye | 914 | 914.0 | 1.75 | 1.79 |
| 149 | Nose | 881 | 320.4 | 1.71 | 1.76 |
| 173 | head hair front right 3 | 814 | 309.1 | 1.59 | 1.80 |
| 49 | lThumb3 | 786 | 631.8 | 1.50 | 1.53 |
| 74 | rThumb3 | 786 | 631.8 | 1.50 | 1.53 |
| 47 | lThumb1 | 777 | 318.8 | 1.51 | 1.55 |
| 72 | rThumb1 | 776 | 318.6 | 1.51 | 1.55 |
| 34 | rBigToe_2 | 771 | 642.3 | -0.00 | 0.07 |
| 18 | lBigToe_2 | 771 | 642.4 | -0.00 | 0.07 |
| 171 | head hair front right 1 | 752 | 370.0 | 1.68 | 1.88 |
| 78 | rIndex3 | 684 | 611.3 | 1.52 | 1.54 |
| 65 | lPinky3 | 684 | 605.9 | 1.52 | 1.54 |
| 86 | rRing3 | 684 | 607.6 | 1.52 | 1.54 |
| 82 | rMid3 | 684 | 609.3 | 1.53 | 1.54 |
| 57 | lMid3 | 684 | 609.3 | 1.53 | 1.54 |
| 53 | lIndex3 | 684 | 611.3 | 1.52 | 1.54 |
| 61 | lRing3 | 684 | 607.6 | 1.52 | 1.54 |
| 90 | rPinky3 | 684 | 605.9 | 1.52 | 1.54 |
| 84 | rRing1 | 665 | 244.1 | 1.52 | 1.55 |
| 59 | lRing1 | 665 | 244.1 | 1.52 | 1.55 |
| 73 | rThumb2 | 641 | 276.1 | 1.50 | 1.54 |
| 48 | lThumb2 | 641 | 276.1 | 1.50 | 1.54 |
| 75 | rCarpal1 | 640 | 264.1 | 1.52 | 1.56 |
| 50 | lCarpal1 | 640 | 264.1 | 1.51 | 1.56 |
| 10 | lSmallToe4_2 | 627 | 539.8 | -0.00 | 0.07 |
| 80 | rMid1 | 627 | 246.1 | 1.53 | 1.55 |
| 55 | lMid1 | 627 | 246.1 | 1.52 | 1.55 |
| 26 | rSmallToe4_2 | 627 | 539.7 | -0.00 | 0.07 |
| 16 | lSmallToe1_2 | 612 | 533.9 | -0.00 | 0.08 |
| 32 | rSmallToe1_2 | 612 | 533.9 | -0.00 | 0.08 |
| 160 | LipUpperMiddle | 611 | 218.2 | 1.70 | 1.73 |
| 51 | lIndex1 | 602 | 264.4 | 1.52 | 1.55 |
| 76 | rIndex1 | 602 | 264.4 | 1.52 | 1.55 |
| 116 | BelowJaw | 592 | 134.5 | 1.65 | 1.72 |
| 33 | rBigToe | 587 | 256.6 | -0.00 | 0.08 |
| 17 | lBigToe | 587 | 256.6 | -0.00 | 0.08 |
| 28 | rSmallToe3_2 | 585 | 526.0 | -0.00 | 0.07 |
| 12 | lSmallToe3_2 | 585 | 526.0 | -0.00 | 0.07 |
| 14 | lSmallToe2_2 | 584 | 520.2 | -0.00 | 0.07 |
| 30 | rSmallToe2_2 | 584 | 520.2 | -0.00 | 0.07 |
| 174 | head hair front right 4 | 583 | 334.5 | 1.59 | 1.77 |
| 58 | lCarpal3 | 576 | 199.3 | 1.52 | 1.56 |
| 83 | rCarpal3 | 576 | 199.3 | 1.52 | 1.56 |
| 88 | rPinky1 | 571 | 237.6 | 1.52 | 1.55 |
| 63 | lPinky1 | 571 | 237.6 | 1.52 | 1.55 |
| 54 | lCarpal2 | 540 | 193.9 | 1.52 | 1.56 |
| 79 | rCarpal2 | 540 | 193.9 | 1.52 | 1.56 |
| 108 | LipLowerMiddle | 526 | 175.3 | 1.68 | 1.70 |
| 98 | tongue02 | 523 | 136.4 | 1.69 | 1.71 |
| 150 | lNostril | 515 | 262.4 | 1.71 | 1.75 |
| 151 | rNostril | 515 | 262.4 | 1.71 | 1.75 |
| 169 | head hair left 1 | 512 | 218.0 | 1.65 | 1.79 |
| 172 | head hair front right 2 | 501 | 235.2 | 1.68 | 1.87 |
| 87 | rCarpal4 | 480 | 212.5 | 1.52 | 1.55 |
| 62 | lCarpal4 | 480 | 212.5 | 1.52 | 1.55 |
| 105 | lLipCorner | 455 | 96.2 | 1.68 | 1.71 |
| 111 | rLipCorner | 455 | 96.0 | 1.68 | 1.71 |
| 52 | lIndex2 | 440 | 185.2 | 1.52 | 1.55 |
| 77 | rIndex2 | 440 | 185.2 | 1.52 | 1.54 |
| 99 | tongue03 | 439 | 102.9 | 1.69 | 1.71 |
| 97 | tongue01 | 439 | 133.9 | 1.69 | 1.71 |
| 147 | lCheekUpper | 436 | 112.4 | 1.70 | 1.78 |
| 148 | rCheekUpper | 436 | 112.4 | 1.70 | 1.78 |
| 85 | rRing2 | 424 | 197.9 | 1.52 | 1.55 |
| 60 | lRing2 | 424 | 197.9 | 1.52 | 1.55 |
| 127 | lEyelidInner | 423 | 125.4 | 1.75 | 1.78 |
| 135 | rEyelidInner | 423 | 125.4 | 1.75 | 1.78 |
| 64 | lPinky2 | 418 | 208.1 | 1.52 | 1.54 |
| 89 | rPinky2 | 418 | 208.1 | 1.52 | 1.54 |
| 81 | rMid2 | 416 | 199.0 | 1.53 | 1.55 |
| 56 | lMid2 | 416 | 199.0 | 1.53 | 1.55 |
| 162 | lLipUpperInner | 415 | 99.7 | 1.70 | 1.72 |
| 163 | rLipUpperInner | 414 | 99.4 | 1.70 | 1.72 |
| 139 | rEyelidOuter | 403 | 149.8 | 1.76 | 1.78 |
| 131 | lEyelidOuter | 402 | 149.4 | 1.76 | 1.78 |
| 170 | head hair left 2 | 400 | 216.7 | 1.65 | 1.78 |
| 124 | lBrowOuter | 398 | 96.2 | 1.76 | 1.83 |
| 121 | rBrowOuter | 398 | 96.1 | 1.76 | 1.83 |
| 125 | CenterBrow | 395 | 116.0 | 1.76 | 1.85 |
| 31 | rSmallToe1 | 387 | 135.5 | 0.04 | 0.08 |
| 15 | lSmallToe1 | 387 | 135.5 | 0.04 | 0.08 |
| 123 | lBrowMid | 382 | 92.5 | 1.77 | 1.84 |
| 120 | rBrowMid | 381 | 92.5 | 1.77 | 1.84 |
| 9 | lSmallToe4 | 373 | 150.0 | 0.00 | 0.08 |
| 25 | rSmallToe4 | 373 | 150.2 | 0.00 | 0.08 |
| 138 | rEyelidUpperOuter | 362 | 114.2 | 1.76 | 1.78 |
| 130 | lEyelidUpperOuter | 362 | 113.0 | 1.76 | 1.78 |
| 29 | rSmallToe2 | 360 | 131.2 | 0.04 | 0.08 |
| 13 | lSmallToe2 | 360 | 131.2 | 0.04 | 0.08 |
| 11 | lSmallToe3 | 359 | 128.9 | 0.04 | 0.08 |
| 27 | rSmallToe3 | 359 | 128.9 | 0.04 | 0.08 |
| 119 | rBrowInner | 337 | 73.6 | 1.76 | 1.83 |
| 122 | lBrowInner | 337 | 73.6 | 1.76 | 1.83 |
| 161 | lLipUpperOuter | 336 | 81.9 | 1.70 | 1.72 |
| 164 | rLipUpperOuter | 333 | 81.1 | 1.70 | 1.72 |
| 117 | lJawClench | 333 | 52.4 | 1.67 | 1.75 |
| 113 | Chin | 330 | 121.2 | 1.66 | 1.69 |
| 133 | lEyelidLowerOuter | 324 | 70.6 | 1.75 | 1.77 |
| 141 | rEyelidLowerOuter | 324 | 70.5 | 1.75 | 1.77 |
| 109 | rLipLowerInner | 321 | 66.8 | 1.68 | 1.70 |
| 107 | lLipLowerInner | 320 | 66.5 | 1.68 | 1.70 |
| 100 | tongue04 | 314 | 111.1 | 1.69 | 1.71 |
| 110 | rLipLowerOuter | 314 | 89.8 | 1.69 | 1.70 |
| 106 | lLipLowerOuter | 314 | 89.3 | 1.69 | 1.70 |
| 159 | rNasolabialMiddle | 298 | 72.4 | 1.70 | 1.75 |
| 158 | lNasolabialMiddle | 298 | 72.4 | 1.70 | 1.75 |
| 114 | lCheekLower | 284 | 54.4 | 1.68 | 1.76 |
| 156 | lNasolabialUpper | 282 | 47.7 | 1.72 | 1.76 |
| 157 | rNasolabialUpper | 282 | 47.7 | 1.72 | 1.76 |
| 112 | LipBelow | 277 | 93.9 | 1.66 | 1.69 |
| 115 | rCheekLower | 274 | 54.3 | 1.68 | 1.76 |
| 136 | rEyelidUpper | 271 | 92.2 | 1.77 | 1.78 |
| 128 | lEyelidUpper | 269 | 93.2 | 1.77 | 1.78 |
| 118 | rJawClench | 263 | 42.1 | 1.67 | 1.75 |
| 152 | lLipBelowNose | 261 | 28.9 | 1.70 | 1.73 |
| 137 | rEyelidUpperInner | 258 | 87.6 | 1.76 | 1.78 |
| 129 | lEyelidUpperInner | 258 | 87.7 | 1.76 | 1.78 |
| 134 | lEyelidLowerInner | 255 | 49.3 | 1.75 | 1.76 |
| 142 | rEyelidLowerInner | 255 | 49.3 | 1.75 | 1.76 |
| 153 | rLipBelowNose | 255 | 28.6 | 1.70 | 1.73 |
| 101 | lNasolabialLower | 248 | 57.1 | 1.66 | 1.71 |
| 102 | rNasolabialLower | 248 | 57.1 | 1.66 | 1.71 |
| 145 | rSquintInner | 229 | 59.6 | 1.73 | 1.76 |
| 143 | lSquintInner | 229 | 59.6 | 1.73 | 1.76 |
| 103 | lNasolabialMouthCorner | 227 | 43.4 | 1.67 | 1.74 |
| 104 | rNasolabialMouthCorner | 227 | 43.4 | 1.67 | 1.74 |
| 146 | rSquintOuter | 213 | 57.0 | 1.73 | 1.77 |
| 144 | lSquintOuter | 213 | 57.0 | 1.73 | 1.77 |
| 126 | MidNoseBridge | 203 | 26.1 | 1.74 | 1.77 |
| 155 | rLipNasolabialCrease | 202 | 29.7 | 1.70 | 1.73 |
| 154 | lLipNasolabialCrease | 202 | 29.7 | 1.70 | 1.73 |
| 140 | rEyelidLower | 185 | 63.2 | 1.75 | 1.76 |
| 132 | lEyelidLower | 185 | 63.2 | 1.75 | 1.76 |

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
textures: [0]textures\pc_a_summersuit01_hd_body_rgbx_albedo.jpg; [1]textures\Torso-C.jpg; [2]textures\Arms-C.jpg; [3]textures\Eye-1.jpg; [4]textures\Face-C.jpg; [5]textures\Legs-C.jpg; [6]textures\G8FBaseMouthMapD_1005.jpg; [7]textures\GensMapD_Default_P_1009.png; [8]textures\pc_a_nk_eyebrow_rgbx_albedo.png; [9]textures\pc_a_nk_hair_rgbx_albedo.png

| # | name | name_e | tex | sphere(mode) | toon | diffuse | specular | shin | ambient | flags D/G/M/S/E | edge | edge color | faces | memo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 4_+Swimsuit_0.1_0_0 |  | textures\pc_a_summersuit01_hd_body_rgbx_albedo.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 16158 |  |
| 1 | 6_-Swimsuit.GenS_0.1_0_0 |  | textures\GensMapD_Default_P_1009.png | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 14396 |  |
| 2 | 4_Body_0.1_0_0 |  | textures\Torso-C.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 37724 |  |
| 3 | 4_-Swimsuit.Body_0.1_0_0 |  | textures\Torso-C.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 704 |  |
| 4 | 4_Mouth_0.1_0_0 |  | textures\G8FBaseMouthMapD_1005.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 16464 |  |
| 5 | 4_+Earrings_0.1_0_0 |  | textures\pc_a_summersuit01_hd_body_rgbx_albedo.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 256 |  |
| 6 | 4_Face_0.1_0_0 |  | textures\Face-C.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 18432 |  |
| 7 | 4_Eyes_0.1_0_0 |  | textures\Eye-1.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 3264 |  |
| 8 | 6_Eyelashes_0.1_0_0 |  | textures\pc_a_nk_eyebrow_rgbx_albedo.png | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 804 |  |
| 9 | 6_Hair_0.1_0_0 |  | textures\pc_a_nk_hair_rgbx_albedo.png | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 17018 |  |
| 10 | 6_Eyebrows_0.1_0_0 |  | textures\pc_a_nk_eyebrow_rgbx_albedo.png | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 228 |  |
| 11 | 4_+Jewelry_0.1_0_0 |  | textures\pc_a_summersuit01_hd_body_rgbx_albedo.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 1172 |  |
| 12 | 4_Arms_0.1_0_0 |  | textures\Arms-C.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 35568 |  |
| 13 | 4_Legs_0.1_0_0 |  | textures\Legs-C.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 30256 |  |
| 14 | 4_+Shoes_0.1_0_0 |  | textures\pc_a_summersuit01_hd_body_rgbx_albedo.jpg | - (off) | #-1 | (0.80, 0.80, 0.80, 1.00) | (1.00, 1.00, 1.00) | 11.8991 | (0.40, 0.40, 0.40) | DGMS- | 1 | (0.00, 0.00, 0.00, 0.50) | 7290 |  |

## 9. Display frames
- **Root** / Root special=True n=0: 
- **表情** / Facial special=True n=0: 

## 10. Validation smells
- dup_bones: {}
- dup_morphs: {}
- dup_mats: {}
- dup_rigids: {}
- dup_joints: {}
- bone_gt15: [('lNasolabialLower', 16), ('rNasolabialLower', 16), ('lNasolabialMouthCorner', 22), ('rNasolabialMouthCorner', 22), ('lEyelidUpperInner', 17), ('lEyelidUpperOuter', 17), ('lEyelidLowerOuter', 17), ('lEyelidLowerInner', 17), ('rEyelidUpperInner', 17), ('rEyelidUpperOuter', 17), ('rEyelidLowerOuter', 17), ('rEyelidLowerInner', 17), ('lLipNasolabialCrease', 20), ('rLipNasolabialCrease', 20), ('lNasolabialUpper', 16), ('rNasolabialUpper', 16), ('lNasolabialMiddle', 17), ('rNasolabialMiddle', 17), ('head hair left 1', 16), ('head hair left 2', 16), ('head hair front right 1', 23), ('head hair front right 2', 23), ('head hair front right 3', 23), ('head hair front right 4', 23)]
- morph_gt15: []
- non_cp932_bones: []
- non_cp932_morphs: []
- non_cp932_mats: []
- empty_name_e_bones: 177
- unused_leaf_bones_noweight: []
- weighted_but_nonrot: []
- weighted_bones: 175
- wsum_bad: 0
- rigid_no_bone: []
- joint_bad: []
- missing_textures: []
- parent_after_child: []
- ctrl_visible_not_in_frames: ['hip', 'pelvis', 'lThighBend', 'lThighTwist', 'lShin', 'lFoot', 'lMetatarsals', 'lToe', 'lSmallToe4', 'lSmallToe4_2', 'lSmallToe3', 'lSmallToe3_2', 'lSmallToe2', 'lSmallToe2_2', 'lSmallToe1', 'lSmallToe1_2', 'lBigToe', 'lBigToe_2', 'rThighBend', 'rThighTwist', 'rShin', 'rFoot', 'rMetatarsals', 'rToe', 'rSmallToe4', 'rSmallToe4_2', 'rSmallToe3', 'rSmallToe3_2', 'rSmallToe2', 'rSmallToe2_2', 'rSmallToe1', 'rSmallToe1_2', 'rBigToe', 'rBigToe_2', 'Anus', 'Genitals', 'abdomenLower', 'abdomenUpper', 'chestLower', 'chestUpper', 'lCollar', 'lShldrBend', 'lShldrTwist', 'lForearmBend', 'lForearmTwist', 'lHand', 'lThumb1', 'lThumb2', 'lThumb3', 'lCarpal1', 'lIndex1', 'lIndex2', 'lIndex3', 'lCarpal2', 'lMid1', 'lMid2', 'lMid3', 'lCarpal3', 'lRing1', 'lRing2'] ... (176)
