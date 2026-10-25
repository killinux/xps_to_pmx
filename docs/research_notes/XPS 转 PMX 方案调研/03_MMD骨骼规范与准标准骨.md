# 03 MMD 骨骼规范与准标准骨（標準ボーン / 準標準ボーン / IK / 静止姿态 / 坐标 / 表示枠 / 表情 / 格式约束）

> 调研目的：为 XPS→PMX Blender 插件自动合成缺失骨骼提供可编程的、数值精确的参考。
> 来源分级：**[一次数据]** = 本次直接解析的原始文件（あにまさ式初音ミク ver.2.3 的 `miku_v2.pmd`、PMXEditor 随附 `PMX仕様.txt`、nanoem 对そぼろ插件的开源移植 `ssb.cc`、Hogarth-MMD 的标准骨架 PMX）；**[规范/官方]** = PMX 仕様、VPVP wiki；**[社区]** = 日文博客 / 教程；**[推断]** = 本文根据以上数据推导，未经外部验证。所有「位置」均为 MMD 左手系 Y-up 单位（见问题 5）。
> 注意：ニコニコ大百科 / ピクシブ百科事典 / bowlroll / そぼろ原版 readme（OneDrive）在本次环境中全部无法访问（403/404），相关内容改由 VPVP wiki、nanoem 移植版文档与源码、日文博客补足；凡属替代来源处均已标明。

---

## 问题 1：MMD 标准骨骼集（標準ボーン，源自 あにまさ式ミク）

### Takeaway
「標準ボーン」= MMD 自带 あにまさ式初音ミク 的骨骼去掉服装/头发等非通用骨后的集合（社区称 64 根）；本次直接解析 ver.2.3 PMD 得到全部骨骼的名称、父子、表示先、类型与**精确坐标**（身高 20.214 单位、センター Y=8.0、両目 浮在头顶上方 Y=21.0、脚尖 Z=−2.464 即模型面向 −Z），足够据此按比例把骨骼放到任意模型的身体地标上。

### Cited Findings

**定义与数量**
- 「標準ボーン」= 「PMXで作られたモデルにあるボーンのうち、以下の条件を満たすもの」，以 MMD 同梱的あにまさ式初音ミク（無印）骨骼结构为基准；总数 **64 根**，即「あにまさ式ミクに設定されているボーンのうち、服や髪などの不要なボーンを削除したもの」；准标准骨则是「動かす際の自由度、操作性を高める等の目的で、様々なモデラーさんやモーション作成者が実装してきたボーン」，并指出「完全には標準化できていないようだ」 — [scrapbox: 標準ボーン](https://scrapbox.io/motoso/%E6%A8%99%E6%BA%96%E3%83%9C%E3%83%BC%E3%83%B3)
- 64 根标准骨的完整设置表由 まめピカ 以 Excel（「標準Boneの設定.xlsx」）发布，网页本身只给出注意事项：「名前の設定に注意。全角半角、大文字小文字、漢字平仮名など、全て一致させないと上手く動かないことがある」 — [note: 標準ボーンの全設定｜まめピカ](https://note.com/mamepika/n/n9b8a6d55f0bb)（xlsx 未能抓取）

**一次数据：あにまさ式初音ミク ver.2.3（`miku_v2.pmd`，three.js r100 示例目录随附）**
- 文件头注释：「PolyMo用モデルデータ：初音ミク ver.2.3 (物理演算対応モデル) モデリング：あにまさ氏 データ変換：あにまさ氏 Copyright：CRYPTON FUTURE MEDIA, INC」；12354 顶点 / 22961 面 / 17 材质 / **140 根骨**（含头发・领带・裙子・袖子・「〜先」隐藏尖端骨） — [miku_v2.pmd（three.js r100）](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku) 本地解析
- 顶点 Y 范围 0.031～**20.214**（即身高约 20.2 单位），X 范围 −7.058～7.057 — 同上

**标准骨骼总表（ver.2.3 坐标；左侧骨给出，右侧 X 取负；PMD 英文名为该文件自带）**

| 日文名 | PMD 英文名 | 父骨 | 表示先（PMD 子骨/尖端） | ver.2.3 位置 (x,y,z) | PMD 类型 | 是否带权重 |
|---|---|---|---|---|---|---|
| センター | center | （无） | センター先 (0,0,0) → 朝下 | (0, 8.0, 0) | 1 回転移動 | 否 |
| 上半身 | upper body | センター | 首 | (0, 13.301, −0.255) | 0 回転 | 是 |
| 下半身 | lower body | センター | 下半身先 (0,11.361,−0.246) → 朝下 | (0, 13.243, −0.255) | 0 | 是 |
| 首 | neck | 上半身 | 頭 | (0, 16.418, 0) | 0 | 是 |
| 頭 | head | 首 | 頭先 (0,19.0,0) → 朝上 | (0, 16.799, 0) | 0 | 是 |
| 左目 | eye_L | 頭 | 左目先 (0.62,17.8,−0.897) → 朝前(−Z) | (0.35, 17.858, −0.348) | 5 回転影響下（源=両目） | 是 |
| 両目 | eyes | 頭 | 両目先 (0,21.0,−1.5) → 朝前(−Z) | (0, 21.0, −0.7) | 0 | 否 |
| 左肩 | shoulder_L | 上半身 | 左腕 | (0.136, 16.13, 0.265) | 0 | 是 |
| 左腕 | arm_L | 左肩 | 左ひじ | (0.891, 15.689, 0.318) | 0 | 是 |
| 左腕捩 | arm twist_L | 左腕 | 左腕捩先 (=左ひじ位置) | (1.844, 15.368, 0.305) | 8 捩り | 是 |
| 左ひじ | elbow_L | 左腕捩 | 左手首 | (3.591, 14.148, 0.282) | 0 | 是 |
| 左手捩 | wrist twist_L | 左ひじ | 左手捩先 (=左手首位置) | (4.036, 13.782, 0.276) | 8 捩り | 是 |
| 左手首 | wrist_L | 左手捩 | 左手先 (6.019,12.009,0.316) | (5.27, 12.725, 0.272) | 0 | 是 |
| 左親指１ / 左親指２ | thumb1_L / thumb2_L | 左手首 / 左親指１ | 左親指２ / 左親指先 | (5.6,12.176,−0.185) / (5.835,11.89,−0.346) | 0 | 是 |
| 左人指１/２/３ | fore1_L/2/3 | 左手首→链式 | 下一节 / 左人差指先 | (6.134,11.974,0.046) (6.407,11.776,0.048) (6.621,11.604,0.043) | 0 | 是 |
| 左中指１/２/３ | middle1_L/2/3 | 左手首→链式 | 下一节 / 左中指先 | (6.147,11.963,0.23) (6.493,11.767,0.227) (6.736,11.574,0.221) | 0 | 是 |
| 左薬指１/２/３ | third1_L/2/3 | 左手首→链式 | 下一节 / 左薬指先 | (6.148,11.941,0.398) (6.385,11.745,0.395) (6.621,11.593,0.403) | 0 | 是 |
| 左小指１/２/３ | little1_L/2/3 | 左手首→链式 | 下一节 / 左小指先 | (6.013,11.924,0.576) (6.243,11.773,0.569) (6.385,11.65,0.559) | 0 | 是 |
| 左足 | leg_L | 下半身 | 左ひざ | (0.797, 10.753, −0.073) | 4 IK影響下（左足ＩＫ） | 是 |
| 左ひざ | knee_L | 左足 | 左足首 | (0.674, 5.927, −0.053) | 4 | 是 |
| 左足首 | ankle_L | 左ひざ | 左つま先 | (0.875, 1.34, 0.0) | 4 | 是 |
| 左つま先 | toe_L | 左足首 | （センター，PMD 占位） | (0.929, 0.0, −2.464) | 6 IK接続先 | 是（PMD 中为 IK 目标） |
| 左足ＩＫ | leg IK_L | **（无，根级）** | 左足ＩＫ先 (0.875,1.34,1.5) → 朝后(+Z) | (0.875, 1.34, 0.0)（=左足首） | 2 IK | 否 |
| 左つま先ＩＫ | toe IK_L | 左足ＩＫ | 左つま先ＩＫ先 (0.929,−1.0,−2.464) → 朝下 | (0.929, 0.0, −2.464)（=左つま先） | 2 IK | 否 |
| 左腕捩1/2/3 | （无） | 左腕 | 左腕捩 | 与 左腕捩 同位置 | 9 回転連動（字段值 25/50/75） | 是 |

— 全部数据来自 [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)；PMD 类型含义（0 ROTATE, 1 ROTATE_MOVE, 2 IK, 4 IK_ROTATE_INFL, 5 ROTATE_INFL, 6 IK_TARGET, 7 UNVISIBLE, 8 ROLLING, 9 TWEAK；骨记录为 20 字节名 + parent short + tail short + type byte + ik short + 3 float）见 [pymeshio pmd 源码](https://pythonhosted.org/pymeshio/pymeshio.pmd-pysrc.html)
- 「是否带权重」依据：「The center(センター) bone does not have any vertex group. The root(全ての親) bone ... does not have any vertex group. The eyes(両目) bone does not have any vertex group. The 4 leg and foot IK bones also do not have any vertex group ... Every other bone in an MMD standard armature has a vertex group.」 — [Hogarth-MMD: MMD standard armature notes.txt](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/tutorials%20MMD%20standard%20armature/MMD%20standard%20armature%20notes.txt)

**PMX 形式下的同一骨架（Hogarth-MMD 随附 `MMD standard bones with leg foot IK.pmx`，文件头注明来源「初音ミク ver.1.3 データ変換：京 秋人氏」，57 骨，无网格）**
- `全ての親` (0,0,0) parent=−1 flags=0x001e[rot|mov|vis|ctrl] tail=(0,2,0)；`センター` (0,8.0,0) parent=全ての親 flags 0x001e tail=(0,−2,0)；`上半身` (0,13.301,−0.255) flags 0x001b[tailIdx|rot|vis|ctrl] tail=首；`首` (0,16.532,0)；`頭` (0,16.909,0) tail=(0,2.091,0)；`左目` (0.354,17.798,−0.454) layer=2 flags 0x011a[rot|vis|ctrl|grantRot] grant=(両目,1.0)；`両目` (0,21.0,−0.7) tail=(0,0,−0.8)；`左足ＩＫ` parent=全ての親 flags 0x003e[rot|mov|vis|ctrl|IK] tail=(0,0,2.749)；`左つま先ＩＫ` parent=左足ＩＫ flags 0x003e tail=(0,−1.375,0)；`左手首` tail=(0.554,−0.497,0.044)；`左つま先` tail=(0,0,−1) — [Hogarth-MMD pmx example armatures](https://github.com/Hogarth-MMD/mmd_tools_helper/tree/master/pmx%20example%20armatures) 本地解析
- 该 ver.1.3 骨架中没有 腕捩/手捩，上臂 `左腕` (1.151,15.689,0.318) → `左ひじ` (3.457,14.281,0.48) → `左手首` (5.018,12.964,0.252) — 同上

**层级与表示先惯例（PMX 实现者的代码化定义）**
- miu200521358 的 `bone_setting.py`（VMD Sizing 作者）给出每根标准/准标准骨的候选父骨、表示先与标志位，例如：`センター` parents=("全ての親",) display_tail=(0,1,0)；`下半身` display_tail=("足中心",)；`上半身` display_tail=("上半身2",) flag 含 `TAIL_IS_BONE`；`首` display_tail=("頭",)；`頭` display_tail=(0,1,0)；`両目` parents=("頭",) display_tail=(0,1,0) tails=("左目","右目")；`左目` flag 含 `IS_EXTERNAL_ROTATION`；`右手首` display_tail=(−1,0,0)、`左手首` (1,0,0)；`右足首` display_tail=("右つま先",)；`右つま先` (0,−1,0)；`右足ＩＫ` parents=("右足IK親","全ての親") display_tail=("右つま先ＩＫ",) flag 含 `IS_IK|TAIL_IS_BONE`；`右つま先ＩＫ` parents=("右足ＩＫ",) display_tail=(0,−1,0) — [mmd_base/mlib/pmx/bone_setting.py](https://github.com/miu200521358/mmd_base/blob/develop/mlib/pmx/bone_setting.py)
- 「In the .pmd and .pmx file formats, each bone is a single point ... the .pmd file format uses hidden tip bones to show a bone's tail/tip ... the .pmx file format uses a display destination x,y,z co-ordinate or the location of another bone」；「The root(全ての親) bone is located at (0,0,0). The center(センター) bone is usually located half-way between a character's knees and thighs, but it can be located higher than that without damaging an animation」；「The upper body(上半身) and lower body(下半身) bones are located near to a character's waist」 — [Hogarth-MMD: MMD standard armature notes.txt](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/tutorials%20MMD%20standard%20armature/MMD%20standard%20armature%20notes.txt)

**MMD Tools（Blender）使用的英文译名（部件级词表，组合生成整名）**
- `全ての親→ParentNode`, `操作中心→ControlNode`, `センター→Center`, `グルーブ→Groove`, `キャンセル→Cancel`, `上半身→UpperBody`, `下半身→LowerBody`, `手首→Wrist`, `足首→Ankle`, `首→Neck`, `頭→Head`, `両目→Eyes`, `目→Eye`, `腰→Waist`, `肩→Shoulder`, `腕→Arm`, `ひじ→Elbow`, `手→Hand`, `親指→Thumb`, `人指→IndexFinger`, `中指→MiddleFinger`, `薬指→RingFinger`, `小指→LittleFinger`, `足→Leg`, `ひざ→Knee`, `つま→Toe`, `捩→Twist`, `ダミー→Dummy`, `右→Right`, `左→Left`, `先→Tip`, `親→Parent`, 全角数字/字母→半角 — [blender_mmd_tools/mmd_tools/translations.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/translations.py)
- nanoem 移植版插件生成的英文名：`上半身2→upper body2`, `腰→waist`, `右足IK親→leg IKP_R`, `右足先EX→toe2_R`, `右ダミー→dummy_R`, `右肩P→shoulderP_R`, `右親指０→thumb0_R`, `グルーブ→groove`, `全ての親→master`, `操作中心→view cnt`, `右腕捩→arm twist_R`, `右手捩→wrist twist_R` — [nanoem ssb.cc](https://github.com/hkrn/nanoem/blob/main/emapp/plugins/ssb/ssb.cc)

### Inferences
- **按身高比例的地标公式**（H = 模型最高点 Y；由 ver.2.3 数据 H=20.214 计算）：センター ≈ 0.396H；下半身 ≈ 0.655H、上半身 ≈ 0.658H（二者几乎同点，上半身略高 0.058 单位、同在 Z=−0.255）；首 ≈ 0.812H；頭 ≈ 0.831H；肩 ≈ 0.798H；腕 ≈ 0.776H；ひじ ≈ 0.700H；手首 ≈ 0.630H；足 ≈ 0.532H；ひざ ≈ 0.293H；足首 ≈ 0.066H；つま先 Y=0；両目 ≈ 1.039H（在头顶之上，Z=−0.7 略前）；左目 ≈ 0.883H。
- **実装建议**：上半身/下半身 放在骨盆顶/腰线处同一位置（下半身尾朝下、上半身尾指首）；センター 放在大腿中段（约 0.4H，Hogarth 称「knees 与 thighs 之间，更高也不破坏动画」）；両目 作为纯控制骨可放在头顶上方任意便于抓取处，左目/右目 放在眼球中心、尾朝 −Z，并设 回転付与 源=両目 率=1.0；足ＩＫ 与 足首 同位置、尾朝 +Z（PMD ver.2.3 的 ＩＫ先 在 Z+1.5）；つま先ＩＫ 与 つま先 同位置、尾朝 −Y；つま先 放在脚尖地面（Y=0）。
- 「64 根」的具体清单未能获取；按本次 PMD 数据去掉服饰/头发/「〜先」骨后，可见可操作骨为 60 根（センター,上半身,下半身,首,頭,左右目,両目 = 8；双臂 2×(肩,腕,腕捩,ひじ,手捩,手首 + 14 指骨) = 40；双腿 2×(足,ひざ,足首,つま先) = 8；IK 4），若再加 隐藏的 腕捩1〜3×2 为 66，加 全ての親 为 61——64 的计数口径不明。

### Gaps
- まめピカ 的 64 骨设置表（xlsx）与 ニコニコ大百科「MMD標準ボーン」条目均无法访问，64 的精确清单未验证。
- ver.2.3 与 ver.1.3 坐标略有差异（首 16.418 vs 16.532；腕 X 0.891 vs 1.151），哪一个被社区视为「基准」未见明示；TDA 式等常见模型的坐标未取得。

---

## 问题 2：准标准骨（準標準ボーン）与 そぼろ「準標準ボーン追加プラグイン」(SemiStandardBones)

### Takeaway
插件原版 readme 不可达，但 nanoem 作者 hkrn 把该插件完整移植为开源 C++（`plugin_ssb`，文档自述「ほぼ同じ機能」），其源码给出了每根骨的**精确放置公式、父子重排、付与率、轴固定、权重分配算法与默认选项**；关键数值：腕捩/手捩 位于父→子 0.6 处并沿该轴 軸固定，子捩骨 付与率 0.25/0.5/0.75；上半身2 位于 上半身→首 0.35 处；腰 位于 (0, mix(下半身.y, 足.y, 0.6), 下半身.y×0.02)；足IK親 = 足ＩＫ 投影到地面 (x,0,z)；足D/ひざD/足首D = 原骨克隆 + 付与率 1 + 変形階層 +1；足先EX 位于 足首→つま先ＩＫ 的 2/3 处；肩C 付与率 −1（源 肩P）；腰キャンセル 付与率 −1（源 腰）；グルーブ = センター + (0,0.2,0)；親指０ 位于 手首→親指１ 的 2/3 处。

### Cited Findings

**插件元数据**
- VPVP wiki 条目「準標準ボーン追加プラグイン/SemiStandardBones」：【DL】配布先 (2012/10/06) OneDrive（`onedrive.live.com/?...cid=EF581C37A4524EDA`）**PMD版 ver 4.2、PMX版 ver 1.4**；【作者】そぼろ；【機能】「腕捩れ氏ボーンや上半身２ボーンをウエイトの設定を含めて追加する」；紹介動画「【MMD】準標準ボーン追加プラグインの紹介【PMDE】」；评论区 2014-03-07：「そぼろさんの配布先が変わっているようです。ご本人のtwitter上にリンクがありました」 — [VPVP wiki: PMDエディタ用プラグイン](https://w.atwiki.jp/vpvpwiki/pages/228.html)
- 同页另列：「標準ボーンチェッカー/CheckBasicBone」【DL】bowlroll.net/file/9611 (2014/11/28)【作者】T0R0【機能】「標準ボーン構成のチェックを行って強制的にある程度そろえてしまうプラグイン」【補足】「あにまさミク基準＋α」；「モーション流し対応肩キャンセル追加プラグイン」【作者】極北、でで — 同上
- 安装：「プラグインファイル『SemiStandardBones.dll』をPMDエディタまたはPMXエディタの『_plugin』フォルダ内の『User』フォルダに配置」；推荐「とりあえず全部チェック入れて追加」；文中「おねがいダーリン」モーション 必须骨：グルーブ, 上半身2, 腰, 肩P, 腕捩, 手捩, 親指0 — [さらりっち: はじめてのMMD3・準標準ボーン](https://karisakmmd.blog.jp/archives/8334623.html)
- PMX 版 dll 名「SemiStandardBonesPMX.dll」，放入 PMXE 的 `_plugin/User`；作者常用三项：足IK親（「足IKの多段モーション作成」「歩行モーション等の多段調整」）、手持ちアクセサリ用ダミー（右ダミー/左ダミー，外部親で持たせる）、肩キャンセルボーン（「右肩P、左肩P」として登録） — [MMD swamp: 準標準ボーン追加プラグイン](https://sites.google.com/view/mmd-swamp/tipsother/%E6%BA%96%E6%A8%99%E6%BA%96%E3%83%9C%E3%83%BC%E3%83%B3%E8%BF%BD%E5%8A%A0%E3%83%97%E3%83%A9%E3%82%B0%E3%82%A4%E3%83%B3mmd%E3%83%A2%E3%83%87%E3%83%AB%E3%82%92%E3%82%AB%E3%82%B9%E3%82%BF%E3%83%9E%E3%82%A4%E3%82%BA)
- 「必要なのはOneDriveにある、『SemiStandardBones.zip』です。最近のモーションには使われていることが多いボーン達を一括追加してくれる天才」 — [note: PMX 〜追加プラグイン導入編〜｜とーか](https://note.com/gabugabu_megane/n/n716875820789)
- 使用流程：「編集→プラグイン→User→準標準ボーン追加(PMX)」→「全選択ボタン」→OK；「足Dボーンのチェックは外れたままで、気にせずOKしましょう」 — [nnwarks: ③VRM→MMD『ボーンの追加･修正』](https://nnwarks.com/vrm_mmd_3/)
- 执行前「必ず別名で保存」（「上書きしてしまうと、今まであにまさ式ミクを使ったpmmファイルが開けなくなります」）；PMD/PMX 用不同版本的插件 — [Rick: 準標準ボーンの追加方法について](https://site.nicovideo.jp/ch/userblomaga_thanks/archive/ar285448)
- 再分发许可（仅搜索摘要，原推未抓取）：「以下の再配布セットの『SemiStandardBones』が準標準ボーン追加プラグイン ※そぼろ氏の配布物は再配布OKなのでミラー配布は問題なし」 — [X @Baroque384](https://x.com/Baroque384/status/2005544259664175122)
- nanoem 移植版：「『準標準ボーンプラグイン』はそぼろさんが開発する PMDEditor/PMXEditor 用のプラグインである『準標準ボーンプラグイン』とほぼ同じ機能を実現する モデルプラグイン です」；最新 **1.3.0 (2021/2/14)**；「* が後ろについてるものは頂点のボーン再配置及びウェイト塗り（以降自動再配置）を実行します」；「『必要なボーン』は『日本語』のボーン名で判定します」「全角英数字と半角英数字を区別します」；1.1.0 起缺骨时报错中止（「これらの機能はオリジナルには存在せず独自に追加した機能」） — [nanoem プラグイン文档](https://nanoem.readthedocs.io/ja/latest/plugin.html)；源码 [emapp/plugins/ssb/ssb.cc](https://github.com/hkrn/nanoem/blob/main/emapp/plugins/ssb/ssb.cc)（仓库许可：nanoem 为 MIT/X11，emapp 等为 MPL — [hkrn/nanoem](https://github.com/hkrn/nanoem)）

**对话框选项与默认值（nanoem 移植版 `loadWindowLayout()`；`registerCallback(..., checked, ...)` 的 checked 参数即默认勾选）**

| 选项（日/英） | 需要的骨 | 默认 | 产生的骨 |
|---|---|---|---|
| 腕捩れボーン * / Arm Twist Bone * | 右腕, 右ひじ, 左腕, 左ひじ | ✓ | 右腕捩, 左腕捩 + 腕捩1/2/3 |
| └ 回転自動補正 / Enable Elbow Offset | — | ✓ | （腕捩 Z 位置按臂部顶点修正） |
| 手捩れボーン * / Wrist Twist Bone * | 右ひじ, 右手首, 左ひじ, 左手首 | ✓ | 右手捩, 左手捩 + 手捩1/2/3 |
| 上半身2ボーン * / Upper Body 2 Bone * | 上半身, 首 | ✓ | 上半身2 |
| 腰ボーン / Waist Bone | 下半身, 右足, 左足 | ✓ | 腰, 腰キャンセル右, 腰キャンセル左 |
| 足IK親 / Parent of Leg IK | 右足ＩＫ, 左足ＩＫ（全角ＩＫ） | ✓ | 右足IK親, 左足IK親（半角 IK） |
| 足先EX * / Toes EX * | 右足, 右ひざ, 右足首, 右つま先ＩＫ, 左… | ✓ | 右足先EX, 左足先EX + 足D, ひざD, 足首D |
| └ 足Dボーンを操作可能に / Make Leg-D Bone Controllable | — | **✗** | （D 骨可见/可操作并入表示枠） |
| 手持ちアクセサリ用ダミー / Dummy Bone | 右手首, 右中指１, 左手首, 左中指１ | ✓ | 右ダミー, 左ダミー |
| 肩キャンセルボーン / Shoulder Cancel Bone | 右肩, 右腕, 左肩, 左腕 | ✓ | 右肩P, 右肩C, 左肩P, 左肩C |
| 親指０ボーン * / Thumb Proximal Bone * | 右手首, 右親指１, 左手首, 左親指１ | ✓ | 右親指０, 左親指０ |
| └ 親指ローカル軸設定 / Enable Local Axes of Thumb | — | ✓ | （为 親指０/１/２ 设 ローカル軸） |
| グルーブボーン / Groove Bone | センター | ✓ | グルーブ |
| 全ての親 / Root Bone | — | ✓ | 全ての親 |
| 操作中心 / View Center | — | ✓ | 操作中心 |
| ボーン表示枠に自動登録 / Generate Labels | — | ✓ | （表示枠登记） |
| （材質選択） | — | 全部 ✓ | 自動再配置対象材质 |

— [nanoem ssb.cc](https://github.com/hkrn/nanoem/blob/main/emapp/plugins/ssb/ssb.cc)、[nanoem 文档](https://nanoem.readthedocs.io/ja/latest/plugin.html)
- 原版插件**不**生成 両目 与 首（它们属标准骨；两份文档的骨清单中均无）；标准骨的补齐/校正由 T0R0 的「標準ボーンチェッカー」负责 — [nanoem 文档](https://nanoem.readthedocs.io/ja/latest/plugin.html)、[VPVP wiki](https://w.atwiki.jp/vpvpwiki/pages/228.html)

**逐骨规格（nanoem `ssb.cc` 代码行为；`mix(a,b,t)=a+(b−a)t`；「插入位置」指骨骼列表 index）**

| 骨 | 位置公式 | 父骨 / 重排 | 付与・軸 | 标志/表示先 | 変形階層 | 权重处理 |
|---|---|---|---|---|---|---|
| 腕捩（`addTwistBone(P=腕, C=ひじ, elbowOffset=true)`） | `C' = C`；若勾选回転自動補正：`C'.z += 0.75×(mean_z(权重≥0.6属于P的顶点) − C.z)`；`O = mix(P, C', 0.6)`；`axis = normalize(C' − P)` | 父=腕；插入到 腕 之后；**ひじ 改父为 腕捩** | 軸固定=axis | rot\|vis\|ctrl；表示先偏移 (0,0,0) | 未设置（默认 0） | 见下 |
| 腕捩1/2/3 | `pd = 0.8×dot(P−O,axis)`、`cd = 0.8×dot(C'−O,axis)`，再分别取 min/max 扩展到「专属于 P（≥0.97）的顶点」投影；`O_i = O + axis×mix(pd, cd, i/4)`，i=1,2,3 | 父=腕；依次插在 腕捩 之后 | **回転付与 源=腕捩, 率 = 0.25 / 0.5 / 0.75** | rot\|ctrl（不可见）；表示先 (0,0,0)；同名旧骨先删除 | 未设置 | 专属 P 顶点：`δ = (proj−pd)/(cd−pd)×4`，`w = (int(100δ) mod 100)/100`，按 `int(δ)` 分段 BDEF2：0→[捩1,腕] 1→[捩2,捩1] 2→[捩3,捩2] 3→[捩,捩3] 4→[ひじ,捩]（首项权重 w，次项 1−w）；非专属但含 ひじ 且 proj>0 的顶点：腕→腕捩 替换 |
| 手捩（`P=ひじ, C=手首, elbowOffset=false`） | 同上，`O = mix(ひじ, 手首, 0.6)` | 父=ひじ；**手首 改父为 手捩** | 軸固定；子骨 0.25/0.5/0.75 | 同上 | 未设置 | 同上（分段到 手首） |
| 上半身2 | `O = mix(上半身, 首, 0.35)` | 父=上半身；插在 上半身 之后；**上半身 原有全部子骨改父为 上半身2**；上半身 的表示先改指 上半身2；上半身 的刚体改挂 上半身2 | — | rot\|vis\|ctrl；表示先偏移 `(首−O)×0.8` | = 上半身 的値 | 非专属上半身的顶点中 `y > O.y` 者：上半身→上半身2 替换；专属上半身（≥0.97）顶点：`d = v−O`，若 `d.z>0` 则 `d.y += 0.5 d.z`；`v' = d.y/(首.y−O.y)`；`v'<−0.35`→BDEF1 上半身；`v'>0.35`→BDEF1 上半身2；否则 BDEF2，上半身2 权重 `int(((v'+0.35)/0.7)×100)×0.01` |
| 腰 | `O = (0, mix(下半身.y, 右足.y, 0.6), 下半身.y×0.02)` | 父 = 下半身 的父（センター/グルーブ）；插在该父之后；**该父的所有子骨（除 センター先）改父为 腰**（即 上半身・下半身 都挂到 腰 下） | — | rot\|vis\|ctrl；表示先 `(下半身−O)×0.8` | = 父的値 | 无 |
| 腰キャンセル右/左 | = 右足/左足 的位置 | 父 = 足 原父；插在 足 之前；**足 改父为 腰キャンセル** | **回転付与 源=腰, 率 −1** | rot\|ctrl（不可见） | 未设置 | 无 |
| 足IK親 | `O = 足ＩＫ × (1,0,1)`（投影到 Y=0 地面） | 父 = 足ＩＫ 原父；插在 足ＩＫ 之前；**足ＩＫ 改父为 足IK親** | — | rot\|mov\|vis\|ctrl；表示先=足ＩＫ（骨指定） | 未设置 | 无 |
| 足D / ひざD / 足首D | 克隆原骨（同位置），名=原名+"D"（日英） | 足D 父=足 原父；ひざD→足D；足首D→ひざD；追加到骨列表末尾 | **回転付与 源=对应原骨, 率 1**；表示先骨指定清空 | 可见/可操作 = 选项「足Dボーンを操作可能に」（默认否） | **原骨値 +1** | **全部顶点与刚体中 足→足D、ひざ→ひざD、足首→足首D** |
| 足先EX | `O = mix(足首, つま先ＩＫ, 2/3)` | 父=足首D；追加末尾 | — | rot\|vis\|ctrl；表示先 (0,0,−1) | = 足首D 的値 | 专属 足首 顶点：`c = (v.z−足首.z)/(O.z−足首.z)`，`w = clamp((c−0.75)×2, 0, 1)` → BDEF2 [足先EX w, 足首 1−w]（随后 足首 再被替换为 足首D） |
| 右/左ダミー | `M = (手首 + (中指１.xy, 手首.z))/2`；`n = normalize(中指１.xy − 手首.xy)`；右：`r=(−n.y, n.x)`，左：`r=(n.y, −n.x)`；`O = M + 0.25 r` | 父=手首；插在 手首 之后 | — | rot\|mov\|vis\|ctrl；表示先 `(1.2 r, 0)` | 未设置 | 无 |
| 肩P | = 肩 的位置 | 父 = 肩 原父（上半身/上半身2）；插在 肩 之前；**肩 改父为 肩P** | — | rot\|vis\|ctrl | 未设置 | 无 |
| 肩C | = 腕 的位置 | 父=肩；插在 肩 之后；**腕 改父为 肩C** | **回転付与 源=肩P, 率 −1** | rot\|ctrl（不可见） | 未设置 | 无 |
| 親指０ | `O = mix(手首, 親指１, 2/3)` | 父=手首；插在 親指１ 之前；**親指１ 改父为 親指０**；表示先=親指１ | 可选 ローカル軸：親指０ X=normalize(親指１−親指０)，Z=normalize(親指０−人指１)；親指１ X=normalize(親指２−親指１)，Z=旋转后的 (親指２−親指１) 且 z 分量=−0.2×长度；親指２ X=指向其表示先，Z 同前 | rot\|vis\|ctrl | 未设置 | 含 手首 或 親指１ 的顶点：到 (親指０+親指１)/2 连线的垂距（方向 右 (1,−1,0)/左 (−1,−1,0) 归一化）`d`，`w = clamp((1 − d/(1.4 L))×1.3, 0, 1)`（L=親指０→親指１ 长度）→ BDEF2 分给 親指０ |
| グルーブ | `O = センター + (0, 0.2, 0)` | 父=センター；插在 センター 之后；**センター 的所有子骨（除 センター先）改父为 グルーブ** | — | rot\|mov\|vis\|ctrl；表示先 (0,1.4,0) | 未设置 | 无 |
| 全ての親 | 未显式设置（新建骨默认原点） | 无父；插到 index 0；**所有无父骨改父为 全ての親**；表示先=原第一骨（センター） | — | rot\|mov\|vis\|ctrl | 未设置 | 无 |
| 操作中心 | 未显式设置（原点） | 无父；插到 index 0（在 全ての親 之上） | — | rot\|mov\|vis\|ctrl | 未设置 | 无 |

— 全部出自 [nanoem ssb.cc](https://github.com/hkrn/nanoem/blob/main/emapp/plugins/ssb/ssb.cc)（`isVertexDedicatedByBone` 默认阈值 0.97；`replaceVertexBone` 逐槽替换骨索引）
- 文档对各骨的定性说明：腕捩「それぞれ『右腕』と『右ひじ』…の間に作成されます。また、捩ボーンを親とする回転付与率が 0.25/0.5/0.75 の３つの回転付与ボーンが作成されます」；腰「『下半身』と『足』の間に作成されます。また『右足』と『腰』の間に『腰キャンセル右』が…名前が示す通り回転補正が -1.0 で行われる回転付与のボーン」；足先EX「加えて以下の回転付与のボーンが作成されます 右足D 右ひざD 右足首D …元のモーションに直接手を加えることなく追加の回転補正を行えるようにする」；肩キャンセル「P は右肩または左肩の親として、C は右肩または左肩と右腕または左腕の間に入ります…C の方は付与率が -1.0 の回転付与ボーン」；グルーブ「『センター』ボーンの直後に配置…センターボーンから上下の動きを分離するために使われます」；全ての親「最上位に設定…配布用に作る場合にかぎり先の理由で干渉を起こす可能性があることから利用を避けるべきです」；操作中心「最上位に設定（優先度的には『全ての親』よりも上）…カメラの視点の中心に設定するために使われます…操作中心ボーンを動かしてもモデル自身は一切動きません」；表示枠：腰→依赖 下半身 的枠，グルーブ→センター，全ての親/操作中心→(最初のボーン)，无枠时自动建「センター」枠 — [nanoem 文档](https://nanoem.readthedocs.io/ja/latest/plugin.html)
- 肩P/肩C 原理：标准结构「肩P → 肩 → 肩C → 腕」，「肩Cの付与親を肩Pに設定して倍率をマイナス１倍」；若改为「肩 → 肩P → 肩C → 腕」则「肩Pのローカル軸が肩に合う」但「すでに以前の肩Pで組んあるモーションの動作を完全互換しない」 — [PIP_MMD: 肩Pの話](https://pip-mmd.hatenablog.com/entry/2017/10/03/010753)
- 捩骨付与率的社区表述：「腕捩ボーンは　左腕捩からの回転影響の付与率が0.25」「左腕捩2は…0.5」「左腕捩3は…0.75」 — [くぅ＆みぃ: 捩ボーン・IKボーンの基礎](https://q-ku.blog.jp/archives/11315486.html)
- 插件后臂部权重顺序：「腕ボーン→腕捩1ボーン→腕捩2ボーン→腕捩3ボーン→腕捩ボーン」，腕捩「腕ボーンの中央に配置」（博主措辞，与代码 0.6 略异） — [ameblo: 腕捩りボーンを考える](https://ameblo.jp/everymemo/entry-12883850157.html)
- あにまさ式 ver.2.3 自带的 腕捩1/2/3 为 PMD 类型 9（TWEAK/回転連動），ik 字段值依次为 25/50/75，且位置与 腕捩 相同 — [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)
- Nuthouse01 的「auto armtwist」脚本以准标准 腕捩/手捩 为前提，并把 D 骨 変形階層 设 2、T 骨 3、子捩骨 4，IK loops=100、角=5° — [bone_add_semistandard_auto_armtwist.py](https://github.com/Nuthouse01/PMX-VMD-Scripting-Tools/blob/master/mmd_scripting/scripts_for_gui/bone_add_semistandard_auto_armtwist.py)（非标准做法，仅供参考）

### Inferences
- 插件的实现顺序即勾选项在对话框中的顺序（腕捩→手捩→上半身2→腰→足IK親→足先EX→ダミー→肩P→親指０→グルーブ→全ての親→操作中心），后执行者会看到前者改过的父子关系（例如 腰 把 上半身 挂到自己下面后，上半身2 的父仍是 上半身；足IK親 执行在 全ての親 之前，因此其父是 足ＩＫ 当时的父，随后 全ての親 把所有无父骨收为子）。XPS 转换器若一次性生成全部骨，可直接按最终结构写出：`操作中心 > 全ての親 > センター > グルーブ > 腰 > {上半身 > 上半身2 > 首 > 頭 …, 下半身 > 腰キャンセル左/右 > 足 …}`，并把 D 链单独挂在 腰キャンセル（或 下半身）之下。
- あにまさ原模型自己的 腕捩 位于 腕→ひじ 的 t≈0.353、手捩 位于 ひじ→手首 的 t≈0.265（由坐标反算），与插件的 0.6 不同；两者都被广泛使用，说明 VMD 兼容性对捩骨位置不敏感（捩骨只做轴向扭转），位置主要影响蒙皮效果。
- 原版插件（C#）的权重算法细节未必与移植版逐字相同；但移植版文档明确称功能「ほぼ同じ」，且其对话框文字、骨名、付与率与日文教程完全吻合，可作为实现依据。

### Gaps
- そぼろ 原版 readme（SemiStandardBones_Readme.txt）与 OneDrive 分发页无法访问；原版的许可条款只有第三方转述（「再配布OK」）。
- 原版对 変形階層 的具体赋值、各骨默认勾选状态（nnwarks 提到「足D のチェックは外れたまま」与移植版一致，但其余未逐项确认）。
- 「ニコニコ大百科/ピクシブ百科事典 準標準ボーン」条目内容未取得。

---

## 问题 3：IK 规格（足ＩＫ / つま先ＩＫ）与 MMD 的 IK 求解

### Takeaway
一次数据证实：あにまさ式 ver.2.3 的 足ＩＫ = 目标 足首、链 [ひざ, 足]、iterations 40、PMD 控制值 0.5；つま先ＩＫ = 目标 つま先、链 [足首]、iterations 3、控制值 1.0；PMX 以弧度存「单位角」且「PMDのIK値とは4倍異なる」，故 0.5→2 rad = 114.5916°，1.0→4 rad = 229.1831°；ひざ 角度制限 X −180°～−0.5°、Y/Z 0；MMD 用 CCD 迭代，7.38 起带角度制限的 IK 可能超出 Loop 次数继续迭代，官方建议单位角 ≥ 1。

### Cited Findings
- **PMD 一次数据**：`IK bone=左足ＩＫ target=左足首 chain=['左ひざ','左足'] iterations=40 control_weight=0.5`；`IK bone=左つま先ＩＫ target=左つま先 chain=['左足首'] iterations=3 control_weight=1.0`；（参考）`ﾈｸﾀｲＩＫ iterations=15 weight=0.03`、`左髪ＩＫ iterations=8 weight=0.03` — [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)
- **PMX 规范**：IK 数据 = 「IKターゲットボーンのIndex」「IKループ回数 (PMD及びMMD環境では255回が最大になるようです)」「IKループ計算時の1回あたりの制限角度 -> ラジアン角 | PMDのIK値とは4倍異なるので注意」「IKリンク数」；每个 link：「角度制限 0:OFF 1:ON」，开启时「下限 (x,y,z) -> ラジアン角」「上限 (x,y,z) -> ラジアン角」 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)
- 「PMXのIK変形はIKボーンの変形順序時にそのまま変形を行う(PMDのように全ボーン変形後などの順序固定ではないので注意)」；PMD→PMX 转换时「IKボーン及びそのIKを親としている系列の変形階層を 0→1」「回転影響下以下の変形階層を 0→2」 — 同上
- PMD 控制值与弧度的关系：「指定された値×4 radian までしか曲がれないらしい」，PMD editor readme「1.0=4[rad](230度程度)」；算法为 CCD：对链上每骨「回転軸 a = (V_T × V_I) / ||V_T × V_I||」，膝盖只允许 X 轴：先取局部旋转「R'_0 = R̃_1* Q R̃_0」，清零 Y/Z 分量后重组「R̃''_0 = R̃_1 R''_0」；loop 少+角大偏向末端精度，loop 多+角小使弯曲分散 — [edvakf: MMD on WebGL 踊れるようになった（あと IK について）](https://edvakf.hatenadiary.org/entry/20111102/1320268602)
- **PMX 形式标准值（Hogarth 文档）**：つま先ＩＫ「Target = toe (左つま先/右つま先)…The one link bone should be the ankle…Loop count: 3 works fine…Unit angle: 229.1831 (229.1831 degrees = 4 radians)…Angular limits should not be enabled」；足ＩＫ「Target = ankle…2 Link bones = knee and leg/thigh…Loop count: 40 works fine…Unit angle: 114.5916 (114.5916 degrees = 2 radians)…Angular limits must be enabled on the knee bone…x -180 -0.5, y 0 0, z 0 0」；「A leg IK bone must be located at the same location as the ankle bone…give it a tail located backward…A foot/toe IK bone must be located at the same location as the toe bone…tail located downward」；注：「What is the IK unit angle? Our team of mmd_tools developers did not know…values derived by looking at…various .pmx models…and…PMX editor when converting a model from .pmd to .pmx」 — [Hogarth-MMD: MMD leg-foot IK notes.txt](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/tutorials%20MMD%20standard%20armature/MMD%20leg-foot%20IK%20notes.txt)
- Hogarth 的 PMX 示例骨架（由 ver.1.3 PMD 转换）实际字段：`左足ＩＫ … IK: target=左足首 loop=48 unit=2.000001rad=114.5916deg links=[('左ひざ', ((-180.0,0,0),(-0.5,0,0))), ('左足', None)]`；`左つま先ＩＫ … loop=6 unit=4.0rad=229.1831deg links=[('左足首', None)]` — [Hogarth-MMD pmx example armatures](https://github.com/Hogarth-MMD/mmd_tools_helper/tree/master/pmx%20example%20armatures) 本地解析（Loop 48/6 与 ver.2.3 的 40/3 不一致，来源差异未考证）
- 社区解释：「IKというのは、ターゲットボーンの位置がIKボーンに可能な限り近づくよう、各ボーンの回転角度を自動で計算する機能」；「Loopは、1フレームあたりにIKの計算を行う回数」；「単位角…その計算1回ごとにボーンを回転させる最大量で、計算ごとに減衰して微調整になっていく」；「角度制限が多いほどLoop回数が必要になる」；输入下限上限时「『-180』『0』のように最小値を先に入力」 — [note: MMDのIKのまとめ｜改良強化新型ぺんぎん](https://note.com/penmmd/n/n27d02e0ce85f)
- 「X軸回転（ひざボーンにとっては前後回転）が『-180から-0.5』の範囲で回転できます」而 Y（ねじり）/Z（左右）不可；「Loopが0の場合、そのIKは無効」；IK Link 顺序「このボーンリストの上から順番に、ボーン列の先に近い方から並べます」（从靠近目标端到根） — [くぅ＆みぃ: 捩ボーン・IKボーンの基礎](https://q-ku.blog.jp/archives/11315486.html)
- PMDエディタ 手工建 足ＩＫ：复制 足首 为「左足ＩＫ」，父设「全ての親」，Target 选末端 足首，Link 登记 左足・左ひざ，ひざ 角度制限「-180 0」；つま先ＩＫ 复制 つま先，父=足ＩＫ — [クソザコブログ: 足ＩＫの作り方](https://sousakusuki.livedoor.blog/archives/6058900.html)
- **MMD 7.38+ 的 IK 行为**（MMD 作者在 2ch 的回复，VPVP 转录）：「MMD上のPMXでは、角度制限付きIKを正確に計算するためにターゲットボーン方向を向くまで Loop回数以上ループする場合があります(Ver7.38以降)」；单位角异常小会导致极慢；结论「MMDを使う場合はIKの単位角は1以上に設定してください」；要做不动的 IK：「単位角は１にして、IKの角度制限をx,y,z共0に設定」 — [VPVP wiki: PMXの概要](https://w.atwiki.jp/vpvpwiki/pages/284.html)
- PMD 的 IK 角度限制「"ひざ"関連のみ内部で自動設定」，PMX 为「任意設定が可能」 — 同上
- mmd_tools 导入时 `ikConst.iterations = pmx_bone.loopCount`、`chain_count = len(pmx_bone.ik_links)`，并把 `rotationConstraint` 存到 `mmd_bone.ik_rotation_constraint` — [mmd_tools core/pmx/importer.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/pmx/importer.py)；Hogarth 的 Blender 脚本设 `ik_rotation_constraint = 2 # 180*2/math.pi`（膝）与 `= 4`（踝） — [add_foot_leg_ik.py](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/mmd_tools_helper/add_foot_leg_ik.py)
- **IK 父骨**：ver.2.3 PMD 中 足ＩＫ 父=无（根级）、つま先ＩＫ 父=足ＩＫ；PMX 转换后 足ＩＫ 父=全ての親 — [miku_v2.pmd](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)、[Hogarth PMX](https://github.com/Hogarth-MMD/mmd_tools_helper/tree/master/pmx%20example%20armatures)；加 足IK親 后 足ＩＫ 父=足IK親，足IK親 父=原父（见问题 2）
- 足IK親 的用途：「足IKの多段モーション作成」「歩行モーション等の多段調整」，「元のモーションキーに直接触れず」 — [MMD swamp](https://sites.google.com/view/mmd-swamp/tipsother/%E6%BA%96%E6%A8%99%E6%BA%96%E3%83%9C%E3%83%BC%E3%83%B3%E8%BF%BD%E5%8A%A0%E3%83%97%E3%83%A9%E3%82%B0%E3%82%A4%E3%83%B3mmd%E3%83%A2%E3%83%87%E3%83%AB%E3%82%92%E3%82%AB%E3%82%B9%E3%82%BF%E3%83%9E%E3%82%A4%E3%82%BA)
- 「Normally an MMD model does not have any arm/hand IK and adding hand/arm IK may cause incompatibility with VMD motions…free VMD motions…almost always require that a model must have MMD leg/foot IK」；「Leg twist bones and other non-standard leg or foot bones, with few exceptions, make a mess out of MMD leg-foot IK」 — [Hogarth IK notes](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/tutorials%20MMD%20standard%20armature/MMD%20leg-foot%20IK%20notes.txt)、[armature notes](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/tutorials%20MMD%20standard%20armature/MMD%20standard%20armature%20notes.txt)

### Inferences
- 写 PMX 时的推荐字段：`左足ＩＫ`：位置=左足首，父=全ての親（若生成 足IK親 则父=左足IK親），flags=0x003E（回転|移動|表示|操作|IK），表示先偏移 (0,0,+1.5)（ver.2.3）或指向 左つま先ＩＫ（miu 约定），IK target=左足首，loop=40，unit=2.0 rad，links=[左ひざ{limit on, min=(−π,0,0), max=(−0.5°=−0.0087266 rad,0,0)}, 左足{limit off}]；`左つま先ＩＫ`：位置=左つま先，父=左足ＩＫ，flags 0x003E，表示先 (0,−1,0)，target=左つま先，loop=3，unit=4.0 rad，links=[左足首{off}]。
- 把 足/ひざ/足首/つま先 及 IK 的 変形階層 设 0 即可（Hogarth 文件与 nanoem 都未提升；PMD→PMX 官方转换会把 IK 链设 1、回転影響下骨设 2，两种做法都存在）。
- 大腿/小腿需有轻微自然弯曲让 CCD 知道膝盖弯向：ver.2.3 膝盖处 足→ひざ 与 ひざ→足首 夹角 4.0°、腿偏离竖直 1.48°（见问题 4）。

### Gaps
- 单位角「每次迭代衰减」的精确实现与 MMD 7.38+ 的「超 Loop 继续迭代」终止条件无公开源码可证，仅有作者论坛回复。
- Hogarth PMX 中 Loop 48/6 的来源（ver.1.3 原始值还是编辑结果）不明。

---

## 问题 4：标准静止姿态（A-pose）与 VMD 旋转语义

### Takeaway
あにまさ式 ver.2.3 的实测静止姿态：上臂（腕→ひじ）低于水平 29.7°，前臂（ひじ→手首）40.3°，整臂 34.1°，肘弯 10.6°，膝弯 4.0°，脚尖朝 −Z；PMX 骨只有位置没有静止旋转，VMD 以四元数记录「相对初始姿态、在父骨坐标系（= 世界轴向）中的旋转」，ローカル軸/軸固定 在规范中明文「表示及び操作時の制限項目…ボーンの変形特性や内部値には関与しない」，因此 T-pose 模型播放 A-pose 动作会把双臂整体抬高约 30～35°——必须把网格烘焙成 A-pose 后再导出。

### Cited Findings
- **实测（ver.2.3 PMD）**：左肩→左腕 低于水平 30.24°（长 0.875）；左腕→左ひじ **29.72°**（长 3.109）；左ひじ→左手首 **40.28°**（长 2.201）；左腕→左手首 34.09°（长 5.288）；肘弯（上臂与前臂夹角）10.57°；膝弯 4.00°，大腿偏离竖直 1.48°；脚尖 Z 相对脚踝 −2.464（朝 −Z） — [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)
- ver.1.3 骨架：左腕→左ひじ 约 31.4°、左ひじ→左手首 约 40.2°（由 Hogarth PMX 坐标反算） — [Hogarth PMX](https://github.com/Hogarth-MMD/mmd_tools_helper/tree/master/pmx%20example%20armatures)
- 社区概述（近似值）：「The arms are rotated downward at an approximately 45 degree angle in an A-pose. (In most other armature types, the character's rest pose is a T-pose…)」 — [Hogarth armature notes](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/tutorials%20MMD%20standard%20armature/MMD%20standard%20armature%20notes.txt)（与实测 30～40° 不符，视为粗略说法）
- MillionDance（Unity→PMX 导出器）选项：「Convert T-pose: Whether to convert the model's standard T-pose to TDA-styled 'A-pose' (arms stretching to lower left and lower right)」，用于「use the model in VMDs for TDA models」 — [MillionDance Manual](https://github.com/OpenMLTD/MLTDTools/wiki/MillionDance-Manual)
- **VMD 为什么依赖静止姿态**：「Most XPS models are in T pose and VMD motion in A pose…The VMD motion defines how much rotation needs to be applied to each bone but it doesn't specify what the original orientation of the bone is」；该工具提供「Direct Drive」（直接驱动，仅推荐 PMX）与「Standard Pose Angle」滑块微调臂角 — [DanceXR 1.3.6 devlog](https://stormlab.itch.io/dancexr/devlog/439796/release-136)
- **VMD 存储**：每骨帧「15b char-string, name of the bone / 4b uint frame number / 4b float x,y,z position / 4b float x,y,z,w rotation (quaternion) / 64b interpolation」；文件 shift_jis 编码；头 30 字节「Vocaloid Motion Data 0002」+20 字节模型名 — [Nuthouse01 README: VMD binary structure](https://github.com/Nuthouse01/PMX-VMD-Scripting-Tools/blob/master/README.md)；同样结构见 [kumiho_k: VMDファイルフォーマット](https://w.atwiki.jp/kumiho_k/pages/15.html)（「左手座標系(データは左手座標系。MMDの画面表示は右手座標系。)」「ボーンの回転角はクォータニオンで記録」，1 记录 111 字节）与 mmd_tools 代码 `struct.unpack("<fff")`/`"<ffff"`，全零四元数视为 (0,0,0,1) — [mmd_tools core/vmd/__init__.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/vmd/__init__.py)
- 位置为相对绑定姿态：「The position data of the bones in the PMD model are relative to the world's origin, and the position data here is relative to that」 — [MMD fandom: VMD file format](https://mikumikudance.fandom.com/wiki/VMD_file_format)
- **旋转在父骨轴系中**：motion data (.vmd) 记录的是相对父骨轴的旋转，因此改变父子结构会改变导入动作的表现（肩P 重排案例） — [PIP_MMD: 肩Pの話](https://pip-mmd.hatenablog.com/entry/2017/10/03/010753)
- **PMX 规范的局部变形公式**（无静止旋转项）：回転量 = 「[親付与回転量(or 親回転 * 親回転モーフ) * 付与親のIKリンク]:付与率 * 回転 * 回転モーフ * IKリンク」；「ローカル行列 = (スケール行列) * 回転行列 * 移動行列 を計算、親ボーンからのオフセット及び親のローカル行列に合成する」 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)
- **ローカル軸/軸固定 不影响变形**：「0x0001 接続先 / 0x0002 回転可能 / 0x0004 移動可能 / 0x0008 表示 / 0x0010 操作可 / 0x0400 軸固定 / 0x0800 ローカル軸 は、表示及び操作時の制限項目になる。ボーンの変形特性や内部値には関与しないので注意」；制限軸「PMDの捩りボーンと同系の仕組み。捩りボーン同様ボーンの内部変形量には関与しない。操作時の移動及び回転軸を指定した軸方向で固定化する機能」；ローカル軸「操作上のローカルフレームを任意に定義するための軸方向パラメータ。X／Zで指定…Y = Vector3.Cross(Z, X); Z' = Vector3.Cross(X, Y);」「PMDでは腕関連のみ子ボーンの方向をX、手前を-Zとする軸でローカルフレームが自動作成される模様」 — 同上
- 社区说法一致：ローカル軸「操作のためのもにすぎない」；「親指、人差し指、中指の順にX軸、Y軸、Z軸の向きが設定される」；设 X 后「Z軸は勝手に自動計算されます」 — [PIP_MMD: 面の向きにあったローカル軸](https://pip-mmd.hatenablog.com/entry/2025/02/20/171412)；「OFFになっていればグローバル向きにボーンが向きます」，轴向怪异只影响操作感（「X軸方向に回転させたい場合に横に回転してしまう」） — [note: MMDモデルの軸の向きが変…｜ig_k](https://note.com/ig_k/n/n4716da53ab2d)；搜索摘要（原页无法抓取）称 local axes「are for display and operation purposes, not for how MMD manages motions…which use global axes as the reference at the model's initial position」 — [ユルリトラボ: ローカル軸](https://yururitolabo.online/local-axis/)
- mmd_tools 导入 VMD 时用骨的静止矩阵把四元数变换到 Blender 骨空间：`rot = Quaternion((w, x, y, z)); q = self.__mat.to_quaternion(); result = q @ rot @ q.conjugated()`，其中 `mat = pose_bone.bone.matrix_local.to_3x3(); mat[1], mat[2] = mat[2].copy(), mat[1].copy()`，且不引用任何 local_axis 属性 — [mmd_tools core/vmd/importer.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/vmd/importer.py)（即 MMD 侧四元数本身是在轴对齐的父空间里定义的）
- 动作修正经验：手臂动作不对「基本的には肩から直すのが私のやり方です」（再到 ひじ/腕/手首） — [はじめてのMikuMikuDance!: モーション修正](https://mikumikud.hatenablog.com/entry/2014/01/30/112032)；搜索摘要：流し込み时手臂埋进身体是因「モデルの腕の初期位置が低い」，解法是 PMXエディタ TransformView 选 腕 骨抬高并用 反転P 对称 — [MMDやろうず: 腕の埋没](https://ch.nicovideo.jp/TB_Horror/blomaga/ar680479)（页面已失效，仅摘要）；反向（A→T 以配合 Neuron 动捕）同样用 TransformView 调整「腕の関節あたり」，文中无具体角度 — [Qiita: A字型のモデルをT字スタンスに変換](https://qiita.com/ngron/items/53dc7e9c6b6d291b784e)
- 「Is it possible for an MMD character model to have some additional non-standard bones without messing up a VMD motion?: Yes…arm twist bones, one or two additional upper body bones, an additional thumb bone…If bone A is child of bone B…and you insert another bone, so that bone A is the child of the child of bone B, that should not cause an incompatibility problem」 — [Hogarth armature notes](https://github.com/Hogarth-MMD/mmd_tools_helper/blob/master/tutorials%20MMD%20standard%20armature/MMD%20standard%20armature%20notes.txt)
- 捩骨的目的：多边形「苦手な回転」= 沿长轴的扭转，捩骨把扭转沿臂长分散 — [くぅ＆みぃ](https://q-ku.blog.jp/archives/11315486.html)；Nuthouse01 的 `bone_set_arm_localaxis` 为 肩/腕/ひじ/手首 设 ローカル軸，并把 腕捩/手捩 修正到与 腕–ひじ 共线（容差 0.0001） — [bone_set_arm_localaxis.py](https://github.com/Nuthouse01/PMX-VMD-Scripting-Tools/blob/master/mmd_scripting/scripts_for_gui/bone_set_arm_localaxis.py)

### Inferences
- **数学解释**：设 VMD 给 腕 的四元数 q 是「以 A-pose 静止臂向 a 为零点」的旋转；对 T-pose 模型（静止臂向 t），MMD 同样把 q 作用在父空间，得到的臂向为 R(q)·t 而非 R(q)·a，因此每一帧都带有常量误差 δ = ∠(t,a)（上臂约 30°，前臂另加约 10°），表现为双臂整体抬高/外翻、手部穿模。因 PMX 没有静止旋转字段，唯一的修正办法是把 XPS 网格与骨骼位置一起旋转到 A-pose（骨头位置 = 旋转后的关节位置），不能靠 ローカル軸 修正。
- **建议目标姿态**（以 ver.2.3 为基准）：上臂低于水平 ≈30°（TDA 等常见模型未验证，Hogarth 泛称 45°），前臂再向下 ≈10°（整臂 ≈34～40°），肘略向后/外；手掌朝下略内旋（ver.2.3 手首→中指１ 方向 (0.877,−0.762,−0.042)，拇指在 −Z 前侧）；手指基本伸直微曲、略分开（指骨坐标见问题 1）；腿近竖直（1.5°）并有 4° 膝弯，脚尖朝 −Z 平贴地面。Blender 侧做法：对 XPS 骨架施加姿态→Apply as Rest Pose→再导出位置。
- 由于 肩/腕/ひじ 的 VMD 旋转在世界对齐的父空间中，XPS 模型的 肩 骨位置（锁骨根）与 腕 骨位置（肩头）也应与 MMD 比例接近（肩 X≈0.136、腕 X≈0.891 单位，Y 差 0.44），否则 肩 的旋转会把上臂带到不同位置。

### Gaps
- 未找到社区明文的「T→A 旋转角度数值」（如 35°/40°）；仅有 DanceXR 的可调滑块与博客的手工 TransformView 操作。TDA 式等「典型模型」的实际臂角未测得。
- MMD 本体对带 ローカル軸 骨在「ローカル」操作模式之外是否有任何动作期行为差异，除规范文字外没有源码级证据（MMD 闭源）。

---

## 问题 5：尺度与坐标系

### Takeaway
あにまさ式ミク 顶点最高 20.214 单位，按官方身高 158 cm 得 1 单位 ≈ 7.82 cm（社区通用口径「20 单位 ≈ 7.9～8 cm」，mmd_tools 默认 0.08 m/单位）；MMD/PMX 为左手系 Y-up、+Z 朝屏幕深处，模型面向 −Z（脚尖/视线在 −Z），地面 Y=0，センター 高 8.0。

### Cited Findings
- 「Miku herself is a little more than 20 MMD units tall」；若按 20 单位算「each unit measures 7.9 centimeters」，约 8 cm / 3 inch；「Each grid square that you see in MikuMikuDance is 5X5 units」；基于 Miku 官方身高 158 cm；并提醒「no one seems to know exactly」 — [Hogarth-MMD: 1 MMD unit in real world units](https://www.deviantart.com/hogarth-mmd/journal/1-MMD-unit-in-real-world-units-685870002)
- **实测**：ver.2.3 顶点 Y ∈ [0.031, 20.214] → 158 cm / 20.214 = **7.816 cm/单位**；センター Y=8.0；脚尖骨 Y=0.0；足首 Y=1.34 — [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)
- mmd_tools 导入 PMX 的 `scale` 默认 **0.08**（Blender m / MMD 单位），导出默认 **12.5** — [mmd_tools operators/fileio.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/operators/fileio.py)
- 坐标系：VMD/PMD「左手座標系(データは左手座標系。MMDの画面表示は右手座標系。)」 — [kumiho_k VMD wiki](https://w.atwiki.jp/kumiho_k/pages/15.html)；PMX 面「Triangle facing is defined in clockwise winding order (As with DirectX)」 — [felixjones PMX gist](https://gist.github.com/felixjones/f8a06bd48f9da9a4539f)；pymeshio 注明「left-handed Y-up DirectX coordinates」 — [pymeshio pmd](https://pythonhosted.org/pymeshio/pymeshio.pmd-pysrc.html)
- mmd_tools 的轴变换：顶点 `Vector(pv.co).xzy * self.__scale`，骨位置同样 `.xzy`（MMD (x,y,z) → Blender (x,z,y)） — [mmd_tools core/pmx/importer.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/pmx/importer.py)；VMD 导入时 `mat[1], mat[2] = mat[2].copy(), mat[1].copy()` — [core/vmd/importer.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/vmd/importer.py)
- **模型朝向（一次数据）**：左つま先 (0.929, 0, −2.464) 相对 左足首 (0.875, 1.34, 0) 在 −Z；両目先 (0,21,−1.5) 相对 両目 (0,21,−0.7) 在 −Z；左目先 Z=−0.897 < 左目 Z=−0.348；足ＩＫ先 在 +Z（脚后） — [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)
- VRM→PMX 转换文章（搜索摘要）：「VRMは右手座標系（Y-up、-Zが前方）であり、MMD/PMXは左手座標系（Y-up、+Zが前方）なため、変換時にZ軸を反転する必要があります」 — [PROTOCOL.LAIN: VRM to MMD(PMX) 変換ツール](https://lain-lab.com/posts/javascript-vrm-to-mmd-converter/)（此处「前方」指坐标轴/视线深度方向，不是模型面向；与一次数据「模型面向 −Z」并不矛盾，但措辞易混淆）
- PMX 位置存储：骨「12 : float3 | 位置」，顶点「12 : float3 | 位置(x,y,z)」，无单位字段 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)

### Inferences
- XPS→PMX 的尺度换算：若 XPS 模型以米为单位，乘 12.5（=1/0.08）；若以 cm，乘 0.125；更稳妥的做法是按目标身高归一化（成人女性 ≈20 单位，男性 ≈22～23 单位），因为 VMD 的 センター/足ＩＫ 位移是绝对单位，身高差太大会导致步幅与脚 IK 不匹配。
- 轴映射（Blender 右手 Z-up → MMD）：MMD(x,y,z) = (B.x, B.z, B.y)，即交换 Y/Z（交换两轴本身改变手性，故无需再取负）；Blender 中面向 −Y 的模型转换后面向 −Z，与 MMD 一致。

### Gaps
- MMD 官方从未定义单位与现实尺度的关系；7.8～8 cm 为社区推算。

---

## 问题 6：表示枠（Display frames）

### Takeaway
PMX 规范要求首两枠为特殊枠 `Root`（含首骨/全ての親）与 `表情`（PMD 兼容表情枠）；あにまさ式 ver.2.3 的骨枠顺序为 ＩＫ, 体(上), 髪, 腕, 指, 体(下), 足；准标准插件会在 Root/表情 之后新建「センター」枠放 グルーブ/腰 等，并把新骨登记到其依赖骨所在枠。

### Cited Findings
- 规范：「PMXの初期状態では、表示枠:0(先頭) -> "Root"(特殊枠指定) | 枠内に ボーン:0(先頭ボーン)を追加。対応されれば枠のルート位置への設定用 / 表示枠:1 -> "表情"(特殊枠指定) | PMD変換時は枠内に 表情枠 と同様の配置」；「特殊枠判定は、特殊枠フラグ1及び枠名で判断(編集時に誤って削除しないように注意)」；枠记录 = 枠名/枠名英 TextBuf + 「特殊枠フラグ 0:通常枠 1:特殊枠」+ 要素数 + 每要素「要素対象 0:ボーン 1:モーフ」+ 索引 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)
- 「PMD互換として標準でRoot枠（センター用）やPMD用の表情枠も作成されます」 — [VPVP wiki: PMXの概要](https://w.atwiki.jp/vpvpwiki/pages/284.html)
- **ver.2.3 PMD 骨枠**（PMD 无显式 Root/表情，センター 由 MMD 隐式显示）：`ＩＫ`=[ﾈｸﾀｶＩＫ, 左髪ＩＫ, 右髪ＩＫ, 左足ＩＫ, 右足ＩＫ, 左つま先ＩＫ, 右つま先ＩＫ]；`体(上)`=[上半身, 首, 頭, 左目, 右目, 両目, 左目光, 右目光, ﾈｸﾀｲ１〜３]；`髪`=[前髪１〜３, 左髪１〜６, 右髪１〜６]；`腕`=[左肩, 左腕, 左腕捩, 左ひじ, 左手捩, 左手首, 左袖, 右…]；`指`=[左親指１…左小指３, 右…]；`体(下)`=[下半身, 腰飾り, 左右ｽｶｰﾄ前/後]；`足`=[左足, 左ひざ, 左足首, 右足, 右ひざ, 右足首]；英文枠名 IK / Body[u] / Hair / Arms / Fingers / Body[l] / Legs；枠名字段 50 字节 — [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)、[pymeshio](https://pythonhosted.org/pymeshio/pymeshio.pmd-pysrc.html)
- **PMX 转换后（Hogarth 文件）**：`Root`(special=1)=[全ての親, センター]；`表情`(special=1)=[]；`ＩＫ`=[左足ＩＫ, 右足ＩＫ, 左つま先ＩＫ, 右つま先ＩＫ]；`体(上)`=[上半身, 首, 頭, 左目, 右目, 両目]；`髪`=[]；`腕`；`指`；`体(下)`=[下半身]；`足`=[左足, 左ひざ, 左足首, 右足, 右ひざ, 右足首, 左つま先, 右つま先] — [Hogarth PMX 本地解析](https://github.com/Hogarth-MMD/mmd_tools_helper/tree/master/pmx%20example%20armatures)
- 准标准插件（移植版）：`createCenterLabel()` 在不存在「センター/center」枠时于 index 2 插入（注释「0 for root and 1 for expression/morph」）；`setRootLabel()` 清空 Root 枠并放入新根骨（全ての親/操作中心），原首骨（センター）若无所属枠则放入「センター」枠；其他新骨 `insertLabelAfter/Before` 登记到依赖骨所在枠的相邻位置 — [nanoem ssb.cc](https://github.com/hkrn/nanoem/blob/main/emapp/plugins/ssb/ssb.cc)；文档表格：腰→依赖 下半身、グルーブ→センター、全ての親/操作中心→(最初のボーン) — [nanoem 文档](https://nanoem.readthedocs.io/ja/latest/plugin.html)
- mmd_tools 新建模型时初始化 `{"Root": "Root", "表情": "Facial"}` 两枠并置 `is_special = True`，固定在 index 0/1 — [mmd_tools core/model.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/model.py)
- Nuthouse01 工具「display frame cleanup: will now make "center" group follow semistandard conventions」 — [Nuthouse01 README](https://github.com/Nuthouse01/PMX-VMD-Scripting-Tools/blob/master/README.md)
- VMD 的名称限制作用于「モデルデータ内[表示枠]に登録してる"ボーン名"モーフ名"」（只有登记进表示枠的骨/表情才会出现在 MMD 时间轴并被录入 VMD） — [posfie: VMDは15バイトの文字制限](https://posfie.com/@tryme_/p/IX2iSDC)

### Inferences
- 推荐输出顺序：`Root`(special)[全ての親]、`表情`(special)[全部表情]、`センター`[センター, グルーブ, 腰(或并入体(下))]、`ＩＫ`[左足IK親, 左足ＩＫ, 左つま先ＩＫ, 右…]、`体(上)`[上半身, 上半身2, 首, 頭, 左目, 右目, 両目]、`腕`[左肩P, 左肩, 左腕, 左腕捩, 左ひじ, 左手捩, 左手首, 左ダミー, 右…]、`指`[左親指０, 左親指１, …]、`体(下)`[下半身]、`足`[左足, 左ひざ, 左足首, 左つま先, 左足先EX, 右…]、`その他`/`物理`。D 骨、肩C、腰キャンセル、腕捩1〜3 默认不登记（不可见控制骨）。

### Gaps
- 「その他」等补充枠的命名无官方标准，属社区惯例。

---

## 问题 7：标准表情（モーフ）清单与常用动作数据的依赖

### Takeaway
一次数据给出 あにまさ式 ver.2.3 的 30 个表情（按 眉/目/リップ/その他 分面板，含英文名），日文社区明确「配布モーションはあにまさ式ミクの表情を基準に作られている」，另有 TDA 式扩展（はちゅ目, 星目, 口角上げ/下げ, 頬染め, 青ざめ 等）；「え」不在 あにまさ 集合中但被视为必备。

### Cited Findings
- **ver.2.3 PMD 表情（面板码 1=眉 2=目 3=リップ 4=その他；英文为文件自带）**：眉：真面目 serious, 困る sadness, にこり cheerful, 怒り anger, 上 go up, 下 go down；目：まばたき blink, 笑い smile, ウィンク wink, ウィンク２ wink2, ウィンク右 wink_R, ｳｨﾝｸ２右 wink2_R, はぅ close><, なごみ calm, びっくり surprise, じと目 doubt, なぬ！ confuse；リップ：あ a, い i, う u, お o, ▲ triangle, ∧ regret, ω omega, ω□ omegabox, はんっ！ fool, えー e-, にやり grin；その他：瞳小 pupil, ぺろっ tongue；MMD 面板显示顺序：あ, い, う, お, ▲, ∧, ω, ω□, はんっ！, えー, にやり, まばたき, 笑い, ウィンク, ウィンク２, ウィンク右, ｳｨﾝｸ２右, はぅ, なごみ, びっくり, じと目, なぬ！, 真面目, 困る, にこり, 怒り, 上, 下, 瞳小, ぺろっ — [miku_v2.pmd 本地解析](https://github.com/mrdoob/three.js/tree/r100/examples/models/mmd/miku)（PMD skin type 0 base/1 眉/2 目/3 リップ/4 その他 — [pymeshio](https://pythonhosted.org/pymeshio/pymeshio.pmd-pysrc.html)）
- PMX 面板字节：「操作パネル (PMD:カテゴリ) 1:眉(左下) 2:目(左上) 3:口(右上) 4:その他(右下) | 0:システム予約」 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)
- 「配布モーションは…あにまさ式ミクさんの表記…基準につくられている」；标准表（あにまさ式ミク ver.2.3 基準）：【まゆ】真面目、困る、にこり、怒り、上、下；【目】まばたき、笑い、ウィンク、ウィンク２、ウィンク右、ｳｨﾝｋ２右、はぅ、なごみ、びっくり、じと目、なぬ！；【リップ】あ、い、う、お、▲、∧、ω、ω□、はんっ！、えー、にやり；【その他】瞳小、ぺろっ；建议追加：【目】睨み（睨む）、白目、瞳大；【リップ】**え（标为必备，「ミク lacks it」）**、口角上げ、口角下げ；【その他】頬染め、青ざめ — [一護牛乳: MMD表情モーフ一覧](https://mmd15gyuunyuu.blog.jp/archives/11193436.html)
- 「MMD表情はあにまさ氏の『初音ミク ver.2.3』にある表情が基本形で、これは作った方が良い」，进阶参考 TDA 式 初音ミク；扩展清单——眉：真面目, 困る, にこり, 怒り, 上, 下；目：まばたき, 笑い, ウィンク, ウィンク２, ウィンク右, ｳｨﾝｸ２右, はぅ, なごみ, びっくり, じと目, なぬ！, 下まぶた上げ, 瞳大, 瞳小, ハイライト消し, はぁと, 星目, はちゅ目, 恐ろしい子！（白目）；口：あ, い, う, え, お, にやり, ∧, ▲, ω, ω□, はんっ！, えー, 口角上げ, 口角下げ；その他：頬染め, ぺろっ, 青ざめ — [しぐにゃも: MMD＋VRChat＋VRMに必要な表情モーフ一覧](https://signyamo.blog/3d-facial/)
- mmd_tools 词表中的表情相关译名：照れ→Blush, 青ざめ→Pale, ガーン→Gloom, 汗→Sweat, 涙→Tears, 泣き→Cry, 怒→Anger, 眉→Eyebrow, 舌→Tongue, 歯→Teeth — [mmd_tools translations.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/translations.py)
- 名称匹配规则：VMD 表情帧「15b char-string, name of the facial/morph / 4b uint frame / 4b float value/weight」，按名字匹配 — [Nuthouse01 README](https://github.com/Nuthouse01/PMX-VMD-Scripting-Tools/blob/master/README.md)；mmd_tools 读取时若 cp932 不支持或名字在 15 字节处被截断则出现替换字符 — [mmd_tools core/vmd/__init__.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/vmd/__init__.py)

### Inferences
- **核心集（出现于绝大多数配布表情/口型数据）**：あ, い, う, え, お（口型基础，え 需补）、まばたき, 笑い, ウィンク, ウィンク２, ウィンク右, ｳｨﾝｸ２右, はぅ, なごみ, びっくり, じと目、真面目, 困る, にこり, 怒り, 上, 下、▲, ∧, ω, ω□, にやり, えー, はんっ！、ぺろっ, 瞳小——即 あにまさ ver.2.3 全集 + え。**扩展集（TDA 系常见）**：はちゅ目, 星目, はぁと, 瞳大, 下まぶた上げ, ハイライト消し, 白目, 口角上げ, 口角下げ, 口横広げ, 歯無し上/下, にっこり, にやり２, ワ, あ２, ん, □, てへぺろ, 照れ/頬染め, 涙, がーん, 青ざめ——其中 ワ, あ２, ん, □, にやり２, にっこり, 口横広げ, 歯無し上/下, てへぺろ, 涙, がーん 在本次来源中未被逐项证实为 TDA 原生，仅属任务提示中的常见名称（标为未验证）。
- 名称必须逐字节一致（含半角片假名 ｳｨﾝｸ２右 与全角数字），建议直接复制上表字符串。

### Gaps
- 未取得 TDA 式 初音ミク 的官方表情清单原文，扩展集中部分名称未验证来源。
- 没有量化的「动作数据使用频率」统计，「核心/扩展」划分依据社区文章的定性说法。

---

## 问题 8：命名与格式约束（PMD/PMX/VMD）

### Takeaway
PMX 文本为 int 长度前缀的 UTF-16LE/UTF-8，不限长；但 VMD 骨/表情名固定 15 字节 Shift-JIS（约全角 7 字），超长会被截断且不同名字可能被视为同一骨；PMD 名 20 字节、枠名 50 字节、权重仅 2 骨整数；PMX 2.0 为 MMD 7.31+ 唯一可读版本，2.1（QDEF/SoftBody/フリップ・インパルスモーフ/新 Joint 类型）会触发「PMXファイルのバージョンは2.0しか読み込めません」；骨标志为 16 位位域，変形顺序 = 物理前/后 → 変形階層 → Index。

### Cited Findings
- **PMX 头与文本**：「"PMX " ASCIIで 0x50,0x4d,0x58,0x20 ※末尾空白に注意 (PMX1.0は"Pmx ")」「float ver (2.0/2.1)」「後続するデータ列のバイトサイズ PMX2.0は 8 で固定」，8 字节依次 [0] エンコード 0:UTF16 1:UTF8、[1] 追加UV数 0〜4、[2]〜[7] 頂点/テクスチャ/材質/ボーン/モーフ/剛体 Index サイズ 1,2,4；TextBuf = 「int : バイト長 / byte * バイト長」（无长度上限）；索引字节数按数量优化：顶点无符号 1:0〜255 / 2:256〜65535 / 4:65536〜；骨等有符号 1:0〜127 / 2:128〜32767 / 4:32768〜，「ボーンや剛体などは -1を非参照値として扱います。材質は材質モーフにより-1:全材質」 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)
- **权重**：「1頂点につき最大4ボーンまで」；BDEF1 单骨权重 1.0；BDEF2 两骨 + 骨1权重（骨2 = 1−骨1）；BDEF4 四骨四权重「ウェイト合計が1.0である保障はしない」；SDEF = BDEF2 + C/R0/R1 三个 float3「実際の計算ではさらに補正値の算出が必要(一応そのままBDEF2としても使用可能)」；2.1 增 QDEF（与 BDEF4 同格式，「DualQuaternion 方式」） — 同上
- **骨标志位（16 bit）**：0x0001 接続先(0:座標オフセット 1:ボーン指定)、0x0002 回転可能、0x0004 移動可能、0x0008 表示、0x0010 操作可、0x0020 IK、0x0080 ローカル付与、0x0100 回転付与、0x0200 移動付与、0x0400 軸固定、0x0800 ローカル軸、0x1000 物理後変形、0x2000 外部親変形；骨记录顺序：名/名英/位置 float3/親Index/変形階層 int/フラグ 2byte/[接続先]/[付与親Index+付与率 float]/[軸方向 float3]/[X軸 float3 + Z軸 float3]/[外部親 Key int]/[IK] — 同上（mmd_tools 以同一组 0x 常量解析 — [mmd_tools core/pmx/__init__.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/pmx/__init__.py)；miu 的 `BoneFlg` 同，并注 0x0080「付与対象 0:ユーザー変形値／IKリンク／多重付与 1:親のローカル変形量」 — [bone_setting.py](https://github.com/miu200521358/mmd_base/blob/develop/mlib/pmx/bone_setting.py)）
- **変形順序**：「1. 物理前／後 2. 階層順 3. Index順 にて調整(正規化)後、順に変形を行う。1つのボーンにおけるローカル変形処理はIKからのリンク参照を除いて1回のみ」，示例：前,階層0,Index2 → 前,階層0,Index4 → 前,階層1,Index5 → 前,階層2,Index0 → <物理演算> → 後,階層0,Index3 → 後,階層1,Index1；「物理変形後の適用は、物理変形によるグローバル変形量をローカル変形量に一旦戻し、それを親参照する変形を継続することで行われる」；付与「付与親の親子変形によるボーン変形状態は付与対象ではないので注意」（仅局部付与例外）；「親子変形による伝達が必要な変形は、親→子順にボーン変形を呼び出す必要がある」；用户操作量的付与「付与親の変形前にボーン変形が呼び出されても正常に変形する(ただし1段階のみ／多重付与を行う場合は付与親が先に変形されている必要がある)」 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)
- PMX 的变形「ボーン種類(属性)に関わらずIndex／変形階層／物理演算後の各設定により順次変形する仕組み」，PMD 则「基本的にIndex順に順次変形…回転影響下／IK変形が全変形後に再度行われる」 — [VPVP wiki: PMXの概要](https://w.atwiki.jp/vpvpwiki/pages/284.html)；korarei 笔记：「変形階層の値が小さいグループから順に処理され、そのグループ内ではインデックスの小さい順に処理されます」，回転＋/移動＋ 需「コピー元→コピー先」顺序，足部结构「足系ボーン→IKボーン→D系ボーン」三段 — [scrapbox korarei: MMDのボーン設定](https://scrapbox.io/korarei/MMD%E3%81%AE%E3%83%9C%E3%83%BC%E3%83%B3%E8%A8%AD%E5%AE%9A)
- **モーフ类型**：0 グループ, 1 頂点, 2 ボーン, 3 UV, 4〜7 追加UV1〜4, 8 材質，2.1 增 9 フリップ, 10 インパルス；「※仕様上グループモーフのグループ化は非対応」；材质モーフ「0:乗算, 1:加算」 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)
- **2.0 → 2.1 差异**：SoftBody 数/数据追加到末尾；QDEF；材质描画フラグ增 0x20 頂点カラー / 0x40 Point描画 / 0x80 Line描画，エッジサイズ兼作 Point サイズ；面允许 A-A-A / A-B-A；Joint 由仅「0:スプリング6DOF」增至 6DOF/P2P/ConeTwist/Slider/Hinge；SoftBody 形状 TriMesh/Rope 等 — 同上及 [felixjones gist](https://gist.github.com/felixjones/f8a06bd48f9da9a4539f)
- **MMD 支持矩阵**：「PMX形式は、2.0と2.1があり、2.0はMMD ver.7.31以降で対応」；表格 MikuMikuDance 7.31〜 PMD ○ / PMX 2.0 ○ / PMX 2.1 ×；PMXエディタ 2.0 ○ 2.1 ○ — [VPVP wiki: PMXの概要](https://w.atwiki.jp/vpvpwiki/pages/284.html)
- 触发 2.1 的设置：「モーフ：インパルスモーフ、Joint：Joint種類＞バネ付き6DOF（標準）以外、softbody：すべて」以及 QDEF；MMD 报错「PMXファイルのバージョンは2.0しか読み込めません」；改回：「Pmx編集 ファイル＞保存時処理＞PMXバージョン選択＞2.0」；「MMMでも2.1形式に完全対応していない」 — [たるっこ: PMXファイルバージョンの罠](http://tarucco2.blog.shinobi.jp/atelier/pmx%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%83%90%E3%83%BC%E3%82%B8%E3%83%A7%E3%83%B3%E3%81%AE%E7%BD%A0)、[Yahoo!知恵袋](https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11147374276)（摘要）
- **PMD 限制**（PMD vs PMX 对照表）：文本 固定サイズ/シフトJIS vs 可変/ユニコード；顶点 65536(16bit) vs 约 40 億；权重「2ボーン / 整数（0〜100）/ BDEF」vs「4ボーン / 実数 / BDEF／SDEF（SDEF はボーン数2まで）」；贴图名「19文字まで」（「テクスチャ名・スフィア名の合計が半角英数で18文字以内…*も含めて19文字以内」）；「PMDでは20byte程度の容量しか用意されていない場合もあります」；骨「ボーン種類(10種)」vs 个别参数化；「〜先ボーン 設定が必要」vs「座標オフセットで指定可能」 — [VPVP wiki: PMXの概要](https://w.atwiki.jp/vpvpwiki/pages/284.html)；PMD 结构：20 字节模型名、256 字节注释、骨 20 字节名、表情 20 字节名、枠名 50 字节，cp932 编码 — [pymeshio pmd](https://pythonhosted.org/pymeshio/pymeshio.pmd-pysrc.html)
- **VMD 15 字节**：骨名/表情名「15b char-string」，模型名 20 字节（旧版 10），IK 显示帧内骨名 20 字节；文件 shift_jis — [Nuthouse01 README](https://github.com/Nuthouse01/PMX-VMD-Scripting-Tools/blob/master/README.md)；mmd_tools 注释「Bone/Morph name was truncated at 15 bytes, breaking character boundaries」 — [mmd_tools core/vmd/__init__.py](https://github.com/UuuNyaa/blender_mmd_tools/blob/main/mmd_tools/core/vmd/__init__.py)；社区：「VMDの文字制限とはモーションを製作・保存目的に使用したモデルデータ内[表示枠]に登録してる"ボーン名"モーフ名"が相当します」，超 15 字节被截断导致「0123456789012345と0123456789012346が同じ扱いになっちゃう」，「ボーンが名が全角で８文字以上だとvmd保存されないんだよね」 — [posfie: VMDは15バイトの文字制限があるよまとめ](https://posfie.com/@tryme_/p/IX2iSDC)；搜索摘要（未逐字核对）：「MMDが読める名称長さは19バイトであるのに対し、VMDで保存できる名称長さは15バイト」 — [ニコニ・コモンズ sm40920052](https://commons.nicovideo.jp/works/sm40920052)
- 名称区分：插件「ボーン名の判定において全角英数字と半角英数字を区別します」，例如 足IK親 用半角 IK 而 足ＩＫ 用全角 — [nanoem 文档](https://nanoem.readthedocs.io/ja/latest/plugin.html)；动作播放异常「it is very likely that there is a name mismatch」 — [Nuthouse01 README](https://github.com/Nuthouse01/PMX-VMD-Scripting-Tools/blob/master/README.md)
- PMD→PMX 转换：「PMXでは原則1ボーンに対して1つのIKのみ設定可能」；PMX→PMD「仕様の違いにより多くのデータが欠落します【例】テキストデータ、モーフ（UV／ボーン／材質／グループ）、移動付与ボーン、SDEF、BDEF4他」 — [VPVP wiki: PMXの概要](https://w.atwiki.jp/vpvpwiki/pages/284.html)
- 规范使用条件：「各アプリケーションなどでのフォーマットの利用については、非営利であれば自己責任において自由に行ってください」；「PMX1.0は非公開」 — [PMX仕様.txt](https://gist.github.com/FlandreDaisuki/90ae5abf3138a15994526b6bfec73c2c)

### Inferences
- **插件输出策略**：写 PMX 2.0、UTF-16LE（PMXEditor 默认）、BDEF1/2/4 + 可选 SDEF，不使用 QDEF/SoftBody/非标准 Joint；索引字节按数量选 1/2/4；所有需进 VMD 的骨/表情名 ≤15 字节 Shift-JIS（全角 ≤7 字），且在模型内唯一（PMX 本身不强制唯一，但 VMD 按名匹配，重名/截断同名会互相覆盖）；英文名可任意长。
- 変形階層：普通骨 0；回転付与骨（左目/右目、肩C、腰キャンセル、腕捩1〜3）置于其付与親之后即可（同层靠 Index 顺序），或按 PMD→PMX 官方惯例设 IK 链 1、回転影響下 2；足D 链设「原骨 +1」（nanoem）；物理后骨仅用于物理驱动的附属骨。
- MMD 的 UI 并无「15 字字符截断」之说可证；真正的硬限制来自 VMD 字段长度（见 Gaps）。

### Gaps
- 「MMD 可读 19 字节」仅见于搜索摘要，未核对原文；MMD 界面显示截断规则无来源。
- PMX 规范未规定骨名唯一性，PMXEditor 对重名的提示行为未查证。
- ローカル付与（0x0080）在 MMD 本体中的支持程度无一手资料。
