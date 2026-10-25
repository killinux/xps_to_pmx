# 本机 XPS 样本测量:尺度、骨骼命名与格式细节

> 测量日期:2026-10-25。目的:给 XPS→PMX 插件的"尺度 / 身高归一化策略"提供实测依据("测一下"),并摸清本机语料里真实的骨骼命名约定。
>
> 工具(本次新写,纯 Python、无 bpy):`xps_to_pmx/core/xps/reader.py`(读取器)+ `scripts/survey_xps_corpus.py`(扫描脚本)。
> 第 6 节"原始测量数据"由脚本写入 `BEGIN/END GENERATED` 标记之间,重跑脚本只替换该区块;第 0–5 节为人工解读,数字取自同一次运行。
> 记号:`#N` 指第 6 节表格里的文件编号;高度单位为文件原始单位(结论:米);坐标为 XNA 约定(+Y 向上)。

## 0. 结论速览

1. **XPS 单位 = 米,实测确认。** 170 个文件全部解析成功(147 个字节唯一)。123 个完整角色(排除文件名含 pose 的姿势变体)的 bbox 高度:min 1.519 / P25 1.679 / **中位 1.730** / P75 1.796 / max 2.095。头骨高度中位 1.528(1.388–1.880),髋骨高度中位 0.993(0.860–1.406)。语料中没有任何厘米、英寸或其它单位的模型。
2. **用户已有的 PMX 转换只用过两个系数。** 拿同目录 89 个带网格的 PMX 和对应 XPS 比 bbox 高度:**×10 共 43 个**,全部是批量产物 `xps_new.pmx` / `*_new.pmx`;**×12.5 共 31 个**,是手工定稿,如 `alana_bone_l_g2_final*`、`cartilla_413_12.5*`、`misaki.pmx`、`329.pmx`、Diana 的多数变体。另有 3 个 ×1(未缩放),其余是 9.6–12.7 的个别值(PMX 与 XPS 网格组成不同)。×12.5 正是"1 MMD 单位 = 8 cm"的米制换算。
3. **建议的尺度策略。** 默认固定 ×12.5。可选"按身高归一化",但必须用**骨骼地标**(头骨或髋骨高度),不能用网格 bbox 或骨架范围:
   - 网格 bbox 会被饰品放大:头骨以上的部分中位 +0.19 m,最多 +0.51 m(兔耳、翅膀、头饰);地面以下还可能挂道具,最低见到 −0.25 m 的 `+minigun`;
   - 骨架范围里有游戏定位骨,远在 y≈−22~−24 m。

   另外需要一个"落地"选项:minY 中位 −0.003,但 DAZ 系转换的鞋底普遍在 −0.05~−0.09。
4. **骨骼命名约定**(147 个唯一文件):
   - `xnalara_generic` 109 个,其中 99 个带 `unused*` 残留骨;
   - `daz_g8` 17 个(纯 DAZ 13 个,另 4 个混用通用名的脸/头发骨);
   - 其它 21 个:单骨道具 5、Auto-Rig Pro 4、3ds Max Biped 4、`L_/R_/M_` 前缀 3、RE Engine 3、Unreal 1、Valve Biped 1。

   **需要修正一个前提**:lezisell 转的 Rise of Eros 模型是**纯通用名**,外加 `unused bip001 …` 残留。这批文件在 `riseoferos/`、`riseoferos2/`、`2025money/wish/` 和 `inase (purifier)_lezisell-A`。DAZ G8 骨名来自另一个转换来源:Super Moon (Misaki)、Purifier (Inase)、Divine Grace (Lynn)、Reika、Tifa Gantz、Eve Monokini、Fiona、Neurocircuit。
5. **`unused*` ≠ 无权重。** 99 个模型里共有 5 403 根 `unused*` 骨,其中 1 928 根(36%,分布在 82 个模型)带顶点权重,包括原始骨盆和大腿/小腿/前臂扭转骨。所以 01 笔记里"`unused` 前缀骨骼可直接剔除"的推断要改为:**只有无权重的才能剔除**。
6. **渲染组。** 实际只出现 1–9、22–31、38–41。最常见的是 24(89 个模型)、25α(80)、7α(95)、4(38)、5(42)、6α(35)。没有出现 10–21(无光照/顶点光照)、32–37、42/43,也没有未知编号。
7. **格式意外**(详见第 4 节):
   - 103 个 XPS 11.x 文件在网格表后附有 73/77/97 字节的"机器戳"尾部,内含保存者的局域网 IP 和网卡 MAC;
   - 5 个模型有权重和 > 1.01 的顶点(最高约 1.65);
   - 7 个模型有 > 4 个非零影响(最多 33);
   - 35 个模型的网格名带 Blender `.00N` 后缀;
   - 20 个模型在头部嵌入了默认姿势;
   - 没有任何文件设置 hasBoneDirections,也没有 ≤ 2.12 的旧头部文件。

## 1. 方法与命令

**读取器。** `load_xps(path, strict=False)` 按 01 笔记第 1 节实现:
- **二进制**:
  - 首个 uint32 等于 323232 时读头部:版本号、`XNAaraL`、settings 块(type 0 填充 / 1 默认姿势 / 2 flags);
  - 切线规则为"无头部,或 `major <= 2 and minor <= 12`";变长权重规则为 `major >= 3`;
  - 骨骼父索引是 int16,面索引是 uint32,顶点色是 uint8×4,每个 UV 层后跟一个 float4 切线(仅在有切线时)。
- **ASCII**:按行读取,`#` 后为注释,数值行跳过空行;容忍 CR CR LF 和 `-1.#IND`。
- **网格名**:解析渲染组、三个参数、`+/-` 可选项、`|` 分组、`.` 后缀和 `nPart!`。
- **`.pose`**:`load_pose()` 返回 `{骨名: (旋转°, 平移, 缩放)}`。
- **性能**:顶点用 `struct.iter_unpack` / 预编译 `Struct` 批量解包。

**扫描范围。** 根目录 `E:/day_work`、`E:/4090`,排除 `E:/code/model_tools`,再加 6 个额外样本:`E:/mywork` 下 4 个 Purifier/Inase 文件,另 2 个(Gantz Reika、Tifa Gantz)本已在根目录内。
- 匹配 `*.xps`、`*.mesh`、`*.ascii`(含 `*.mesh.ascii`),跳过文件名含 `.bak` 的文件;
- 按 SHA-1 去重,23 个字节相同的文件不重复解析,统计只用唯一文件;
- 怪名 `Generic_Item.mesh.ascii.mesh.ascii.mesh.ascii` 按规则"失败才跳过",实际解析成功,因而保留(#13);
- 10 个 `.pose` 文件用 `load_pose` 校验;
- 同目录的 `*.pmx` 用脚本内的最小 PMX 读取器取顶点 bbox,用于和既有转换比尺度。

**口径定义。**
- **bbox 高度** = 全部网格顶点的 maxY − minY,包含 `-` 默认隐藏的可选项;"默认可见高度"则排除 `-` 网格。
- **髋骨 / 头骨**:按优先级匹配,名字先小写,并把 `_` / `-` 当空格、去掉 ARP 的 `.x/.l/.r` 后缀。
  - 髋骨:`root hips` > `pelvis` > `hips` > `hip` > `bip001 pelvis` > … > ARP `root.x`;
  - 头骨:`head neck upper` > `head` > `bip001 head` > `valvebiped.bip01 head1` > `m head`。
- **角色**:同时满足——找到髋骨和头骨且头骨更高、顶点 ≥ 5000、网格最高点 ≥ 头骨、网格最低点 ≤ 0.3×髋骨高度。最后两条排除了只有头发的 hair.ascii 和缺头部网格的 Jill pl2000。
- **姿势变体**:文件名含 `pose` 的文件(`normal pose.xps`、`T-Pose.mesh` 等)不计入主统计,避免同一角色重复计数。

**命令**(系统 Python 3.13.12,位于 `D:\openclaw\python\python.exe`;Blender 3.6 自带 Python 3.10.13):

```
python --version
python -m pip install pytest                      # 原先没有 pytest,装入 9.1.1
python -m pyflakes xps_to_pmx tests scripts       # 无告警
python -m pytest tests -q                         # 18 passed(约 6 s)
"D:\Program Files\blender-3.6.15-windows-x64\3.6\python\bin\python.exe" tests\test_xps_reader.py
                                                  # 无 pytest 的纯脚本模式:18 passed (Python 3.10.13)
python scripts/survey_xps_corpus.py               # 生成本文件第 6 节(可加 --json 输出逐文件记录)
"D:\Program Files\blender-3.6.15-windows-x64\3.6\python\bin\python.exe" scripts/survey_xps_corpus.py --stdout-only --no-pmx
                                                  # 3.10 兼容性冒烟:170 个文件 0 失败
```

**耗时。** 170 个文件共 1.02 GB(唯一文件 935 MB、1157 万顶点):
- 本机多次运行总耗时 43–123 s,其中纯解析 29–87 s,随机器负载明显波动,约合每顶点 2.5–7.5 µs;
- 最慢的单个文件 2.5 s(27 MB、43 万顶点);
- 在 Blender 3.6 的 Python 3.10 下纯解析 99 s,约比 3.13 慢 2.5 倍;单个 10–20 MB 模型在 Blender 内仍是 1 s 量级。

## 2. XPS 单位与尺度策略

### 2.1 测量结果(123 个完整角色,非姿势变体)

| 指标 | min | P25 | 中位 | P75 | max |
|---|---|---|---|---|---|
| bbox 高度 | 1.519 | 1.679 | 1.730 | 1.796 | 2.095 |
| 头骨高度 Y | 1.388 | 1.488 | 1.528 | 1.544 | 1.880 |
| 髋骨高度 Y | 0.860 | 0.950 | 0.993 | 1.019 | 1.406 |
| bbox 高度 − 头骨离地高度(头骨以上的头发/帽子/耳朵) | 0.039 | 0.178 | 0.193 | 0.240 | 0.512 |
| 地面偏移 minY | −0.253 | −0.016 | −0.003 | 0.001 | 0.047 |
| 头骨 Y ÷ bbox 高度 | 0.705 | 0.854 | 0.880 | 0.893 | 0.927 |
| 髋骨 Y ÷ bbox 高度 | 0.436 | 0.551 | 0.576 | 0.585 | 0.671 |

### 2.2 判断:单位是米

- **绝对尺度**:bbox 1.52–2.10、头骨 1.39–1.88、髋骨 0.86–1.41,正是成年人含头发、鞋和饰品的米制尺寸。如果是厘米,数值会在 170 左右;如果是英寸,会在 67 左右。两者都没有出现。
- **比例**:髋骨约在身高的 0.58,头骨(颅底)约在 0.88,符合人体比例。
- **旁证一**:`roe_xps_addon.py` 导入 FBX 时把小于 0.5 的模型 ×100 后再导出 XPS(见第 5 节)。
- **旁证二**:用户手工定稿的 PMX 一律 ×12.5,即 1 MMD 单位 = 8 cm(见 2.4)。
- 01 笔记第 5 节"XPS 单位近似米"的推断由此得到证实,"本机无样本可测"这一缺口关闭。

### 2.3 离群值及其原因

- **Fubuki**(#103/#104):头骨 1.880、髋骨 1.406、bbox 2.10。模型本身整体放大了约 1.2 倍,不是单位问题。
- **alana 系列**:7 套服装的头骨都是 1.388–1.396,bbox 却在 1.519–1.973 之间。以 steelhare(#41)为例,兔耳 `38_+robousamimi` 顶到 1.72,地面以下的 `38_+minigun` 道具低到 −0.253。
- **inase (blesser)**(#5):bbox 2.055,头骨 1.543,多出的是头饰/背饰。
- **同角色、不同来源,绝对尺寸不同**:
  - Inase:lezisell 的 10 套服装头骨都是 1.543–1.545;DAZ 转换(#167/#168/#170)是 1.630,大 5.6%;
  - Reika:1.394(SSPD077)/ 1.488(DOA)/ 1.535–1.559(Gantz 套装,Unreal/ARP 骨架)/ 1.642(DAZ);
  - Eve:1.518(Biped)/ 1.542(通用)/ 1.608(DAZ);
  - Tifa:1.500(DAZ)/ 1.540 / 1.561。

  DAZ 系转换一贯偏大 4–6%。
- **骨架范围不可靠**:
  - Eve - Cooling Suit(#86)的 `FX_GunFire_Rail_End` 在 y≈−22 m;
  - Jill(#100/#101)的 `setProp B 01` 在 y≈−24 m。

### 2.4 既有 PMX 转换用的缩放(第 6 节 D8)

| PMX/XPS 高度比 | 个数 | 典型文件 |
|---|---|---|
| ×10.0 | 43 | `riseoferos*/…/xps_new.pmx`、`normal pose_new.pmx`、`rouffe_new.pmx`、`inase_arbiter.pmx`、`keleira.pmx` |
| ×12.5 | 31 | `alana.pmx`、`alana_bone_l_g2_final*.pmx`、`rouffe_finnal.pmx`、`cartilla_413_12.5.pmx`、`cartilla4xx_*_body*.pmx`、`arbiter_nomal.pmx`、`misaki.pmx`、`329.pmx`、Diana None/V1/V2/V4–V7 |
| ×12.4–12.7 | 5 | Diana V3/V8/Children/Inase、`lisa.pmx`(PMX 改过网格) |
| ×12.0 | 1 | `lynn12.pmx`(文件名即系数) |
| ×10.1–10.2 | 4 | SSPD077 的 Asagi/Reika(XPS 与 PMX 网格组成不同) |
| ×9.6–9.7 | 2 | Wonder Woman(同上) |
| ×1.0 | 3 | `cartilla.pmx`、`keleira0.1.pmx`、`329_converted.pmx`(未缩放) |

另有 33 个 0 顶点的"仅骨骼"PMX(`*_bone*.pmx`、`*_standbone*.pmx`、`*_lie*.pmx`),推测是骨骼编辑中间件,未计入比值。

### 2.5 建议(供决策)

1. **默认系数 ×12.5**(1 XPS 单位 = 1 m,1 MMD 单位 = 8 cm),与用户的手工定稿一致。UI 提供 ×12.5 / ×10 / 自定义三个预设;×10 是旧批处理产物 `*_new.pmx` 用的系数。
2. **可选"按身高归一化"**,系数从骨骼地标求出:
   - 推荐头骨高度。各约定的头骨名:`head neck upper` / DAZ `head` / `Bip001 Head` / ARP `head.x` / `M_Head` / `ValveBiped.Bip01_Head1`;
   - 例:按中位数,头骨高度 1.528 m × 12.5 ≈ 19.1 MMD 单位;
   - 不用网格 bbox:饰品让它多出 +0.04~+0.51 m(中位 +0.19);
   - 不用骨架范围:有定位骨;
   - 髋骨可作为备选地标,它对头饰免疫,但对腿长比例敏感。
3. **单位自检**:头骨高度不在约 [1.0, 2.5] m 时提示"可能是厘米/英寸或整体缩放的模型",并给出 ×0.01、×0.0254 等建议。本机语料里没有这类文件,这只是一道保护。
4. **落地选项**:按脚/脚趾骨所带权重顶点的最低点,或排除 `+/-` 道具网格后的最低点,把模型平移到 y=0。DAZ 系鞋底在 −0.05~−0.09,道具最低到 −0.25。
5. **同角色多套服装的一致性**:同一转换来源内头骨高度一致(Inase 10 套差 ±0.001),跨来源差 4–6%。如果要统一,应提供"匹配参考模型身高",而不是逐文件归一到固定值。

## 3. 骨骼命名约定

### 3.1 分布(147 个唯一文件)

| 顶层分类 | 细分 | 数量 | 代表 |
|---|---|---|---|
| xnalara_generic | xnalara_generic | 109 | lezisell 的 Rise of Eros 全系、SSPD077 系列、Naruto 包、DOAXVV Yukino、FF7 Tifa sweater、DOA Reika |
| daz_g8 | daz_g8 | 13 | Reika(`gantz/already/Reika`)、Tifa Gantz(混有 ARP 控制骨)、Eve Monokini、Fiona、Neurocircuit、Purifier (Inase) ×3 |
| daz_g8 | daz_g8+xnalara_generic | 4 | Super Moon (Misaki) ×2、Divine Grace (Lynn) ×2(DAZ 躯干 + 通用名的脸/头发骨) |
| other | prop(≤3 bones) | 5 | 武器、盾、法杖、刀(单骨 `root ground` / `root`) |
| other | auto_rig_pro | 4 | Valby、Reika-Gantz-2024 ×2、Wonder Woman Office CE(`c_pos`、`c_traj`、`*.x/.l/.r`) |
| other | 3dsmax_biped | 4 | rouffe (naked) 的 ASCII、Mikasa、Eve Cooling Suit ×2(`Bip001-Pelvis` 连字符写法) |
| other | lr_prefix | 3 | DR.ANJA、erika、Pilot(`Master` / `M_Hips` / `L_Thigh` / `*_ST` 辅助骨) |
| other | re_engine | 3 | Jill Gantz ×3(`l leg femur`、`COG`、`setProp …`) |
| other | unreal | 1 | (Gantz) Reika Shimohira(`thigh_l`、`calf_twist_01_l`,外加 `hip`/`pelvis`) |
| other | valve_biped | 1 | Diana Burnwood(`ValveBiped.Bip01_*`,夹杂 DAZ 的脚趾/腕骨名) |

### 3.2 观察

- **通用名模型的核心骨很全**:几乎都有 14/14 或 13/14 个核心骨。缺的通常是 `pelvis`,因为 lezisell 系用 `root hips`,并把原 `bip001 pelvis` 改成了 `unused bip001 pelvis`。
- **`unused*` 骨很普遍,且很多带权重**:99 个模型都有,来自 XPS 改名时给无映射的原骨加前缀(`unused bip001 thightwist_lt`、`unused bip001 l foretwist1`、`unused ac eyelid_bone_bl`、`unused trash 17`、`unused muscle_elbow_l`)。其中 36% 带权重,见第 0 节第 5 条。转换器必须先查权重再决定删除、合并到父骨还是隐藏。XNALaraMesh 也只是把它们移到隐藏层,并不删除。
- **判定 DAZ 要看躯干核心骨**:DAZ 的脚趾和面部名(`lSmallToe1_2`、`lNasolabial…`)也作为碎片出现在 ARP 骨架(#105)和 Valve 骨架(#128)里。所以分类器只在 `abdomenLower`、`chestUpper`、`lShldrBend`、`lThighBend`、`lShin` 等 18 个躯干核心骨中命中 ≥ 8 个时才判为 `daz_g8`;碎片只作为附加标签(见第 6 节表 B)。
- **映射器至少要覆盖这些约定**:XNALara 通用名、DAZ G3/G8、3ds Max Biped(含 `Bip001-` 连字符)、Auto-Rig Pro(`.x/.l/.r` 后缀)、Unreal。其余走手动 CSV 映射。仅这五类就覆盖了 147 个里的 135 个(含 5 个单骨道具)。

## 4. 格式意外与警告

1. **XPS 11.x 尾部"机器戳"**:共 103 个文件,其中 100 个 97 字节、2 个 73 字节、1 个 77 字节。
   - **位置**:最后一个网格之后,01 笔记的格式描述里没有;
   - **结构**:一串 .NET 字符串和 uint32——`"B"`、`" "`、4 个 uint32(IPv4 四段)、`"O"`、`"MM"`、十六进制 MAC 字符串、`"MMFF"`、MAC、`"FF"`、`" "`;73/77 字节的变体 IP 为 127.0.0.1,MAC 串较短;
   - **处理**:参考导入器从不检查 EOF,所以静默忽略;本读取器记一条警告后忽略;
   - **隐私**:XPS 11 保存的模型会带出作者的局域网 IP 和 MAC。本报告不列具体值;将来如果回写 XPS,不要复制这段尾部。
2. **权重未归一**:
   - 5 个模型(#1/#2 Eve Cooling 主体和 hair.ascii、#30/#31 Reika-Gantz-2024、#165 Valby)共 28 832 个顶点权重和 > 1.01,最高约 1.65。典型情况是前两个权重已经和为 1,又叠加了第三个;
   - 6 个模型有和 < 0.99 的顶点,Valby 还有 5 个全零权重顶点;
   - 结论:转换时必须重新归一化。01 笔记"XPS 权重已归一"的推断在本机不成立,问题文件多是 Blender 再导出的。
3. **超过 4 个影响**:7 个模型——Reika-Gantz-2024 最多 33、Valby 24、Wonder Woman Office 11、hair.ascii 9、Eve Cooling Suit 8、Jill pl2000 的 ASCII 8。PMX 的 BDEF4 需要截断到前 4 个再归一。3.x 文件还会存零权重槽。
4. **远离网格的骨骼**:见 2.3。无权重的远端定位骨应剔除或隐藏,不能参与身高计算。
5. **版本**:
   - 带头部的二进制只有两种版本:3.15(68 个,变长权重)和 2.15(64 个,固定 4 权重);
   - 无头部二进制 3 个,都带切线:DOA Reika、Jill、Asagi 的 `Generic_Item.mesh`;
   - ASCII 12 个,其中 hair.ascii 和 Jill pl2000 每顶点超过 4 个权重;
   - 没有 ≤ 2.12 的旧头部文件,没有触发布局回退,没有截断文件,没有非 UTF-8 字符串。
6. **Flags**:新格式文件只写了 flag 2/3/4/5,组合为 `2=1,3=0,4=3,5=4`(105 个)和 `2=1,3=0,4=2,5=4`(27 个)。
   - **推断(未验证)**:flag 3/4/5 的值很可能编码为"2×源通道 + 取反位"。3 表示 G 取反,即默认的 X+ Y− Z+(DirectX 风格);2 表示 G 不取反(OpenGL 风格)。27 个由 XPS 11.8 保存的 lezisell 模型声明了绿色不取反。参考导入器只取 `value % 2`,与这一推断一致。PMX 没有法线贴图,这只在烘焙时才相关。
   - 没有文件写 flag 0/1(背面剔除)、6(gloss)或 7(hasBoneDirections),所以 01 笔记中关于 hasBoneDirections 的缺口,本机样本无法验证。
7. **settings 条目**:
   - 全部是 `[(1, n, k), (2, 4, 4), (0, 256, 0)]`,hash 恒为 180,与 XNALaraMesh 的 mock 布局一致;
   - 20 个模型嵌入了默认姿势(5 760–31 718 字节、157–731 行);
   - 另有 18 个是"长度 0 但行数非 0"的空姿势项(如 `(1, 0, 243)`),无害。
8. **网格名**:
   - 108 个模型用 `+/-` 可选项,21 个用 `|` 分组;
   - 6 个有 nPart 分片。真实写法是 `24_body1nPart!_0_16_16`,分片号在 `nPart!` 前面,还可能带 `!wrong!` 注释;
   - 35 个模型的网格名带 Blender 重名后缀 `.00N`,而且粘在最后一个数值参数上(例如 `24_body.1_1.0_0_0.003` 的 bump2 会读成 0.003)。生成 PMX 材质名时应剥掉;
   - 也有第 6 段附加参数,如 `1_PC_10.0_0_0_BODY`。
9. **字符编码**:
   - 只有 2 个模型含非 ASCII 名:`Degradê Cinza 5C.png`,以及 `Rootì†Œì¼“`——后者是文件里本来就存着的双重编码乱码;
   - 本机 Blender 3.6 的 `XNALaraMesh-master` 把 `xps_const.py` 的 `ENCODING_READ` 改成了 `latin-1`(7 月 12 日修改)。这会把 UTF-8 的 `ê` 读成 `Ãª`,导致贴图找不到;
   - 本读取器按 01 笔记用 `utf-8-sig`,解码失败才回退 latin-1 并记警告。
10. **本读取器与参考实现的有意差异**:
    - settings 块以头部给出的长度为准,不论条目内容,读完都跳到块尾;
    - 7-bit 长度按 .NET 规则可以超过 2 字节;小于 16384 时与参考实现完全相同;
    - gloss 保留数值,不转 bool;
    - 参数 `0` 按 0 解析。参考实现因为 `if value:` 会把 `_0_` 当成缺省值 1;
    - 姿势缺省值为旋转 0 / 平移 0 / 缩放 1;参考实现全部用 1 补齐;
    - 名字主体含 `_` 时,取最后一个非数字段及其之前的部分作名字;
    - `.` 和 `|` 只对 `+/-` 可选项解释;
    - 只有版本推导出的布局失败时,才尝试其它布局,并且要求刚好读到文件尾才接受。本次触发 0 次。

## 5. `roe_xps_addon.py` 是什么

`C:\Users\haoni\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\roe_xps_addon.py`(2597 行,`bl_info`: "ROE XPS Tools" v1.1.17,作者 ripper_tpose,Blender 3.6)**不包含 XPS 读取器**:全文没有 `struct` 解析、没有 magic `323232`、没有 `.mesh.ascii` 解析。它是"Rise of Eros 角色 → XPS"的**导出流水线**,N 面板 ROE 页签:

1. **导入 FBX**(`ROE_OT_import_fbx`):`automatic_bone_orientation=True`;若导入后网格最大尺寸 < 0.5 就认为是旧版厘米级导出,自动整体 ×100 并应用缩放——即它把 XPS 输出的目标单位当作**米**。
2. **挂材质**(`ROE_OT_apply_materials`、`ROE_OT_repair_eyes` 等):眼球/睫毛/眉毛修复、按源材质名或贴图提示配 albedo,另有 HQ 材质与游戏眼球选项。
3. **导出 XPS `.mesh`**(`ROE_OT_export_xps`):烘焙眼球贴图 → head 按材质拆分 → 设渲染组(不透明仅漫反射 RG5、带 alpha RG7;有 lightmap/bump/specular 的 HQ 贴图用 24/25)→ 调 XNALaraMesh 的 `bpy.ops.xps_tools.export_model`(要求 XNALaraMesh 已启用),导出时临时补建 "XPS Shader" 节点组。
4. **修正 XPS 骨架方向**(`ROE_OT_fix_xps_armature`):若骨架骨骼 head 的 |y| 最大值 > 2×|z| 最大值且 ≥ 0.3("骨架躺平"),则临时解除子物体父子关系、骨架绕 X 轴 +90° 并应用旋转,再挂回,网格不动。

对本项目的意义:它是本机 XPS 样本的来源之一(ROE 模型经 FBX→Blender→XNALaraMesh 导出),其渲染组选择(5/7/24/25)和"米"单位假设可以和第 6 节的测量互相印证;它没有可复用的读取代码。

## 6. 原始测量数据(脚本生成)

<!-- BEGIN GENERATED: scripts/survey_xps_corpus.py -->

> 生成命令: `python scripts/survey_xps_corpus.py`  
> 扫描根目录: E:/day_work, E:/4090;排除: E:/code/model_tools;额外样本 6 个  
> 文件 170 个(唯一且解析成功 147,与前面某文件字节相同而未重复解析 23;失败 0,跳过 0);总耗时 123.1 s(含哈希与统计),纯解析 86.5 s

### A. 几何与尺度(XNA 坐标,+Y 向上;单位为文件原始单位)

| # | 文件 | 格式 | 版本 | 骨骼 | 网格 | 顶点 | 三角面 | 高度 Y | 默认可见高度 | 地面 minY | 宽 X | 深 Z | bbox min (x,y,z) | bbox max (x,y,z) | 髋骨 Y | 头骨 Y | 解析 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | day_work/2025money/wish/Cooing Suit(EVE)/#Stellar Blade - Eve (Cooling)/hair.ascii | ascii | no header | 354 | 2 | 44788 | 46248 | **1.265** |  | 0.453 | 0.433 | 0.384 | (-0.198, 0.453, -0.329) | (0.235, 1.718, 0.055) | 1.032 (root hips) | 1.542 (head neck upper) | 1.10 |
| 2 | day_work/2025money/wish/Cooing Suit(EVE)/#Stellar Blade - Eve (Cooling)/xps.xps | bin | 2.15 | 354 | 28 | 247488 | 340253 | **1.815** | 1.815 | -0.082 | 1.572 | 0.543 | (-0.786, -0.082, -0.435) | (0.786, 1.733, 0.108) | 1.032 (root hips) | 1.542 (head neck upper) | 2.47 |
| 3 | day_work/2025money/wish/cartilla (white rose)/xps.xps | bin | 3.15 | 133 | 9 | 38903 | 64684 | **1.789** | 1.789 | -0.002 | 1.406 | 0.546 | (-0.703, -0.002, -0.367) | (0.703, 1.788, 0.180) | 1.029 (root hips) | 1.538 (head neck upper) | 0.17 |
| 4 | day_work/2025money/wish/inase (arbiter)/xps.xps | bin | 3.15 | 117 | 8 | 56151 | 88295 | **1.722** | 1.722 | -0.000 | 1.430 | 0.866 | (-0.715, -0.000, -0.655) | (0.715, 1.722, 0.211) | 0.993 (root hips) | 1.544 (head neck upper) | 0.34 |
| 5 | day_work/2025money/wish/inase (blesser)/xps.xps | bin | 3.15 | 194 | 7 | 53923 | 82748 | **2.055** | 2.055 | -0.000 | 1.652 | 0.568 | (-0.937, -0.000, -0.275) | (0.715, 2.055, 0.293) | 0.993 (root hips) | 1.543 (head neck upper) | 0.24 |
| 6 | day_work/2025money/wish/inase (secret seeker)/inase/xps.xps | bin | 3.15 | 189 | 8 | 54007 | 76506 | **1.731** | 1.731 | -0.009 | 1.430 | 0.446 | (-0.715, -0.009, -0.274) | (0.715, 1.723, 0.171) | 0.993 (root hips) | 1.545 (head neck upper) | 0.23 |
| 7 | day_work/2025money/wish/inase (secret seeker)/weapon/xps.xps | bin | 3.15 | 1 | 1 | 2772 | 2916 | **0.877** | 0.877 | -0.000 | 0.876 | 0.082 | (-0.438, -0.000, -0.041) | (0.438, 0.877, 0.041) |  |  | 0.01 |
| 8 | day_work/2025money/wish/lynn - racing queen/xps.xps | bin | 3.15 | 209 | 21 | 93358 | 137093 | **1.723** | 1.706 | -0.008 | 1.476 | 0.285 | (-0.738, -0.008, -0.095) | (0.738, 1.715, 0.191) | 0.988 (root hips) | 1.528 (head neck upper) | 0.63 |
| 9 | day_work/work/Reika/rouffe (maiden flora)/normal pose.xps | bin | 3.15 | 194 | 10 | 58153 | 83343 | **1.988** | 1.988 | 0.004 | 1.252 | 0.563 | (-0.626, 0.004, -0.376) | (0.626, 1.992, 0.186) | 1.009 (root hips) | 1.537 (head neck upper) | 0.33 |
| 10 | day_work/work/Reika/rouffe (maiden flora)/xps.xps | bin | 3.15 | 194 | 10 | 62508 | 83486 | **1.988** | 1.988 | 0.004 | 1.399 | 0.563 | (-0.700, 0.004, -0.376) | (0.700, 1.992, 0.186) | 1.009 (root hips) | 1.537 (head neck upper) | 0.41 |
| 11 | day_work/work/gantz/already/(Gantz) Reika Shimohira/xps.xps | bin | 2.15 | 138 | 23 | 208724 | 249276 | **1.790** | 1.790 | -0.016 | 1.221 | 0.404 | (-0.611, -0.016, -0.187) | (0.611, 1.775, 0.217) | 1.030 (pelvis) | 1.559 (head) | 1.32 |
| 12 | day_work/work/gantz/already/DOA-Shimohira Reika/Generic_Item.mesh | bin | no header | 1096 | 17 | 45424 | 66056 | **1.665** | 1.665 | 0.011 | 1.211 | 0.297 | (-0.605, 0.011, -0.140) | (0.605, 1.676, 0.157) | 1.032 (root hips) | 1.488 (head neck upper) | 0.31 |
| 13 | day_work/work/gantz/already/DOA-Shimohira Reika/Generic_Item.mesh.ascii.mesh.ascii.mesh.ascii | ascii | no header | 1096 | 17 | 45424 | 66056 | **1.665** | 1.665 | 0.011 | 1.211 | 0.297 | (-0.605, 0.011, -0.140) | (0.605, 1.676, 0.157) | 1.032 (root hips) | 1.488 (head neck upper) | 1.10 |
| 14 | day_work/work/gantz/already/DOA-Shimohira Reika/xps.xps | bin | 2.15 | 1096 | 17 | 45424 | 66056 | **1.665** | 1.665 | 0.011 | 1.211 | 0.297 | (-0.605, 0.011, -0.140) | (0.605, 1.676, 0.157) | 1.032 (root hips) | 1.488 (head neck upper) | 0.16 |
| 15 | day_work/work/gantz/already/Luong as DOA5LR Naotora Ii - Gantz Outfit A/xps.xps | bin | 2.15 | 772 | 76 | 164738 | 232964 | **1.868** | 1.837 | -0.115 | 1.681 | 1.492 | (-0.841, -0.115, -0.367) | (0.841, 1.752, 1.125) | 0.973 (root hips) | 1.505 (head neck upper) | 1.17 |
| 16 | day_work/work/gantz/already/Reika/normal pose.xps | bin | 2.15 | 243 | 24 | 202623 | 229785 | **1.855** | 1.855 | -0.013 | 1.254 | 0.372 | (-0.627, -0.013, -0.212) | (0.627, 1.841, 0.159) | 1.075 (pelvis) | 1.642 (head) | 1.21 |
| 17 | day_work/work/gantz/already/Reika/xps.xps | bin | 2.15 | 243 | 24 | 202622 | 229785 | **1.862** | 1.862 | -0.020 | 1.671 | 0.372 | (-0.836, -0.020, -0.212) | (0.836, 1.841, 0.159) | 1.075 (pelvis) | 1.642 (head) | 1.43 |
| 18 | day_work/work/gantz/already/Tifa Gantz/normal pose.xps | bin | 2.15 | 263 | 35 | 253037 | 324197 | **1.689** | 1.689 | 0.001 | 1.076 | 0.357 | (-0.538, 0.001, -0.222) | (0.538, 1.690, 0.135) | 1.040 (pelvis) | 1.500 (head) | 1.50 |
| 19 | day_work/work/gantz/already/Tifa Gantz/xps.xps | bin | 2.15 | 263 | 35 | 253032 | 324195 | **1.698** | 1.698 | -0.007 | 1.502 | 0.357 | (-0.751, -0.007, -0.222) | (0.751, 1.690, 0.135) | 1.040 (pelvis) | 1.500 (head) | 1.72 |
| 20 | day_work/work/model/alana (archdemon baal)/xps.xps | bin | 3.15 | 173 | 9 | 46035 | 66358 | **1.585** | 1.585 | -0.001 | 1.300 | 0.512 | (-0.652, -0.001, -0.335) | (0.648, 1.584, 0.177) | 0.860 (root hips) | 1.391 (head neck upper) | 0.12 |
| 21 | day_work/work/model/ffvii_tifa_as_sweater_tights__dl__xps_by_sihsengiu_dj8wr7v/T-Pose.mesh | bin | 2.15 | 413 | 27 | 240342 | 322440 | **1.768** | 1.768 | -0.037 | 1.535 | 0.389 | (-0.768, -0.037, -0.200) | (0.768, 1.731, 0.189) | 0.982 (root hips) | 1.540 (head neck upper) | 1.97 |
| 22 | day_work/work/model/ffvii_tifa_as_sweater_tights__dl__xps_by_sihsengiu_dj8wr7v/xps.xps | bin | 2.15 | 413 | 27 | 240342 | 322440 | **1.742** | 1.742 | -0.011 | 1.186 | 0.389 | (-0.593, -0.011, -0.200) | (0.593, 1.731, 0.189) | 0.982 (root hips) | 1.540 (head neck upper) | 3.03 |
| 23 | day_work/work/model/misaki (knight of the holy shield)/misaki/xps.xps | bin | 3.15 | 159 | 10 | 52861 | 79263 | **1.802** | 1.802 | 0.033 | 1.432 | 0.503 | (-0.716, 0.033, -0.302) | (0.716, 1.835, 0.201) | 1.081 (root hips) | 1.634 (head neck upper) | 0.24 |
| 24 | day_work/work/model/misaki (knight of the holy shield)/shield/xps.xps | bin | 3.15 | 1 | 1 | 1643 | 1812 | **0.981** | 0.981 | -0.000 | 0.619 | 0.143 | (-0.309, -0.000, -0.140) | (0.309, 0.981, 0.003) |  |  | 0.00 |
| 25 | day_work/work/model/misaki (knight of the holy shield)/sword/xps.xps | bin | 3.15 | 1 | 1 | 697 | 968 | **1.557** | 1.557 | 0.000 | 0.285 | 0.063 | (-0.142, 0.000, -0.031) | (0.142, 1.557, 0.031) |  |  | 0.00 |
| 26 | day_work/work/model/rouffe (grand magician)/rouffe/xps.xps | bin | 3.15 | 209 | 7 | 49336 | 74456 | **1.707** | 1.707 | 0.002 | 1.400 | 0.340 | (-0.700, 0.002, -0.133) | (0.700, 1.709, 0.207) | 1.009 (root hips) | 1.537 (head neck upper) | 0.25 |
| 27 | day_work/work/model/rouffe (grand magician)/staff/xps.xps | bin | 3.15 | 1 | 1 | 4953 | 6753 | **0.239** | 0.239 | -0.073 | 1.565 | 0.334 | (-0.891, -0.073, -0.120) | (0.675, 0.166, 0.214) |  |  | 0.02 |
| 28 | day_work/work/other_model/[DR.ANJA] [BATHROBE]/xps.xps | bin | 2.15 | 414 | 19 | 235082 | 311489 | **1.878** | 1.878 | -0.094 | 1.047 | 0.414 | (-0.524, -0.094, -0.206) | (0.524, 1.783, 0.208) | 1.048 (hip) | 1.606 (M_Head) | 1.88 |
| 29 | day_work/work/other_model/_erika___succubus_misstress__by_lyyssadawn_dhnolct/xps.xps | bin | 2.15 | 399 | 17 | 231830 | 411726 | **1.711** | 1.711 | -0.004 | 0.959 | 0.332 | (-0.479, -0.004, -0.179) | (0.479, 1.706, 0.154) | 0.934 (hip) | 1.520 (M_Head) | 1.65 |
| 30 | day_work/work/reika花钱了/R2_Studio_REIKA_GANTZ/Blender/Reika-Gantz-2024.xps | bin | 3.15 | 435 | 16 | 55998 | 86968 | **1.790** | 1.790 | -0.016 | 1.221 | 0.402 | (-0.611, -0.016, -0.187) | (0.611, 1.775, 0.215) | 1.022 (root.x) | 1.559 (head.x) | 0.31 |
| 31 | day_work/work/reika花钱了/REIKA - GANTZ/Blender/Reika-Gantz-2024-C.xps | bin | 3.15 | 435 | 14 | 57784 | 90360 | **1.790** | 1.790 | -0.016 | 1.221 | 0.404 | (-0.611, -0.016, -0.187) | (0.611, 1.775, 0.217) | 1.022 (root.x) | 1.559 (head.x) | 0.36 |
| 32 | day_work/work/riseoferos/Super Moon (Misaki)- Rise Of Eros/normal pose.xps | bin | 2.15 | 192 | 18 | 157473 | 178621 | **1.867** | 1.867 | -0.063 | 1.157 | 0.408 | (-0.575, -0.063, -0.279) | (0.581, 1.804, 0.129) | 1.124 (pelvis) | 1.597 (head neck upper) | 1.12 |
| 33 | day_work/work/riseoferos/Super Moon (Misaki)- Rise Of Eros/xps.xps | bin | 2.15 | 192 | 18 | 157470 | 178621 | **1.872** | 1.872 | -0.069 | 1.533 | 0.408 | (-0.767, -0.069, -0.279) | (0.767, 1.804, 0.129) | 1.124 (pelvis) | 1.597 (head neck upper) | 0.99 |
| 34 | day_work/work/riseoferos/alana (aberrant corpse)/xps.xps | bin | 3.15 | 200 | 7 | 42585 | 62912 | **1.634** | 1.634 | -0.003 | 1.794 | 0.345 | (-0.897, -0.003, -0.115) | (0.897, 1.632, 0.230) | 0.860 (root hips) | 1.391 (head neck upper) | 0.18 |
| 35 | day_work/work/riseoferos/alana (archdemon baal)/xps.xps | 与 #20 字节相同 | | | | | | | | | | | | | | | |
| 36 | day_work/work/riseoferos/alana (blackwing ★ noir)/xps.xps | bin | 3.15 | 223 | 6 | 50231 | 71192 | **1.583** | 1.583 | 0.000 | 1.293 | 1.074 | (-0.646, 0.000, -0.882) | (0.646, 1.584, 0.192) | 0.860 (root hips) | 1.391 (head neck upper) | 0.25 |
| 37 | day_work/work/riseoferos/alana (flame falcon)/xps.xps | bin | 3.15 | 158 | 11 | 45508 | 67477 | **1.519** | 1.519 | 0.047 | 1.299 | 0.285 | (-0.649, 0.047, -0.087) | (0.649, 1.566, 0.199) | 0.863 (root hips) | 1.396 (head neck upper) | 0.22 |
| 38 | day_work/work/riseoferos/alana (midsummer)/xps.xps | bin | 3.15 | 152 | 9 | 48041 | 74550 | **1.796** | 1.796 | -0.248 | 1.294 | 0.298 | (-0.647, -0.248, -0.106) | (0.647, 1.548, 0.192) | 0.860 (root hips) | 1.391 (head neck upper) | 0.32 |
| 39 | day_work/work/riseoferos/alana (naked)/alana (naked)/xps.xps | bin | 3.15 | 217 | 7 | 39178 | 65140 | **1.544** | 1.544 | 0.004 | 1.294 | 0.278 | (-0.647, 0.004, -0.086) | (0.647, 1.548, 0.192) | 0.872 (root hips) | 1.393 (head neck upper) | 0.19 |
| 40 | day_work/work/riseoferos/alana (spirit detective)/xps.xps | bin | 3.15 | 214 | 6 | 51925 | 82287 | **1.585** | 1.585 | 0.007 | 1.294 | 0.420 | (-0.647, 0.007, -0.225) | (0.647, 1.592, 0.195) | 0.860 (root hips) | 1.391 (head neck upper) | 0.23 |
| 41 | day_work/work/riseoferos/alana (steelhare)/xps.xps | bin | 3.15 | 152 | 11 | 41674 | 61806 | **1.973** | 1.973 | -0.253 | 1.512 | 1.003 | (-0.866, -0.253, -0.500) | (0.646, 1.720, 0.502) | 0.860 (root hips) | 1.391 (head neck upper) | 0.23 |
| 42 | day_work/work/riseoferos/alana (tempting tidings)/xps.xps | bin | 3.15 | 168 | 10 | 39763 | 58908 | **1.658** | 1.658 | -0.038 | 1.297 | 0.477 | (-0.649, -0.038, -0.158) | (0.649, 1.620, 0.320) | 0.860 (root hips) | 1.391 (head neck upper) | 0.22 |
| 43 | day_work/work/riseoferos/cartilla (denim hotpants)/xps.xps | bin | 3.15 | 199 | 24 | 60610 | 99031 | **1.753** | 1.753 | -0.017 | 1.412 | 0.288 | (-0.706, -0.017, -0.106) | (0.706, 1.736, 0.182) | 1.009 (root hips) | 1.564 (head neck upper) | 0.40 |
| 44 | day_work/work/riseoferos/cartilla (holy slayer)/xps.xps | bin | 3.15 | 170 | 7 | 54586 | 85493 | **1.832** | 1.832 | 0.003 | 1.407 | 0.399 | (-0.703, 0.003, -0.191) | (0.703, 1.835, 0.207) | 1.004 (root hips) | 1.537 (head neck upper) | 0.23 |
| 45 | day_work/work/riseoferos/eileen (deep sea diva)/xps.xps | bin | 3.15 | 208 | 7 | 61729 | 87185 | **1.716** | 1.716 | 0.017 | 1.394 | 0.806 | (-0.697, 0.017, -0.546) | (0.697, 1.733, 0.260) | 0.994 (root hips) | 1.527 (head neck upper) | 0.37 |
| 46 | day_work/work/riseoferos/eileen (frostblossom)/xps.xps | bin | 3.15 | 191 | 17 | 61699 | 84166 | **1.737** | 1.737 | 0.000 | 1.406 | 0.703 | (-0.703, 0.000, -0.457) | (0.703, 1.737, 0.246) | 1.002 (root hips) | 1.539 (head neck upper) | 0.32 |
| 47 | day_work/work/riseoferos/inase (goddess of envy invidia)/xps.xps | bin | 3.15 | 202 | 9 | 56150 | 85246 | **1.760** | 1.760 | -0.002 | 1.904 | 0.339 | (-1.189, -0.002, -0.169) | (0.715, 1.758, 0.170) | 0.993 (root hips) | 1.543 (head neck upper) | 0.41 |
| 48 | day_work/work/riseoferos/inase (naked)/inase (naked)/xps.xps | bin | 3.15 | 202 | 11 | 42295 | 70390 | **1.718** | 1.718 | 0.004 | 1.430 | 0.258 | (-0.715, 0.004, -0.097) | (0.715, 1.722, 0.161) | 0.993 (root hips) | 1.545 (head neck upper) | 0.20 |
| 49 | day_work/work/riseoferos/inase (purifier)/xps.xps | bin | 3.15 | 109 | 8 | 50124 | 79198 | **1.749** | 1.749 | -0.027 | 1.430 | 0.259 | (-0.715, -0.027, -0.097) | (0.715, 1.722, 0.161) | 0.993 (root hips) | 1.544 (head neck upper) | 0.41 |
| 50 | day_work/work/riseoferos/lynn (flight attendant)/xps.xps | bin | 3.15 | 209 | 21 | 86857 | 147448 | **1.727** | 1.727 | 0.003 | 1.471 | 0.260 | (-0.736, 0.003, -0.088) | (0.736, 1.730, 0.172) | 0.988 (root hips) | 1.528 (head neck upper) | 0.48 |
| 51 | day_work/work/riseoferos/lynn (furious pirate)/xps.xps | bin | 3.15 | 173 | 8 | 50466 | 76633 | **1.865** | 1.865 | 0.000 | 1.469 | 1.081 | (-0.734, 0.000, -0.749) | (0.734, 1.865, 0.332) | 0.988 (root hips) | 1.528 (head neck upper) | 0.29 |
| 52 | day_work/work/riseoferos/misaki 02/xps.xps | bin | 3.15 | 149 | 10 | 32921 | 52434 | **1.810** | 1.810 | -0.040 | 1.422 | 0.387 | (-0.711, -0.040, -0.228) | (0.711, 1.770, 0.159) | 1.048 (root hips) | 1.595 (head neck upper) | 0.19 |
| 53 | day_work/work/riseoferos/pc_a02_ld/xps.xps | bin | 3.15 | 101 | 10 | 17035 | 23544 | **1.736** | 1.736 | 0.001 | 1.444 | 0.911 | (-0.722, 0.001, -0.179) | (0.722, 1.737, 0.731) | 1.000 (root hips) | 1.556 (head neck upper) | 0.06 |
| 54 | day_work/work/riseoferos/phoenix (naked)/phoenix (naked)/xps.xps | bin | 3.15 | 191 | 7 | 35045 | 59706 | **1.542** | 1.542 | 0.004 | 1.241 | 0.225 | (-0.620, 0.004, -0.076) | (0.620, 1.546, 0.148) | 0.866 (root hips) | 1.388 (head neck upper) | 0.14 |
| 55 | day_work/work/riseoferos/rouffe (empress of snows)/xps.xps | bin | 3.15 | 169 | 10 | 47732 | 68879 | **1.798** | 1.798 | 0.001 | 1.396 | 0.672 | (-0.698, 0.001, -0.320) | (0.698, 1.799, 0.352) | 1.009 (root hips) | 1.537 (head neck upper) | 0.26 |
| 56 | day_work/work/riseoferos/rouffe (enchanting coach)/xps.xps | bin | 3.15 | 217 | 19 | 57466 | 94286 | **1.713** | 1.713 | -0.004 | 1.400 | 0.279 | (-0.700, -0.004, -0.108) | (0.700, 1.709, 0.171) | 0.993 (root hips) | 1.541 (head neck upper) | 0.37 |
| 57 | day_work/work/riseoferos/rouffe (glistening grace)/xps.xps | bin | 3.15 | 166 | 10 | 38824 | 61122 | **1.765** | 1.765 | -0.029 | 1.402 | 0.582 | (-0.701, -0.029, -0.277) | (0.701, 1.736, 0.305) | 1.009 (root hips) | 1.537 (head neck upper) | 0.21 |
| 58 | day_work/work/riseoferos/rouffe (goddess of love aphrodite)/xps.xps | bin | 3.15 | 234 | 15 | 67014 | 90177 | **1.801** | 1.801 | 0.000 | 2.325 | 0.444 | (-1.163, 0.000, -0.263) | (1.163, 1.801, 0.180) | 1.009 (root hips) | 1.537 (head neck upper) | 0.37 |
| 59 | day_work/work/riseoferos/rouffe (inked gold)/xps.xps | bin | 3.15 | 144 | 6 | 45552 | 75241 | **1.712** | 1.712 | -0.002 | 1.400 | 0.310 | (-0.700, -0.002, -0.108) | (0.700, 1.709, 0.203) | 1.009 (root hips) | 1.537 (head neck upper) | 0.20 |
| 60 | day_work/work/riseoferos/rouffe (maiden flora)/xps.xps | 与 #10 字节相同 | | | | | | | | | | | | | | | |
| 61 | day_work/work/riseoferos/rouffe (naked)/rouffe (naked)/rouffe.mesh.ascii | ascii | no header | 228 | 7 | 40040 | 66825 | **1.706** | 1.706 | 0.004 | 1.400 | 0.278 | (-0.700, 0.004, -0.108) | (0.700, 1.709, 0.171) | 0.993 (Bip001 Pelvis) | 1.541 (Bip001 Head) | 1.05 |
| 62 | day_work/work/riseoferos/rouffe (naked)/rouffe (naked)/xps.xps | bin | 3.15 | 217 | 7 | 40040 | 66825 | **1.706** | 1.706 | 0.004 | 1.400 | 0.278 | (-0.700, 0.004, -0.108) | (0.700, 1.709, 0.171) | 0.993 (root hips) | 1.541 (head neck upper) | 0.24 |
| 63 | day_work/work/riseoferos/rouffe (obsidian armor)/xps.xps | bin | 3.15 | 154 | 10 | 50542 | 81022 | **1.731** | 1.731 | -0.000 | 1.396 | 0.709 | (-0.698, -0.000, -0.532) | (0.698, 1.730, 0.177) | 1.009 (root hips) | 1.537 (head neck upper) | 0.25 |
| 64 | day_work/work/riseoferos/rouffe (pasionate gift)/xps.xps | bin | 3.15 | 153 | 8 | 46632 | 74335 | **1.765** | 1.765 | -0.000 | 1.396 | 0.365 | (-0.698, -0.000, -0.164) | (0.698, 1.765, 0.202) | 1.009 (root hips) | 1.537 (head neck upper) | 0.31 |
| 65 | day_work/work/riseoferos/rouffe (sash)/xps.xps | bin | 3.15 | 175 | 11 | 45370 | 71565 | **1.742** | 1.742 | -0.030 | 1.402 | 0.594 | (-0.701, -0.030, -0.287) | (0.701, 1.712, 0.307) | 1.009 (root hips) | 1.537 (head neck upper) | 0.21 |
| 66 | day_work/work/riseoferos/rouffe (tigerstripe)/xps.xps | bin | 3.15 | 195 | 11 | 47753 | 72430 | **1.829** | 1.829 | -0.120 | 2.689 | 0.348 | (-1.330, -0.120, -0.171) | (1.359, 1.709, 0.176) | 1.009 (root hips) | 1.537 (head neck upper) | 0.26 |
| 67 | day_work/work/riseoferos/rouffe (virgin killer)/xps.xps | bin | 3.15 | 229 | 15 | 62523 | 104230 | **1.714** | 1.714 | 0.002 | 1.400 | 0.353 | (-0.700, 0.002, -0.113) | (0.700, 1.717, 0.240) | 0.993 (root hips) | 1.541 (head neck upper) | 0.26 |
| 68 | day_work/work/riseoferos2/cartilla (pure white love song)_pmx/normal pose.xps | bin | 3.15 | 150 | 7 | 35145 | 56894 | **1.940** | 1.940 | 0.003 | 1.078 | 0.549 | (-0.539, 0.003, -0.248) | (0.539, 1.943, 0.301) | 1.029 (root hips) | 1.538 (head neck upper) | 0.20 |
| 69 | day_work/work/riseoferos2/cartilla (pure white love song)_pmx/xps.xps | bin | 3.15 | 150 | 7 | 35145 | 56894 | **1.940** | 1.940 | 0.003 | 1.406 | 0.549 | (-0.703, 0.003, -0.248) | (0.703, 1.943, 0.301) | 1.029 (root hips) | 1.538 (head neck upper) | 0.15 |
| 70 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps-A-pose.xps | bin | 3.15 | 144 | 9 | 42245 | 61735 | **1.737** | 1.737 | -0.001 | 1.078 | 0.284 | (-0.539, -0.001, -0.110) | (0.539, 1.736, 0.174) | 1.004 (root hips) | 1.537 (head neck upper) | 0.20 |
| 71 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps.xps | bin | 3.15 | 144 | 11 | 46192 | 65378 | **1.737** | 1.737 | -0.001 | 1.510 | 0.592 | (-0.770, -0.001, -0.191) | (0.741, 1.736, 0.401) | 1.004 (root hips) | 1.537 (head neck upper) | 0.20 |
| 72 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx3/normal pose.xps | bin | 3.15 | 144 | 9 | 42245 | 61735 | **1.737** | 1.737 | -0.001 | 1.078 | 0.284 | (-0.539, -0.001, -0.110) | (0.539, 1.736, 0.174) | 1.004 (root hips) | 1.537 (head neck upper) | 0.22 |
| 73 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx3/xps.xps | 与 #71 字节相同 | | | | | | | | | | | | | | | |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | bin | 3.15 | 144 | 9 | 42245 | 61735 | **1.737** | 1.737 | -0.001 | 1.078 | 0.284 | (-0.539, -0.001, -0.110) | (0.539, 1.736, 0.174) | 1.004 (root hips) | 1.537 (head neck upper) | 0.24 |
| 75 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/xps.xps | 与 #71 字节相同 | | | | | | | | | | | | | | | |
| 76 | day_work/work/riseoferos2/inase (arbiter)_pmx/normal pose.xps | bin | 3.15 | 117 | 6 | 53730 | 85007 | **1.722** | 1.722 | -0.000 | 1.073 | 0.329 | (-0.530, -0.000, -0.098) | (0.542, 1.722, 0.231) | 0.993 (root hips) | 1.544 (head neck upper) | 0.23 |
| 77 | day_work/work/riseoferos2/inase (arbiter)_pmx/xps.xps | 与 #4 字节相同 | | | | | | | | | | | | | | | |
| 78 | day_work/work/riseoferos2/inase (auditioner)/xps.xps | bin | 3.15 | 135 | 7 | 41101 | 65273 | **1.724** | 1.724 | -0.002 | 2.161 | 3.589 | (-1.446, -0.002, -1.795) | (0.715, 1.722, 1.795) | 0.993 (root hips) | 1.544 (head neck upper) | 0.22 |
| 79 | day_work/work/riseoferos2/inase (heart stealer)/xps.xps | bin | 3.15 | 198 | 10 | 50628 | 80269 | **1.750** | 1.750 | -0.027 | 1.430 | 0.605 | (-0.715, -0.027, -0.421) | (0.715, 1.723, 0.185) | 0.993 (root hips) | 1.545 (head neck upper) | 0.29 |
| 80 | day_work/work/riseoferos2/inase (heart stealer)/inase (naked)/xps.xps | 与 #48 字节相同 | | | | | | | | | | | | | | | |
| 81 | day_work/work/riseoferos2/inase (nightcrawler)_pmx/xps.xps | bin | 3.15 | 142 | 7 | 41430 | 66095 | **1.722** | 1.722 | -0.000 | 1.462 | 0.405 | (-0.731, -0.000, -0.236) | (0.731, 1.722, 0.170) | 0.993 (root hips) | 1.544 (head neck upper) | 0.18 |
| 82 | day_work/work/xps/Eve (Wave Oblique Monokini)- Stellar Blade/normal pose.xps | bin | 2.15 | 241 | 16 | 219016 | 239580 | **1.850** | 1.850 | -0.055 | 1.214 | 0.579 | (-0.607, -0.055, -0.437) | (0.607, 1.796, 0.142) | 1.099 (pelvis) | 1.608 (head) | 1.63 |
| 83 | day_work/work/xps/Eve (Wave Oblique Monokini)- Stellar Blade/xps.xps | bin | 2.15 | 241 | 16 | 219016 | 239580 | **1.857** | 1.857 | -0.062 | 1.616 | 0.579 | (-0.808, -0.062, -0.437) | (0.808, 1.796, 0.142) | 1.099 (pelvis) | 1.608 (head) | 1.28 |
| 84 | day_work/work11(model)/AoTWA - Mikasa Ackermann/xps.xps | bin | 2.15 | 105 | 9 | 26864 | 27397 | **1.698** | 1.698 | 0.003 | 1.482 | 1.508 | (-0.741, 0.003, -0.610) | (0.741, 1.701, 0.898) | 0.941 (Bip001 Pelvis) | 1.483 (Bip001 Head) | 0.06 |
| 85 | day_work/work11(model)/Cooling Suit crazy/Stellar Blade - Eve (Cooling Suit).xps | bin | 3.15 | 579 | 1 | 35219 | 59996 | **1.516** | 1.516 | 0.000 | 0.798 | 0.287 | (-0.399, 0.000, -0.138) | (0.399, 1.516, 0.149) | 0.989 (Bip001-Pelvis) | 1.518 (Bip001-Head) | 0.25 |
| 86 | day_work/work11(model)/Eve - Cooling Suit/Eve - Cooling Suit.xps | bin | 3.15 | 320 | 21 | 134837 | 179106 | **1.736** | 1.736 | 0.000 | 0.517 | 0.798 | (-0.368, 0.000, -0.399) | (0.149, 1.736, 0.399) | 0.989 (Bip001-Pelvis) | 1.518 (Bip001-Head) | 1.39 |
| 87 | day_work/work11(model)/keleira (vespermas star)/xps.xps | bin | 3.15 | 196 | 9 | 51792 | 74845 | **1.767** | 1.767 | -0.001 | 1.466 | 0.676 | (-0.733, -0.001, -0.469) | (0.733, 1.766, 0.207) | 0.988 (root hips) | 1.530 (head neck upper) | 0.26 |
| 88 | day_work/work2/DOAXVV Yukino - Shimmering Elf Dress/Generic_Item.mesh.ascii | ascii | no header | 523 | 30 | 87650 | 129918 | **1.662** | 1.662 | 0.001 | 1.137 | 1.165 | (-0.568, 0.001, -0.297) | (0.568, 1.664, 0.869) | 0.959 (root hips) | 1.468 (head neck upper) | 1.90 |
| 89 | day_work/work2/DOAXVV Yukino - Shimmering Elf Dress/xps.xps | bin | 2.15 | 523 | 30 | 87648 | 129918 | **1.662** | 1.662 | 0.001 | 1.137 | 1.165 | (-0.568, 0.001, -0.297) | (0.568, 1.664, 0.869) | 0.959 (root hips) | 1.468 (head neck upper) | 0.53 |
| 90 | day_work/work2/Fiona Vindictus Defying Fate/normal pose.xps | bin | 2.15 | 275 | 20 | 233332 | 280386 | **1.867** | 1.867 | -0.063 | 1.207 | 0.461 | (-0.604, -0.063, -0.281) | (0.604, 1.805, 0.180) | 1.093 (pelvis) | 1.618 (head) | 1.59 |
| 91 | day_work/work2/Fiona Vindictus Defying Fate/xps.xps | bin | 2.15 | 275 | 20 | 233332 | 280386 | **1.873** | 1.873 | -0.069 | 1.617 | 0.461 | (-0.809, -0.069, -0.281) | (0.809, 1.805, 0.180) | 1.093 (pelvis) | 1.618 (head) | 1.87 |
| 92 | day_work/work2/Neurocircuit Bondage/normal pose.xps | bin | 2.15 | 239 | 17 | 247628 | 277227 | **1.871** | 1.871 | -0.073 | 1.203 | 0.529 | (-0.601, -0.073, -0.390) | (0.601, 1.798, 0.139) | 1.121 (pelvis) | 1.619 (head) | 1.83 |
| 93 | day_work/work2/Neurocircuit Bondage/xps.xps | bin | 2.15 | 239 | 17 | 247628 | 277227 | **1.878** | 1.878 | -0.080 | 1.628 | 0.529 | (-0.814, -0.080, -0.390) | (0.814, 1.798, 0.139) | 1.121 (pelvis) | 1.619 (head) | 1.41 |
| 94 | day_work/work3/Reika_Tropical_Bikini_by_SSPD077/Reika_Tropical_Bikini_by_SSPD077/Generic_Item.mesh.ascii | ascii | no header | 339 | 18 | 54869 | 83271 | **1.632** | 1.632 | 0.002 | 1.178 | 2.186 | (-0.589, 0.002, -1.105) | (0.589, 1.633, 1.081) | 0.950 (root hips) | 1.394 (head neck upper) | 1.56 |
| 95 | day_work/work3/Reika_Tropical_Bikini_by_SSPD077/Reika_Tropical_Bikini_by_SSPD077/xps.xps | bin | 2.15 | 339 | 18 | 54869 | 83271 | **1.632** | 1.632 | 0.002 | 1.178 | 2.186 | (-0.589, 0.002, -1.105) | (0.589, 1.633, 1.081) | 0.950 (root hips) | 1.394 (head neck upper) | 0.47 |
| 96 | day_work/work3/Rosa nude (Bayonetta)/xps.xps | bin | 2.15 | 294 | 20 | 30497 | 46498 | **1.836** | 1.836 | -0.001 | 1.633 | 0.296 | (-0.817, -0.001, -0.143) | (0.817, 1.835, 0.153) | 1.138 (root hips) | 1.586 (head neck upper) | 0.18 |
| 97 | day_work/work3/xps/Divine Grace (Lynn)/normal pose.xps | bin | 2.15 | 250 | 18 | 181115 | 211863 | **1.990** | 1.990 | -0.051 | 1.202 | 0.577 | (-0.601, -0.051, -0.416) | (0.601, 1.939, 0.160) | 1.111 (pelvis) | 1.633 (head) | 1.17 |
| 98 | day_work/work3/xps/Divine Grace (Lynn)/xps.xps | bin | 2.15 | 250 | 18 | 181113 | 211863 | **1.999** | 1.999 | -0.059 | 1.631 | 0.577 | (-0.815, -0.059, -0.416) | (0.816, 1.939, 0.160) | 1.111 (pelvis) | 1.633 (head) | 1.23 |
| 99 | day_work/work4/#Tifa Maiden/xps.xps | bin | 2.15 | 331 | 31 | 277931 | 472265 | **1.725** | 1.725 | 0.023 | 0.988 | 0.559 | (-0.494, 0.023, -0.381) | (0.494, 1.749, 0.179) | 1.077 (root hips) | 1.561 (head neck upper) | 2.26 |
| 100 | day_work/work4/Jill Gantz/Generic_Item.mesh | bin | no header | 438 | 8 | 74316 | 87970 | **1.712** | 1.712 | 0.004 | 0.826 | 0.541 | (-0.414, 0.004, -0.143) | (0.412, 1.716, 0.398) | 1.012 (hips) | 1.556 (head) | 0.62 |
| 101 | day_work/work4/Jill Gantz/pl2000.meshout.mesh.ascii | ascii | no header | 191 | 25 | 31845 | 44200 | **1.447** | 1.447 | -0.001 | 0.826 | 0.541 | (-0.414, -0.001, -0.147) | (0.412, 1.446, 0.394) | 1.007 (hips) | 1.553 (head) | 1.07 |
| 102 | day_work/work4/Jill Gantz/xps.xps | bin | 2.15 | 1316 | 9 | 119058 | 129779 | **1.731** | 1.731 | 0.009 | 0.826 | 0.541 | (-0.414, 0.009, -0.158) | (0.412, 1.740, 0.383) | 1.019 (hips) | 1.565 (head) | 0.76 |
| 103 | day_work/work4/One Punch Man Fubuki by Animanpower/1 T POSE xps.xps | bin | 2.15 | 218 | 23 | 78643 | 130544 | **2.129** | 2.129 | -0.022 | 1.690 | 0.586 | (-0.845, -0.022, -0.334) | (0.845, 2.107, 0.253) | 1.406 (root hips) | 1.880 (head neck upper) | 0.53 |
| 104 | day_work/work4/One Punch Man Fubuki by Animanpower/xps.xps | bin | 2.15 | 218 | 23 | 78643 | 130544 | **2.095** | 2.095 | 0.012 | 1.307 | 0.586 | (-0.654, 0.012, -0.334) | (0.654, 2.107, 0.253) | 1.406 (root hips) | 1.880 (head neck upper) | 0.35 |
| 105 | day_work/work4/Wonder Woman Movie by Mokujin Hornywood Office CE by Animanpower/xps.xps | bin | 3.15 | 755 | 35 | 175756 | 267630 | **1.879** | 1.876 | -0.006 | 1.157 | 0.349 | (-0.578, -0.006, -0.209) | (0.578, 1.872, 0.141) | 1.122 (root.x) | 1.654 (head.x) | 1.55 |
| 106 | day_work/work5/Lisa gantz hairstyle 2/xps.xps | bin | 2.15 | 423 | 14 | 40595 | 58722 | **1.658** | 1.658 | 0.011 | 1.211 | 0.301 | (-0.605, 0.011, -0.140) | (0.605, 1.669, 0.160) | 0.988 (root hips) | 1.482 (head neck upper) | 0.21 |
| 107 | day_work/work5/Pilot/xps.xps | bin | 2.15 | 630 | 23 | 433413 | 245063 | **1.724** | 1.724 | -0.053 | 1.071 | 0.296 | (-0.534, -0.053, -0.122) | (0.537, 1.671, 0.174) | 0.951 (hip) | 1.483 (M_Head) | 3.59 |
| 108 | day_work/work5/Reika_Shimohira_by_SSPD077/Reika_Shimohira_by_SSPD077/Generic_Item.mesh.ascii | ascii | no header | 339 | 32 | 60779 | 91991 | **1.648** | 1.648 | -0.015 | 1.178 | 2.186 | (-0.589, -0.015, -1.105) | (0.589, 1.633, 1.081) | 0.950 (root hips) | 1.394 (head neck upper) | 1.39 |
| 109 | day_work/work5/Reika_Shimohira_by_SSPD077/Reika_Shimohira_by_SSPD077/Generic_Item.mesh.tui.xps | bin | 3.15 | 339 | 32 | 60744 | 91991 | **1.672** | 1.672 | -0.038 | 1.178 | 2.186 | (-0.589, -0.038, -1.105) | (0.589, 1.633, 1.081) | 0.950 (root hips) | 1.394 (head neck upper) | 0.36 |
| 110 | day_work/work5/Reika_Shimohira_by_SSPD077/Reika_Shimohira_by_SSPD077/xps.xps | bin | 2.15 | 339 | 32 | 60779 | 91991 | **1.648** | 1.648 | -0.015 | 1.178 | 2.186 | (-0.589, -0.015, -1.105) | (0.589, 1.633, 1.081) | 0.950 (root hips) | 1.394 (head neck upper) | 0.44 |
| 111 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/1.mesh.ascii | ascii | no header | 350 | 49 | 35874 | 57624 | **1.674** | 1.674 | 0.000 | 1.202 | 1.079 | (-0.601, 0.000, -0.173) | (0.601, 1.675, 0.906) | 0.989 (root hips) | 1.495 (head neck upper) | 1.00 |
| 112 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/Generic_Item.mesh | bin | no header | 350 | 51 | 37505 | 59536 | **1.674** | 1.674 | 0.000 | 1.202 | 1.079 | (-0.601, 0.000, -0.173) | (0.601, 1.675, 0.906) | 0.989 (root hips) | 1.495 (head neck upper) | 0.26 |
| 113 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/Generic_Item.mesh.ascii | ascii | no header | 350 | 49 | 35875 | 57630 | **1.674** | 1.674 | 0.000 | 1.202 | 1.079 | (-0.601, 0.000, -0.173) | (0.601, 1.675, 0.906) | 0.989 (root hips) | 1.495 (head neck upper) | 0.73 |
| 114 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/finalasagi.mesh.ascii | ascii | no header | 350 | 51 | 37509 | 59540 | **1.674** | 1.674 | 0.000 | 1.202 | 1.079 | (-0.601, 0.000, -0.173) | (0.601, 1.675, 0.906) | 0.989 (root hips) | 1.495 (head neck upper) | 0.97 |
| 115 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/finalasagi.xps | bin | 3.15 | 350 | 51 | 37506 | 59530 | **1.709** | 1.709 | -0.034 | 1.202 | 1.079 | (-0.601, -0.034, -0.173) | (0.601, 1.675, 0.906) | 0.989 (root hips) | 1.495 (head neck upper) | 0.20 |
| 116 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/xps.xps | bin | 2.15 | 350 | 49 | 35875 | 57630 | **1.674** | 1.674 | 0.000 | 1.202 | 1.079 | (-0.601, 0.000, -0.173) | (0.601, 1.675, 0.906) | 0.989 (root hips) | 1.495 (head neck upper) | 0.19 |
| 117 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Asagi_Igawa_by_SSPD077/Generic_Item.mesh.ascii | ascii | no header | 351 | 48 | 34206 | 53856 | **1.679** | 1.679 | -0.005 | 1.202 | 1.079 | (-0.601, -0.005, -0.160) | (0.601, 1.675, 0.919) | 0.989 (root hips) | 1.495 (head neck upper) | 0.82 |
| 118 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Asagi_Igawa_by_SSPD077/xps.xps | bin | 2.15 | 351 | 48 | 34206 | 53856 | **1.679** | 1.679 | -0.005 | 1.202 | 1.079 | (-0.601, -0.005, -0.160) | (0.601, 1.675, 0.919) | 0.989 (root hips) | 1.495 (head neck upper) | 0.19 |
| 119 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Hell_Knight_Ingrid_by_SSPD077/Hell_Knight_Ingrid_With_Cape_by_SSPD077/xps.xps | bin | 2.15 | 530 | 34 | 27925 | 43822 | **1.708** | 1.708 | -0.014 | 1.241 | 1.410 | (-0.628, -0.014, -0.327) | (0.613, 1.694, 1.083) | 1.000 (root hips) | 1.504 (head neck upper) | 0.16 |
| 120 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Hell_Knight_Ingrid_by_SSPD077/Hell_Knight_Ingrid_by_SSPD077/xps.xps | bin | 2.15 | 467 | 31 | 24828 | 38832 | **1.708** | 1.708 | -0.014 | 1.241 | 1.359 | (-0.628, -0.014, -0.276) | (0.613, 1.694, 1.083) | 1.000 (root hips) | 1.504 (head neck upper) | 0.11 |
| 121 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Mask_Oboro_Kokawa_by_SSPD077/xps.xps | bin | 2.15 | 157 | 22 | 26486 | 43023 | **1.690** | 1.690 | -0.005 | 1.202 | 0.316 | (-0.601, -0.005, -0.134) | (0.601, 1.686, 0.182) | 0.989 (root hips) | 1.492 (head neck upper) | 0.14 |
| 122 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Murasaki_Yatsu_by_SSPD077/xps.xps | bin | 2.15 | 470 | 37 | 27566 | 43959 | **1.669** | 1.669 | -0.005 | 1.309 | 2.054 | (-0.708, -0.005, -0.327) | (0.601, 1.665, 1.727) | 0.989 (root hips) | 1.495 (head neck upper) | 0.19 |
| 123 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Oboro_by_SSPD077/Generic_Item.mesh.ascii | ascii | no header | 267 | 30 | 27023 | 42926 | **1.682** | 1.682 | -0.005 | 1.440 | 0.461 | (-0.714, -0.005, -0.279) | (0.726, 1.677, 0.182) | 0.989 (root hips) | 1.492 (head neck upper) | 0.64 |
| 124 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Oboro_by_SSPD077/xps.xps | bin | 2.15 | 267 | 30 | 27023 | 42926 | **1.682** | 1.682 | -0.005 | 1.440 | 0.461 | (-0.714, -0.005, -0.279) | (0.726, 1.677, 0.182) | 0.989 (root hips) | 1.492 (head neck upper) | 0.15 |
| 125 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Rinko_Akiyama_bu_SSPD077/Rinko_Akiyama_Longhair_by_SSPD077/xps.xps | bin | 2.15 | 315 | 33 | 32830 | 53442 | **1.674** | 1.674 | -0.005 | 1.202 | 1.909 | (-0.601, -0.005, -0.800) | (0.601, 1.670, 1.110) | 0.989 (root hips) | 1.494 (head neck upper) | 0.14 |
| 126 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Rinko_Akiyama_bu_SSPD077/Rinko_Akiyama_Ponytail_by_SSPD077/xps.xps | bin | 2.15 | 209 | 31 | 35274 | 57696 | **1.757** | 1.757 | -0.005 | 1.202 | 1.909 | (-0.601, -0.005, -0.800) | (0.601, 1.752, 1.110) | 0.989 (root hips) | 1.494 (head neck upper) | 0.19 |
| 127 | day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Sakura_Igawa_by_SSPD077/xps.xps | bin | 2.15 | 191 | 44 | 50853 | 77053 | **1.678** | 1.678 | -0.005 | 1.202 | 0.804 | (-0.601, -0.005, -0.621) | (0.601, 1.673, 0.182) | 0.989 (root hips) | 1.495 (head neck upper) | 0.28 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | bin | 2.15 | 145 | 77 | 112427 | 187580 | **1.675** | 1.675 | -0.083 | 1.575 | 0.371 | (-0.788, -0.083, -0.149) | (0.788, 1.592, 0.222) | 1.020 (hip) | 1.553 (ValveBiped.Bip01_Head1) | 0.79 |
| 129 | day_work/work6/Wonder Woman Movie by Mokujin Hornywood Default by Animanpower/xps.xps | bin | 2.15 | 559 | 32 | 142513 | 223250 | **1.971** | 1.971 | -0.056 | 1.255 | 0.363 | (-0.628, -0.056, -0.212) | (0.628, 1.914, 0.151) | 1.019 (root hips) | 1.689 (head neck upper) | 0.84 |
| 130 | day_work/work6/inase (secret seeker)/inase/xps.xps | 与 #6 字节相同 | | | | | | | | | | | | | | | |
| 131 | day_work/work6/inase (secret seeker)/weapon/xps.xps | 与 #7 字节相同 | | | | | | | | | | | | | | | |
| 132 | day_work/work7/Gantz Reika suit V2/Knife.mesh | bin | 2.15 | 1 | 1 | 9220 | 17110 | **1.241** | 1.241 | -0.017 | 0.108 | 0.108 | (-0.943, -0.017, -0.054) | (-0.835, 1.224, 0.054) |  |  | 0.04 |
| 133 | day_work/work7/Gantz Reika suit V2/xps.xps | bin | 2.15 | 245 | 19 | 113463 | 207394 | **1.676** | 1.676 | -0.090 | 1.093 | 1.241 | (-0.546, -0.090, -0.211) | (0.546, 1.586, 1.030) | 0.958 (root hips) | 1.535 (head neck upper) | 0.58 |
| 134 | day_work/work7/inase (secret seeker)/inase/xps.xps | 与 #6 字节相同 | | | | | | | | | | | | | | | |
| 135 | day_work/work7/inase (secret seeker)/weapon/xps.xps | 与 #7 字节相同 | | | | | | | | | | | | | | | |
| 136 | day_work/work7/lynn (deathblossom)/xps.xps | bin | 3.15 | 222 | 10 | 43392 | 66196 | **1.701** | 1.701 | -0.003 | 1.471 | 0.311 | (-0.736, -0.003, -0.130) | (0.736, 1.698, 0.182) | 0.988 (root hips) | 1.528 (head neck upper) | 0.39 |
| 137 | day_work/work7/misaki (mooncaller)/xps.xps | bin | 3.15 | 215 | 8 | 42821 | 64909 | **1.865** | 1.865 | -0.068 | 1.427 | 0.564 | (-0.713, -0.068, -0.378) | (0.713, 1.797, 0.186) | 1.069 (root hips) | 1.634 (head neck upper) | 0.27 |
| 138 | day_work/work7/rouffe (virgin killer)/xps.xps | 与 #67 字节相同 | | | | | | | | | | | | | | | |
| 139 | day_work/work8/(Gantz) Reika Shimohira/xps.xps | 与 #11 字节相同 | | | | | | | | | | | | | | | |
| 140 | day_work/work9/naruto/Naruto - Gaara PACK 1/Shippuden/Main Outfit/With Kazekage Hat/generic_item.mesh | bin | 2.15 | 130 | 12 | 29589 | 35231 | **1.728** | 1.728 | -0.008 | 1.267 | 0.789 | (-0.634, -0.008, -0.582) | (0.634, 1.720, 0.207) | 0.897 (root hips) | 1.474 (head neck upper) | 0.18 |
| 141 | day_work/work9/naruto/Naruto - Gaara PACK 1/Shippuden/Main Outfit/Without Kazekage Hat/generic_item.mesh | bin | 2.15 | 112 | 11 | 28248 | 35014 | **1.730** | 1.730 | -0.008 | 1.267 | 0.753 | (-0.634, -0.008, -0.582) | (0.634, 1.722, 0.171) | 0.897 (root hips) | 1.474 (head neck upper) | 0.18 |
| 142 | day_work/work9/naruto/Naruto - Gaara PACK 1/Shippuden/School Outfit/generic_item.mesh | bin | 2.15 | 89 | 8 | 23244 | 30326 | **1.723** | 1.723 | -0.002 | 1.267 | 0.323 | (-0.634, -0.002, -0.154) | (0.634, 1.722, 0.169) | 0.897 (root hips) | 1.474 (head neck upper) | 0.08 |
| 143 | day_work/work9/naruto/Naruto - Gaara PACK 1/Shippuden/Swimsuit Outfit/generic_item.mesh | bin | 2.15 | 87 | 8 | 22442 | 31184 | **1.699** | 1.699 | 0.022 | 1.267 | 0.305 | (-0.634, 0.022, -0.154) | (0.634, 1.722, 0.151) | 0.897 (root hips) | 1.474 (head neck upper) | 0.11 |
| 144 | day_work/work9/naruto/Naruto - Gaara PACK 1/Shippuden/War Outfit/generic_item.mesh | bin | 2.15 | 92 | 10 | 28095 | 34148 | **1.730** | 1.730 | -0.008 | 1.267 | 0.751 | (-0.634, -0.008, -0.582) | (0.634, 1.722, 0.169) | 0.904 (root hips) | 1.474 (head neck upper) | 0.11 |
| 145 | day_work/work9/naruto/Naruto - Gaara PACK 1/Shippuden/White Costume/generic_item.mesh | bin | 2.15 | 106 | 11 | 28413 | 35416 | **1.730** | 1.730 | -0.008 | 1.267 | 0.751 | (-0.634, -0.008, -0.582) | (0.634, 1.722, 0.169) | 0.912 (root hips) | 1.474 (head neck upper) | 0.15 |
| 146 | day_work/work9/naruto/Naruto - Gaara PACK 1/Shippuden/White Suit/generic_item.mesh | bin | 2.15 | 114 | 10 | 24592 | 31160 | **1.730** | 1.730 | -0.008 | 1.267 | 0.337 | (-0.634, -0.008, -0.154) | (0.634, 1.722, 0.183) | 0.919 (root hips) | 1.474 (head neck upper) | 0.15 |
| 147 | day_work/work9/naruto/Naruto - Sasuko PACK 2/First Appearance/Cursed Seal Level 2/generic_item.mesh | bin | 2.15 | 166 | 15 | 33550 | 27681 | **1.939** | 1.939 | -0.003 | 1.639 | 1.380 | (-0.820, -0.003, -1.117) | (0.820, 1.936, 0.263) | 0.871 (pelvis) | 1.505 (head neck upper) | 0.14 |
| 148 | day_work/work9/naruto/Naruto - Sasuko PACK 2/First Appearance/Normal Eyes/generic_item.mesh | bin | 2.15 | 127 | 13 | 27002 | 22219 | **1.762** | 1.762 | -0.003 | 1.297 | 1.146 | (-0.649, -0.003, -0.883) | (0.649, 1.759, 0.263) | 0.871 (pelvis) | 1.505 (head neck upper) | 0.08 |
| 149 | day_work/work9/naruto/Naruto - Sasuko PACK 2/First Appearance/Sharingan/generic_item.mesh | 与 #148 字节相同 | | | | | | | | | | | | | | | |
| 150 | day_work/work9/naruto/Naruto - Sasuko PACK 2/Itachi Fight/Cursed Seal Level 2/generic_item.mesh | bin | 2.15 | 165 | 16 | 34832 | 27545 | **1.947** | 1.947 | -0.003 | 1.646 | 1.385 | (-0.823, -0.003, -1.121) | (0.823, 1.944, 0.264) | 0.875 (pelvis) | 1.511 (head neck upper) | 0.13 |
| 151 | day_work/work9/naruto/Naruto - Sasuko PACK 2/Itachi Fight/Normal Eyes/generic_item.mesh | bin | 2.15 | 126 | 15 | 26659 | 21677 | **1.769** | 1.769 | -0.003 | 1.302 | 1.151 | (-0.651, -0.003, -0.887) | (0.651, 1.766, 0.264) | 0.875 (pelvis) | 1.511 (head neck upper) | 0.10 |
| 152 | day_work/work9/naruto/Naruto - Sasuko PACK 2/Itachi Fight/Sharingan/generic_item.mesh | 与 #151 字节相同 | | | | | | | | | | | | | | | |
| 153 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Long Pants/Mangekyou Sharingan/generic_item.mesh | bin | 2.15 | 128 | 15 | 25080 | 21601 | **1.762** | 1.762 | -0.003 | 1.303 | 3.048 | (-0.654, -0.003, -0.883) | (0.649, 1.759, 2.165) | 0.871 (pelvis) | 1.505 (head neck upper) | 0.11 |
| 154 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Long Pants/Normal Eyes/generic_item.mesh | 与 #153 字节相同 | | | | | | | | | | | | | | | |
| 155 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Long Pants/Sharingan/generic_item.mesh | 与 #153 字节相同 | | | | | | | | | | | | | | | |
| 156 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Long Pants/Six Paths/generic_item.mesh | 与 #153 字节相同 | | | | | | | | | | | | | | | |
| 157 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Shorts/Mangekyou Sharingan/generic_item.mesh | bin | 2.15 | 128 | 15 | 24923 | 21559 | **1.762** | 1.762 | -0.003 | 1.303 | 3.048 | (-0.654, -0.003, -0.883) | (0.649, 1.759, 2.165) | 0.871 (pelvis) | 1.505 (head neck upper) | 0.13 |
| 158 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Shorts/Normal Eyes/generic_item.mesh | 与 #157 字节相同 | | | | | | | | | | | | | | | |
| 159 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Shorts/Sharingan/generic_item.mesh | 与 #157 字节相同 | | | | | | | | | | | | | | | |
| 160 | day_work/work9/naruto/Naruto - Sasuko PACK 2/No Shirt/Shorts/Six Paths/generic_item.mesh | 与 #157 字节相同 | | | | | | | | | | | | | | | |
| 161 | day_work/work9/naruto/Naruto - Sasuko PACK 2/Taka/Mangekyou Sharingan/generic_item.mesh | bin | 2.15 | 129 | 15 | 20831 | 19410 | **1.762** | 1.762 | -0.003 | 1.303 | 3.048 | (-0.654, -0.003, -0.883) | (0.649, 1.759, 2.165) | 0.871 (pelvis) | 1.505 (head neck upper) | 0.07 |
| 162 | day_work/work9/naruto/Naruto - Sasuko PACK 2/Taka/Normal Eyes/generic_item.mesh | 与 #161 字节相同 | | | | | | | | | | | | | | | |
| 163 | day_work/work9/naruto/Naruto - Sasuko PACK 2/Taka/Sharingan/generic_item.mesh | 与 #161 字节相同 | | | | | | | | | | | | | | | |
| 164 | day_work/work9/naruto/Naruto - Shizuka PACK 1/Original Outfit/generic_item.mesh | bin | 2.15 | 149 | 14 | 29161 | 22489 | **1.677** | 1.677 | -0.001 | 1.196 | 0.409 | (-0.599, -0.001, -0.250) | (0.598, 1.675, 0.159) | 0.903 (pelvis) | 1.435 (head neck upper) | 0.10 |
| 165 | 4090/blender_file/Valby Ultimate Premium/Premium/Valby Ultimate.xps | bin | 3.15 | 632 | 22 | 134376 | 224003 | **1.813** | 1.813 | 0.000 | 0.996 | 0.429 | (-0.498, 0.000, -0.298) | (0.498, 1.813, 0.131) | 1.031 (root hips) | 1.606 (head.x) | 0.93 |
| 166 | 4090/tifa/llm-good/(Gantz) Reika Shimohira/xps.xps | 与 #11 字节相同 | | | | | | | | | | | | | | | |
| 167 | mywork/add_on/Purifier (Inase)/xps.xps | bin | 2.15 | 177 | 15 | 169621 | 199734 | **1.907** | 1.907 | -0.087 | 1.598 | 0.281 | (-0.799, -0.087, -0.144) | (0.799, 1.821, 0.137) | 1.113 (pelvis) | 1.630 (head) | 0.94 |
| 168 | mywork/add_on/Purifier (Inase)/normal pose.xps | bin | 2.15 | 177 | 15 | 169622 | 199734 | **1.901** | 1.901 | -0.081 | 1.197 | 0.281 | (-0.598, -0.081, -0.144) | (0.598, 1.821, 0.137) | 1.113 (pelvis) | 1.630 (head) | 1.05 |
| 169 | mywork/add_on/inase (purifier)_lezisell-A/xps.xps | bin | 3.15 | 109 | 8 | 50124 | 79198 | **1.749** | 1.749 | -0.000 | 1.095 | 0.259 | (-0.548, -0.000, -0.097) | (0.548, 1.749, 0.161) | 1.020 (root hips) | 1.571 (head neck upper) | 0.43 |
| 170 | mywork/mymodel/Purifier (Inase)/xps-A.xps | bin | 3.15 | 177 | 15 | 132714 | 199734 | **1.907** | 1.907 | -0.087 | 1.197 | 0.281 | (-0.598, -0.087, -0.144) | (0.598, 1.821, 0.137) | 1.113 (pelvis) | 1.630 (head) | 0.98 |

### B. 骨架与命名

| # | 根骨骼 (parent −1) | 命名约定猜测 | 附加标签 | generic 核心/14 | DAZ 核心/18 | unused* | 前 12 个骨骼名 |
|---|---|---|---|---|---|---|---|
| 1 | root ground | xnalara_generic |  | 14 | 0 | 31 | root ground, root hips, pelvis, pelvis alt, leg left thigh, leg left thigh adj 1, leg left knee, leg left ankle, leg left toes meta, leg left toes, leg left toes 5a, leg left toes 5b |
| 2 | root ground | xnalara_generic |  | 14 | 0 | 31 | root ground, root hips, pelvis, pelvis alt, leg left thigh, leg left thigh adj 1, leg left knee, leg left ankle, leg left toes meta, leg left toes, leg left toes 5a, leg left toes 5b |
| 3 | root ground | xnalara_generic |  | 13 | 0 | 19 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, head neck lower, head neck upper, head eyelid upper right, head eyelid upper left, head eyelid lower right, head eyelid lower left |
| 4 | root ground | xnalara_generic |  | 13 | 0 | 17 | root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 xtra04, leg right thigh, leg right knee, leg right ankle, leg right toes |
| 5 | root groujnd | xnalara_generic |  | 13 | 0 | 31 | root groujnd, root hips, unused bip001 pelvis, leg left thigh, unused bip001 thightwist_lt, unused knee_l, leg left knee, leg left ankle, leg left toes, unused bip001 lcalftwist, unused bip001 lcalftwist1, leg right thigh |
| 6 | unused pc_a10_hd | xnalara_generic |  | 13 | 0 | 52 | unused pc_a10_hd, root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, arm left shoulder 1 |
| 7 | root ground | prop(<=3 bones) |  | 0 | 0 | 0 | root ground |
| 8 | unused pc_j01_nk | xnalara_generic |  | 13 | 0 | 65 | unused pc_j01_nk, root ground, root hips, unused bip001 pelvis, butt left, butt right, unused bip001 clitorissub, vagina clitoris, leg left thigh, leg left knee, unused bip001 calfsub_l, leg left ankle |
| 9 | root ground | xnalara_generic |  | 13 | 0 | 30 | root ground, root hips, unused bip001 pelvis, spine lower, leg left thigh, leg left knee, leg left ankle, leg left toes, unused muscle strand076, unused muscle_ankle_l, unused bip001 lcalftwist, unused bip001 lcalftwist1 |
| 10 | root ground | xnalara_generic |  | 13 | 0 | 30 | unused bip001 pelvis, spine lower, leg left thigh, leg left ankle, leg left toes, unused muscle strand076, unused muscle_ankle_l, unused bip001 lcalftwist, unused bip001 lcalftwist1, leg right thigh, leg right ankle, leg right toes |
| 11 | root | other:unreal |  | 1 | 0 | 0 | root, hip, pelvis, Butt.l, Butt.r, thigh_l, calf_l, calf_twist_01_l, calf_twist_02_l, foot_l, ball_l, thigh_twist_01_l |
| 12 | root ground | xnalara_generic |  | 11 | 0 | 614 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, unused face, head eyebrow middle, head lip upper middle, head nose middle, head jaw, head lip lower middle |
| 13 | root ground | xnalara_generic |  | 11 | 0 | 614 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, unused face, head eyebrow middle, head lip upper middle, head nose middle, head jaw, head lip lower middle |
| 14 | root ground | xnalara_generic |  | 11 | 0 | 614 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, unused face, head eyebrow middle, head lip upper middle, head nose middle, head jaw, head lip lower middle |
| 15 | root ground | xnalara_generic |  | 13 | 0 | 41 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toe, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 16 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 17 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 18 | c_pos | daz_g8 | auto_rig_pro×70, lr_prefix×40 | 1 | 18 | 0 | c_pos, hip, pelvis, c_bot_bend.l, c_bot_bend.r, Genitals, Genitals.Top, VagBot, vagMinoraM.L, vagMinoraM.R, vagMayoraM.L, vagMayoraM.R |
| 19 | c_pos | daz_g8 | auto_rig_pro×70, lr_prefix×40 | 1 | 18 | 0 | c_pos, hip, pelvis, c_bot_bend.l, c_bot_bend.r, Genitals, Genitals.Top, VagBot, vagMinoraM.L, vagMinoraM.R, vagMayoraM.L, vagMayoraM.R |
| 20 | root ground | xnalara_generic |  | 13 | 0 | 25 | root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, head neck lower, head neck upper |
| 21 | unused blackwidow | xnalara_generic |  | 14 | 0 | 3 | unused blackwidow, root ground, root hips, spine lower, spine middle, spine upper, head neck lower, head neck upper, unusedC_FaceBase_a, head eyeball left, head eyeball right, head forehead middle |
| 22 | unused blackwidow | xnalara_generic |  | 14 | 0 | 3 | unused blackwidow, root ground, root hips, spine lower, spine middle, spine upper, head neck lower, head neck upper, unusedC_FaceBase_a, head eyeball left, head eyeball right, head forehead middle |
| 23 | unused pc_c08_hd | xnalara_generic |  | 12 | 0 | 38 | leg left armor, leg right armor, butt ring left, butt ring right, unused trash 17, unused ac_leg_l, leg left ankle, unused bip001 lcalftwist, unused bip001 lcalftwist1, unused ac_leg_r, leg right ankle, unused bip001 rcalftwist |
| 24 | root ground | prop(<=3 bones) |  | 0 | 0 | 0 | root ground |
| 25 | root ground | prop(<=3 bones) |  | 0 | 0 | 0 | root ground |
| 26 | root ground | xnalara_generic |  | 13 | 0 | 29 | unused trash 17, spine lower, leg left thigh, leg left ankle, leg left toes, unused bip001 lcalftwist, unused bip001 lcalftwist1, unused bip001 thightwist_lt, unused knee_l, leg right thigh, leg right ankle, leg right toes |
| 27 | root ground | prop(<=3 bones) |  | 0 | 0 | 0 | root ground |
| 28 | Master | other:lr_prefix |  | 0 | 0 | 0 | Master, hip, M_Hips, L_Thigh, L_Shin, L_Foot, L_Foot_helper_ST, L_Heel2_helper_ST, L_Toe, L_ToeA_01, L_ToeA_01_ST, L_ToeA_02 |
| 29 | Master | other:lr_prefix |  | 0 | 0 | 0 | Master, hip, M_Hips, L_Thigh, L_Shin, L_Foot, L_Toe, L_ToeA_01, L_ToeA_01_ST, L_ToeA_02, L_ToeA_02_ST, L_ToeB_01 |
| 30 | c_pos, c_arms_pole.l, c_arms_pole.r, c_foot_ik.r …(+6) | other:auto_rig_pro |  | 0 | 0 | 0 | c_pos, c_traj, c_root_master.x, c_root.x, c_p_root.x, c_root_bend.x, root.x, c_thigh_b.l, thigh_ik.l, leg_ik.l, c_thigh_fk.l, thigh_fk.l |
| 31 | c_pos, c_arms_pole.l, c_arms_pole.r, c_foot_ik.r …(+6) | other:auto_rig_pro |  | 0 | 0 | 0 | c_pos, c_traj, c_root_master.x, c_root.x, c_p_root.x, c_root_bend.x, root.x, c_thigh_b.l, thigh_ik.l, leg_ik.l, c_thigh_fk.l, thigh_fk.l |
| 32 | root | daz_g8+xnalara_generic |  | 2 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 33 | root | daz_g8+xnalara_generic |  | 2 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 34 | root ground | xnalara_generic |  | 13 | 0 | 27 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob left charm, boob right 1, boob right 2, boob right charm |
| 36 | unused pc_f08_hd | xnalara_generic |  | 13 | 0 | 42 | unused pc_f08_hd, root ground, root hips, unused bip001 pelvis, spine lower, leg left thigh, unused bip001 l thigh_twist, skirt back left 1a, skirt back left 1b, skirt back left 2a, skirt back left 2b, skirt back left 2c |
| 37 | root ground | xnalara_generic |  | 13 | 0 | 27 | root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob left tassel 1, boob left tassel 2, boob right 1, boob right 2 |
| 38 | root ground | xnalara_generic |  | 13 | 0 | 24 | root ground, root hips, spine lower, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 lcalftwist, unused bip001 lcalftwist1, leg right thigh, leg right knee, leg right ankle |
| 39 | root ground | xnalara_generic |  | 13 | 0 | 28 | root ground, root hips, unused bip001 pelvis, butt left, butt right, vagina clitoris 1, vagina clitoris 2, leg left thigh, leg left knee, leg left gastrocnemius, leg left ankle, leg left toes |
| 40 | root ground | xnalara_generic |  | 13 | 0 | 31 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, head neck tie 1, head neck tie 2, boob left 1, boob left 2, boob right 1, boob right 2 |
| 41 | root ground | xnalara_generic |  | 13 | 0 | 25 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, head neck lower, head neck upper |
| 42 | root ground | xnalara_generic |  | 13 | 0 | 23 | root ground, gift root, root hips, unused bip001 pelvis, spine lower, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 lcalftwist, unused bip001 lcalftwist1, leg right thigh |
| 43 | root ground | xnalara_generic |  | 13 | 0 | 60 | unused kartia_head_nosearea_tonguering_obj001, root hips, unused trash 17, unused bip001 butt_l, unused bip001 butt_r, unused bip001 clitorissub, vagina clitoris, leg left thigh, leg left knee, unused bip001 calfsub_l, leg left ankle, leg left toes |
| 44 | root ground | xnalara_generic |  | 13 | 0 | 19 | root ground, root hips, unused trash 17, belt ring left, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, arm left shoulder 1 |
| 45 | unused pc_d06_hd | xnalara_generic |  | 12 | 0 | 29 | unused pc_d06_hd, root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, spine shoulders |
| 46 | root ground | xnalara_generic |  | 13 | 0 | 17 | root ground, root hips, unused trash 17, spine lower, skirt back middle upper 1, skirt back middle upper 2, skirt back middle upper 3, skirt back middle lower 1, skirt back middle lower 2, skirt back middle lower 3, skirt back middle lower 4, spine middle |
| 47 | weapon sword root, root ground | xnalara_generic |  | 13 | 0 | 30 | weapon sword root, weapon sword left, weapon sword right, root ground, root hips, unused trash 17, leg left thigh, unused bip001 thightwist_lt, unused knee_l, leg left knee, leg left ankle, leg left toes |
| 48 | root ground | xnalara_generic |  | 13 | 0 | 22 | root ground, root hips, unused bip001 pelvis, anus outside, anus inside, butt left, butt right, vagina clitoris 1, vagina clitoris 2, leg left thigh, leg left knee, leg left gastrocnemius |
| 49 | root ground | xnalara_generic |  | 13 | 0 | 13 | root ground, root hips, unused bip001 pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 xtra04, leg right thigh, leg right knee, leg right ankle, leg right toes |
| 50 | head hat, unused pc_j01_nk | xnalara_generic |  | 13 | 0 | 59 | head hat, unused pc_j01_nk, root ground, root hips, unused bip001 pelvis, butt left, butt right, vagina clitoris 2, vagina clitoris 1, leg left thigh, leg left knee, unused bip001 calfsub_l |
| 51 | unused pc_j03_hd | xnalara_generic |  | 13 | 0 | 34 | unused pc_j03_hd, root ground, root hips, unused bip001 pelvis, sash right 1, sash right 2, sash right 3, belt root, belt bag root, weapon telescope, belt holster left, sash front 1 |
| 52 | root ground | xnalara_generic |  | 13 | 0 | 27 | unused bip001 pelvis, spine lower, spine middle, spine upper, head neck lower, arm left shoulder 1, arm left wrist, arm left finger 1a, arm left finger 1b, arm left finger 1c, arm left finger 2a, arm left finger 2b |
| 53 | root ground | xnalara_generic |  | 13 | 0 | 11 | root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, head neck lower, head neck upper, head hair left 1, head hair left 2, head hair front 1, head hair front 2 |
| 54 | root ground | xnalara_generic |  | 13 | 0 | 20 | root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, head neck lower, head neck upper, head eyelid upper right, unused ac eyelid_bone_ur, head eyelid upper left, unused ac eyelid_bone_ul |
| 55 | root ground | xnalara_generic |  | 13 | 0 | 30 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, head neck lower, head neck upper |
| 56 | root ground | xnalara_generic |  | 13 | 0 | 51 | root ground, root hips, unused trash 17, butt left, butt right, unused bip001 clitorissub, vagina clitoris, vagina labia left root, vagina labia left 3, vagina labia left 2, vagina labia left 1, vagina labia right root |
| 57 | root ground | xnalara_generic |  | 13 | 0 | 27 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, head neck lower, head neck upper |
| 58 | root ground | xnalara_generic |  | 13 | 0 | 29 | root ground, weapon staff, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left, boob right, head neck lower, head neck upper, head hair left 1 |
| 59 | root ground | xnalara_generic |  | 13 | 0 | 33 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, head neck lower, head neck upper |
| 61 | pc_g01_eros_common | other:3dsmax_biped |  | 0 | 0 | 0 | Bip001 Pelvis, Bip001 Anus_inside, Bip001 Butt_L, Bip001 Butt_R, Bip001 ClitorisSub, Bip001 Clitoris, Bip001 L Thigh, Bip001 L Calf, Bip001 CalfSub_L, Bip001 L Foot, Bip001 L Toe0, Bip001 ToeBig_L |
| 62 | root ground | xnalara_generic |  | 13 | 0 | 30 | unused bip001 pelvis, anus inside, bitt left, bitt right, vagina clitoris 1, vagina clitoris 2, leg left thigh, leg left knee, leg left gastrocnemius, leg left ankle, leg left toes, leg left toe 1a |
| 63 | root ground | xnalara_generic |  | 13 | 0 | 35 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, head neck lower, head neck upper |
| 64 | root ground | xnalara_generic |  | 13 | 0 | 29 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2, head neck lower, head neck upper |
| 65 | root ground | xnalara_generic |  | 13 | 0 | 40 | root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, head neck lower, head neck upper, head eyeball left, head eyeball right, head eyelid upper left, unused ac eyelid_ul |
| 66 | root ground | xnalara_generic |  | 13 | 0 | 37 | root ground, root hips, unused trash 17, spine lower, spine middle, spine upper, head boob left 1, head boob left 2, head boob right 1, head boob right 2, head neck lower, head neck upper |
| 67 | unused pc_g01_nk | xnalara_generic |  | 13 | 0 | 63 | unused pc_g01_nk, root ground, root hips, unused bip001 pelvis, butt left, butt right, unused bip001 clitorissub, vagina clitoris, leg left thigh, leg left knee, unused bip001 calfsub_l, leg left ankle |
| 68 | unused pc_b06_hd | xnalara_generic |  | 13 | 0 | 26 | unused pc_b06_hd, root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 l thigh_twist, unused bip001 pelvis_l_twist, unused bip001 pelvis_r_twist, leg right thigh |
| 69 | unused pc_b06_hd | xnalara_generic |  | 13 | 0 | 26 | unused pc_b06_hd, root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 l thigh_twist, unused bip001 pelvis_l_twist, unused bip001 pelvis_r_twist, leg right thigh |
| 70 | unused pc_b10_hd | xnalara_generic |  | 13 | 0 | 31 | unused pc_b10_hd, root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, holster left root, holster left strap 1, holster left strap 2, holster left strap 3 |
| 71 | unused pc_b10_hd | xnalara_generic |  | 13 | 0 | 31 | unused pc_b10_hd, root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, holster left root, holster left strap 1, holster left strap 2, holster left strap 3 |
| 72 | unused pc_b10_hd | xnalara_generic |  | 13 | 0 | 31 | unused pc_b10_hd, root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, holster left root, holster left strap 1, holster left strap 2, holster left strap 3 |
| 74 | unused pc_b10_hd | xnalara_generic |  | 13 | 0 | 31 | unused pc_b10_hd, root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, holster left root, holster left strap 1, holster left strap 2, holster left strap 3 |
| 76 | root ground | xnalara_generic |  | 13 | 0 | 17 | root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 xtra04, leg right thigh, leg right knee, leg right ankle, leg right toes |
| 78 | unused pc_a06_hd | xnalara_generic |  | 13 | 0 | 53 | unused pc_a06_hd, root ground, root hips, unused bip001 pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 xtra04, leg right thigh, leg right knee, leg right ankle |
| 79 | unused pc_a07_hd | xnalara_generic |  | 12 | 0 | 38 | unused pc_a07_hd, root ground, root hips, unused bip001 pelvis, leg left thigh, unused bip001 thightwist_lt, unused knee_l, leg left knee, leg left ankle, unused bip001 lcalftwist, unused bip001 lcalftwist1, leg right thigh |
| 81 | root ground | xnalara_generic |  | 13 | 0 | 26 | root ground, root hips, unused trash 17, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 xtra04, unused pocket_dum_l02, leg right thigh, leg right knee, leg right ankle |
| 82 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 83 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 84 | role_sanli_diaocha_skin, root ground | other:3dsmax_biped |  | 0 | 0 | 0 | role_sanli_diaocha_skin, root ground, Bip001, Bip001 Pelvis, Bip001 L Thigh, Bip001 L Calf, Bip001 L Foot, Bip001 L Toe0, Point006, Bip001 R Thigh, Bip001 R Calf, Bip001 R Foot |
| 85 | Root, root | other:3dsmax_biped |  | 0 | 0 | 0 | Root, Bip001, Bip001-Pelvis, Bip001-Spine, Bip001-Spine1, Bip001-Spine2, Bip001-Neck, Bip001-L-Clavicle, Bip001-L-UpperArm, Bip001-L-Forearm, Bip001-L-Hand, Bip001-L-Finger0 |
| 86 | Root.001 | other:3dsmax_biped |  | 0 | 0 | 0 | Root.001, Bip001, Bip001-Pelvis, Bip001-Spine, Bip001-Spine1, Bip001-Spine2, Bip001-Neck, Bip001-Head, L-Eye, R-Eye, Bip001-Head.001, Root |
| 87 | root ground | xnalara_generic |  | 13 | 0 | 36 | root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, cape ball middle, cape ball right 4, cape ball left 4, cape ball right 3, cape ball left 3, cape ball right 2 |
| 88 | root ground | xnalara_generic |  | 14 | 0 | 5 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, accessory attach ankle left, leg left knee ctr, leg left thigh ctr, leg left thigh ctr 2, leg left thigh adj a |
| 89 | root ground | xnalara_generic |  | 14 | 0 | 5 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, accessory attach ankle left, leg left knee ctr, leg left thigh ctr, leg left thigh ctr 2, leg left thigh adj a |
| 90 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 91 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 92 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 93 | root | daz_g8 |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 94 | root ground | xnalara_generic |  | 14 | 0 | 34 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, head eyeball left, head eyeball right, head eyelid upper left, head eyelid lower left, head eyelid upper right, head eyelid lower right |
| 95 | root ground | xnalara_generic |  | 14 | 0 | 34 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, head eyeball left, head eyeball right, head eyelid upper left, head eyelid lower left, head eyelid upper right, head eyelid lower right |
| 96 | root ground | xnalara_generic |  | 13 | 0 | 0 | root ground, root hips, pelvis, adj hips upper, pelvis lower, adj hips lower, adj butthole, adj vulva, vagina right a, vagina left a, vagina right b, vagina left b |
| 97 | root | daz_g8+xnalara_generic |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 98 | root | daz_g8+xnalara_generic |  | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 99 | root ground | xnalara_generic |  | 14 | 0 | 31 | root ground, root hips, pelvis, leg right thigh, leg right knee, leg right adj 0, leg right adj 1, leg right ankle, leg right toes, leg right toes 1a, leg right toes 1b, leg right toes 2a |
| 100 | root ground, root | other:re_engine |  | 0 | 0 | 0 | spine 2, l arm clavicle, l arm humerus, l arm humerus twist 3 H, l scapula 0, r arm clavicle, r arm humerus, r arm humerus twist 3 H, r scapula 0, neck 0, neck 1, head |
| 101 | root | other:re_engine |  | 0 | 0 | 0 | root, Null Offset, COG, hips, bag1, l leg front muscleOffset, l leg front muscle, l leg back muscleOffset, l leg back muscle, l leg side muscleOffset, l leg side muscle, r leg front muscleOffset |
| 102 | root ground, Armature | other:re_engine |  | 0 | 0 | 591 | root, Null Offset, COG, hips, bag1, bag2, setProp E 00, l leg front muscleOffset, l leg front muscle, l leg back muscleOffset, l leg back muscle, l leg side muscleOffset |
| 103 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, root hips, spine lower, spine lower adj, spine middle, ValveBiped_Bip01_Spine2, spine upper adj, breast left base, breast right base, unused spine top.001, ValveBiped.Bip01_L_Breast0, breast left 2 |
| 104 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, root hips, spine lower, spine lower adj, spine middle, ValveBiped_Bip01_Spine2, spine upper adj, breast left base, breast right base, unused spine top.001, ValveBiped.Bip01_L_Breast0, breast left 2 |
| 105 | c_pos | other:auto_rig_pro | daz_fragments×49 | 0 | 1 | 256 | c_pos, c_traj, c_root_master.x, c_root.x, c_root_bend.x, root.x, skirt_front, skirt_front_end, unused skirt front end_end, skirt_back 1, skirt_back 2, skirt_back 2_end |
| 106 | root ground | xnalara_generic |  | 11 | 0 | 252 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, unuseddummy, head eyebrow centre, head lip upper middle, head nose centre, head jaw, head lip lower middle |
| 107 | Master | other:lr_prefix |  | 0 | 0 | 0 | Master, hip, M_Hips, L_Thigh, L_Shin, L_Foot, L_Toe, L_ToeA_01, L_ToeA_02, L_ToeA_02_bot_ST, L_ToeA_02_top_ST, L_ToeA_01_bot_ST |
| 108 | root ground | xnalara_generic |  | 14 | 0 | 34 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, head eyeball left, head eyeball right, head eyelid upper left, head eyelid lower left, head eyelid upper right, head eyelid lower right |
| 109 | root ground | xnalara_generic |  | 14 | 0 | 34 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, head eyeball left, head eyeball right, head eyelid upper left, head eyelid lower left, head eyelid upper right, head eyelid lower right |
| 110 | root ground | xnalara_generic |  | 14 | 0 | 34 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, head eyeball left, head eyeball right, head eyelid upper left, head eyelid lower left, head eyelid upper right, head eyelid lower right |
| 111 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 112 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 113 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 114 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 115 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 116 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 117 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 118 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 119 | root ground | xnalara_generic |  | 14 | 0 | 2 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 120 | root ground | xnalara_generic |  | 14 | 0 | 2 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 121 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 122 | root ground | xnalara_generic |  | 14 | 0 | 2 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 123 | root ground | xnalara_generic |  | 14 | 0 | 3 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 124 | root ground | xnalara_generic |  | 14 | 0 | 3 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 125 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 126 | root ground | xnalara_generic |  | 14 | 0 | 2 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 127 | root ground | xnalara_generic |  | 14 | 0 | 1 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg left knee ctr, leg left thigh ctr, leg left thigh ctr2, leg right thigh, leg right knee |
| 128 | hip | other:valve_biped | daz_fragments×34, generic_style×6 | 0 | 3 | 0 | hip, ValveBiped.Bip01_Pelvis, Skirt Front Left 1, Skirt Front Left 2, Skirt Front Left 3, Skirt Front Left 4, Skirt Front Left 5, Skirt Front Right 1, Skirt Front Right 2, Skirt Front Right 3, Skirt Front Right 4, Skirt Front Right 5 |
| 129 | unused_Diana_Wonder_Woman_-_Shield_Bone, unused_Diana_Wonder_Woman_-_God_Slayer_Bone, root ground | xnalara_generic |  | 14 | 0 | 346 | unused_Diana_Wonder_Woman_-_Shield_Bone, unused shield, unused shield end, unused_Diana_Wonder_Woman_-_God_Slayer_Bone, unused sword, unused sword end, root ground, unused c traj, root hips, pelvis, pelvis ctrl, skirt ctrl |
| 132 | root | prop(<=3 bones) |  | 0 | 0 | 0 | root |
| 133 | root ground, root | xnalara_generic | auto_rig_pro×26 | 14 | 0 | 0 | root ground, root hips, pelvis, pelvis bend.x, pelvis x, genitals, vagmayorat.l, vagmayoram.l, vagmayorab.l, vagmayorat.r, vagmayoram.r, vagmayorab.r |
| 136 | unused pc_j07_hd | xnalara_generic |  | 13 | 0 | 47 | unused pc_j07_hd, unused pc_j07_hd_cup, root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2 |
| 137 | unused pc_c09_hd | xnalara_generic |  | 12 | 0 | 50 | unused pc_c09_hd, weapon sword, root ground, root hips, unused bip001 pelvis, spine lower, spine middle, spine upper, boob left 1, boob left 2, boob right 1, boob right 2 |
| 140 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, pelvis, coat side right a, coat side right b, coat side right c, coat side right d, leg right thigh, leg right knee, leg right ankle, leg right toes, coat side left a |
| 141 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, pelvis, coat side right a, coat side right b, coat side right c, coat side right d, leg right thigh, leg right knee, leg right ankle, leg right toes, coat side left a |
| 142 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, pelvis, leg right thigh, leg right knee, leg right ankle, leg right toes, leg left thigh, leg left knee, leg left ankle, leg left toes, spine lower |
| 143 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, pelvis, leg right thigh, leg right knee, leg right ankle, leg right toes, leg left thigh, leg left knee, leg left ankle, leg left toes, spine lower |
| 144 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg right thigh, leg right knee, leg right ankle, leg right toes, spine lower |
| 145 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, spine lower, spine upper, head neck lower, head neck upper, head jaw, head lip lower right, head lip lower left, head lip lower middle, head tongue a, head tongue b |
| 146 | root ground | xnalara_generic |  | 14 | 0 | 0 | root ground, root hips, pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, leg right thigh, leg right knee, leg right ankle, leg right toes, spine lower |
| 147 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, pelvis, spine lower, spine upper, head neck lower, head neck upper, head jaw, head lip lower right, head lip lower left, head lip lower middle, head tongue a, head tongue b |
| 148 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, pelvis, spine lower, spine upper, head neck lower, head neck upper, head jaw, head lip lower right, head lip lower left, head lip lower middle, head tongue a, head tongue b |
| 150 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, leg right thigh, leg right knee, leg right ankle, leg right toes, cloth side right a, cloth side right b, cloth front right a, cloth front right b, cloth back right a, cloth back right b, leg left thigh |
| 151 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, leg right thigh, leg right knee, leg right ankle, leg right toes, cloth side right a, cloth side right b, cloth front right a, cloth front right b, cloth back right a, cloth back right b, leg left thigh |
| 153 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, pelvis, spine lower, spine upper, head neck lower, head neck upper, head jaw, head lip lower right, head lip lower left, head lip lower middle, head tongue a, head tongue b |
| 157 | root ground | xnalara_generic |  | 13 | 0 | 1 | root ground, pelvis, spine lower, spine upper, head neck lower, head neck upper, head jaw, head lip lower right, head lip lower left, head lip lower middle, head tongue a, head tongue b |
| 161 | root ground | xnalara_generic |  | 13 | 0 | 0 | root ground, pelvis, spine lower, spine upper, head neck lower, head neck upper, head jaw, head lip lower right, head lip lower left, head lip lower middle, head tongue a, head tongue b |
| 164 | root ground | xnalara_generic |  | 13 | 0 | 0 | root ground, pelvis, spine lower, spine upper, head neck lower, head neck upper, head jaw, head lip lower right, head lip lower middle, head lip lower left, head tongue a, head tongue b |
| 165 | c_pos, c_p_neck_01.x, root_ref.x, c_arms_pole.l …(+8) | other:auto_rig_pro | generic_style×50 | 1 | 0 | 0 | c_pos, c_traj, head_scale_fix.x, c_head.x, head.x, helmet root, helmet ctrl, helmet ear root, helmet ear right 1, helmet ear right 2, helmet ear left 1, helmet ear left 2 |
| 167 | root | daz_g8 | generic_style×8 | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 168 | root | daz_g8 | generic_style×8 | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |
| 169 | root ground | xnalara_generic |  | 13 | 0 | 13 | root ground, root hips, unused bip001 pelvis, leg left thigh, leg left knee, leg left ankle, leg left toes, unused bip001 xtra04, leg right thigh, leg right knee, leg right ankle, leg right toes |
| 170 | root | daz_g8 | generic_style×8 | 1 | 18 | 0 | root, hip, pelvis, lThighBend, lThighTwist, lShin, lFoot, lMetatarsals, lToe, lSmallToe4, lSmallToe4_2, lSmallToe3 |

### C. 材质、标志、权重与警告

| # | 渲染组 (α=alpha) | 贴图扩展名 | 可选项 +/− | 可选组 | nPart | .00N 后缀 | flags 原值 (id=value) | 法线 swizzle | 默认姿势 | 权重和>1.01 | 权重和<0.99 | 全零权重 | 最大影响数 | >4 影响顶点 | 校验问题 | 警告 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6α | .png×4 | 0/2 |  |  | 1 |  |  |  | 11455 | 32 |  | 9 | 5191 | 2 |  |
| 2 | 2 4 5 6α 7α 24 26 27α 29α 40 | .png×74 | 11/5 |  |  | 27 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  | 10405 | 812 |  | 4 |  | 2 |  |
| 3 | 7α 24 25α | .png×29 .tga×4 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 4 | 7α 24 25α 38 | .png×29 | 2/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 5 | 7α 24 25α | .png×25 | 1/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 6 | 7α 24 25α 38 | .png×29 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 7 | 38 | .png×4 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 1 |  |  | trailing 97B |
| 8 | 7α 24 25α | .png×81 | 13/2 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 9 | 7α 24 25α | .png×34 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 10 | 7α 24 25α | .png×34 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 11 | 4 5 6α 7α | .jpg×42 .png×2 | 5/11 | Body, Suit |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 12 | 24 25α 40 | .png×58 .dds×3 | 2/2 |  |  |  |  |  |  |  |  |  | 4 |  |  |  |
| 13 | 24 25α 40 | .png×58 .dds×3 | 2/2 |  |  |  |  |  |  |  |  |  | 4 |  |  |  |
| 14 | 24 25α 40 | .png×60 .dds×3 | 2/2 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 482 骨 |  |  |  | 4 |  |  | trailing 97B |
| 15 | 4 7α 22 24 25α 26 27α 28 30 38 40 41α | .png×250 .tga×56 .dds×2 | 10/56 | earring, glasses, hair, item | 1 | 19 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 731 骨 |  |  |  | 4 |  |  | trailing 97B |
| 16 | 4 6α | .jpg×41 .png×7 | 4/12 | Suit A, Suit B |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 17 | 4 6α | .jpg×41 .png×7 | 4/12 | Suit A, Suit B |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 18 | 4 6α | .jpg×65 .png×5 | 13/12 | Bodysuit, Brows |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 19 | 4 6α | .jpg×65 .png×5 | 13/12 | Bodysuit, Brows |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 20 | 7α 24 25α | .png×33 | 2/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 21 | 7α 22 23α 24 25α 26 27α 29α | .png×75 .tga×48 .jpg×6 .dds×1 | 7/5 | earring, hair, shoes |  | 14 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 22 | 7α 22 23α 24 25α 26 27α 29α | .png×75 .tga×48 .jpg×6 .dds×1 | 7/5 | earring, hair, shoes |  | 14 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 23 | 7α 24 25α | .png×37 | 3/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 24 | 24 | .png×4 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 1 |  |  | trailing 97B |
| 25 | 24 | .png×4 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 1 |  |  | trailing 97B |
| 26 | 7α 24 25α | .png×25 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 27 | 38 | .png×4 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 1 |  |  | trailing 97B |
| 28 | 4 7α | .jpg×36 .png×1 | 6/4 | Bathrobe |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 29 | 4 6α 7α | .jpg×26 .png×5 | 4/8 | Dress |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 30 | 5 | .png×16 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  | 691 | 4337 |  | 33 | 42218 | 7 |  |
| 31 | 5 | .png×14 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  | 1479 | 4754 |  | 33 | 44196 | 4 |  |
| 32 | 4 6α | .png×18 .jpg×18 | 5/4 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 33 | 4 6α | .png×18 .jpg×18 | 5/4 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 34 | 7α 24 25α | .png×25 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 36 | 7α 24 25α | .png×21 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 37 | 7α 24 25α | .png×41 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 38 | 7α 24 25α | .png×33 | 1/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 39 | 24 25α | .png×28 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 40 | 7α 24 25α | .png×21 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 41 | 7α 24 25α 38 | .png×41 | 4/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 42 | 7α 24 25α | .png×37 | 1/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 43 | 7α 24 25α | .png×93 | 17/1 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 44 | 7α 24 25α | .png×25 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 45 | 5 7α 24 39α | .png×13 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 46 | 7α 24 25α | .png×56 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 47 | 7α 24 25α | .png×33 | 3/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 48 | 7α 24 25α | .png×41 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 49 | 7α 24 25α | .png×29 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 50 | 7α 24 25α | .png×81 | 10/5 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 51 | 7α 24 25α | .png×29 | 2/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 52 | 7α 24 25α | .png×37 | 1/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 53 | 24 25α 38 | .png×40 | 3/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 3 |  |  | trailing 97B |
| 54 | 7α 24 25α | .png×25 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 55 | 7α 24 25α | .png×37 | 2/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 56 | 7α 24 25α | .png×73 | 9/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 57 | 7α 24 25α | .png×37 | 1/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 58 | 7α 24 25α | .png×57 | 8/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 59 | 7α 24 25α | .png×21 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 61 | 5 7α | .png×7 |  |  |  |  |  |  |  |  |  |  | 4 |  |  |  |
| 62 | 24 25α | .png×28 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 63 | 7α 24 | .png×34 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 64 | 7α 24 25α | .png×29 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 65 | 7α 24 25α 38 | .png×41 | 3/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 66 | 7α 24 25α | .png×41 | 1/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 67 | 7α 24 25α | .png×57 | 8/1 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 68 | 7α 24 25α | .png×25 | 1/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 69 | 7α 24 25α | .png×25 | 1/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 70 | 7α 24 25α | .png×33 | 1/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 71 | 7α 24 25α | .png×41 | 3/1 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 72 | 7α 24 25α | .png×33 | 1/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 74 | 7α 24 25α | .png×33 | 1/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 76 | 7α 24 25α | .png×21 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 78 | 7α 24 25α | .png×25 | 1/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 79 | 7α 24 25α | .png×37 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 81 | 7α 24 25α 38 | .png×25 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 82 | 4 5 6α | .jpg×20 .png×10 | 3/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 83 | 4 5 6α | .jpg×20 .png×10 | 3/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 84 | 5 | .png×9 | 0/4 |  |  | 8 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 85 | 5 | .png×1 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 86 | 5 | .png×21 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 8 | 9756 |  |  |
| 87 | 7α 24 25α | .png×33 | 1/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 88 | 4 6α 7α 40 41α | .png×39 .tga×30 | 10/1 |  |  |  |  |  |  |  |  |  | 4 |  |  |  |
| 89 | 4 6α 7α 40 41α | .png×39 .dds×30 | 10/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 90 | 4 6α | .jpg×31 .png×9 | 9/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 91 | 4 6α | .jpg×31 .png×9 | 9/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 92 | 4 6α | .jpg×23 .png×11 | 3/3 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 93 | 4 6α | .jpg×23 .png×11 | 3/3 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 94 | 7α 22 24 27α 38 41α | .png×74 | 1/5 | Weapon |  | 13 |  |  |  |  |  |  | 4 |  |  |  |
| 95 | 7α 22 24 27α 38 41α | .png×74 | 1/5 | Weapon |  | 13 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 305 骨 |  |  |  | 4 |  |  | trailing 97B |
| 96 | 5 6α 7α 24 26 27α | .png×67 | 5/0 |  |  | 14 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 294 骨 |  |  |  | 4 |  |  | trailing 97B |
| 97 | 4 6α | .jpg×24 .png×12 | 6/2 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 98 | 4 6α | .jpg×24 .png×12 | 6/2 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 99 | 4 6α 24 27α | .png×47 .jpg×33 | 15/7 | outfit 1, outfit 2 |  | 28 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 100 | 40 41α | .dds×19 .png×5 | 7/1 |  |  |  |  |  |  |  |  |  | 4 |  |  |  |
| 101 | 41α | .dds×75 |  |  |  |  |  |  |  |  |  |  | 8 | 11258 |  |  |
| 102 | 4 40 41α | .dds×17 .png×9 | 7/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 725 骨 |  |  |  | 4 |  |  | trailing 97B |
| 103 | 4 5 7α 40 | .png×50 | 6/9 | clothes, outline |  | 3 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 3 |  |  |  |
| 104 | 4 5 7α 40 | .png×50 | 6/9 | clothes, outline |  | 3 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 217 骨 |  |  |  | 3 |  |  | trailing 97B |
| 105 | 5 7α | .png×22 .jpg×13 | 12/6 | Body, Clothes, Hair |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 499 骨 |  |  |  | 11 | 3969 |  | trailing 97B |
| 106 | 22 24 25α 40 | .png×55 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 171 骨 |  |  |  | 4 |  |  | trailing 97B |
| 107 | 4 6α | .jpg×37 .png×9 | 4/7 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 108 | 7α 22 24 25α 27α 31α 38 | .png×137 | 13/7 | Outfit, Weapon |  | 24 |  |  |  |  |  |  | 4 |  |  |  |
| 109 | 7α 22 24 25α 27α 31α 38 | .png×137 | 13/7 | Outfit, Weapon |  | 24 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 110 | 7α 22 24 25α 27α 31α 38 | .png×137 | 13/7 | Outfit, Weapon |  | 24 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 305 骨 |  |  |  | 4 |  |  | trailing 97B |
| 111 | 4 5 6α 7α 8α 24 25α | .png×178 | 19/8 |  | 2 | 8 |  |  |  |  |  |  | 4 |  |  |  |
| 112 | none(5) 4 5 6α 8α 24 25α | .png×165 | 19/8 |  | 4 | 8 |  |  |  |  |  |  | 4 |  |  | trailing 77B |
| 113 | 4 5 6α 7α 8α 24 25α | .png×178 | 19/8 |  | 2 | 8 |  |  |  |  |  |  | 4 |  |  |  |
| 114 | 4 5 6α 7α 8α 24 25α | .png×186 | 19/8 |  | 4 | 8 |  |  |  |  |  |  | 4 |  |  |  |
| 115 | 4 5 6α 7α 8α 24 25α | .png×186 | 19/8 |  |  | 8 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 116 | 4 5 6α 7α 8α 24 25α | .png×178 | 19/8 |  | 2 | 8 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 349 骨 |  |  |  | 4 |  |  | trailing 97B |
| 117 | 2 4 5 6α 7α 8α 24 25α | .png×166 | 16/17 |  |  | 11 |  |  |  |  |  |  | 4 |  |  |  |
| 118 | 2 4 5 6α 7α 8α 24 25α | .png×166 | 16/17 |  |  | 11 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 350 骨 |  |  |  | 4 |  |  | trailing 97B |
| 119 | 24 25α | .png×136 | 12/4 |  |  | 13 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 528 骨 |  |  |  | 4 |  |  | trailing 73B |
| 120 | 24 25α | .png×124 | 9/4 |  |  | 13 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 465 骨 |  |  |  | 4 |  |  | trailing 73B |
| 121 | 7α 24 25α | .png×85 | 8/10 |  |  | 1 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 157 骨 |  |  |  | 4 |  |  | trailing 97B |
| 122 | 7α 24 25α | .png×145 | 11/8 |  |  | 9 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 468 骨 |  |  |  | 4 |  |  | trailing 97B |
| 123 | 7α 24 25α | .png×117 | 11/5 |  |  | 1 |  |  |  |  |  |  | 4 |  |  |  |
| 124 | 7α 24 25α | .png×117 | 11/5 |  |  | 1 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 264 骨 |  |  |  | 4 |  |  | trailing 97B |
| 125 | 3 9α 24 25α | .png×126 | 11/9 |  |  | 5 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 314 骨 |  |  |  | 4 |  |  | trailing 97B |
| 126 | 3 9α 24 25α | .png×118 | 11/9 |  |  | 5 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 207 骨 |  |  |  | 4 |  |  | trailing 97B |
| 127 | 7α 24 25α 26 | .png×173 | 19/16 |  |  | 13 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 190 骨 |  |  |  | 4 |  |  | trailing 97B |
| 128 | 5 |  |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 3 |  |  |  |
| 129 | 5 7α 38 40 | .png×73 .tga×3 .jpg×3 | 12/2 | clothes, outline |  | 1 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ | 213 骨 |  |  |  | 4 |  |  | trailing 97B |
| 132 | 38 | .png×4 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 1 |  |  | trailing 97B |
| 133 | 30 38 40 | .png×59 | 15/4 | body, suit |  | 15 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 136 | 5 7α 24 25α | .png×34 | 2/0 |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 137 | 7α 24 25α | .png×29 |  |  |  |  | 2=1,3=0,4=2,5=4 | X=R+ Y=G+ Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 140 | 5 7α | .png×10 .dds×2 | 2/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 141 | 5 7α | .png×10 .dds×1 | 2/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 142 | 5 7α | .png×7 .dds×1 | 1/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 143 | 5 7α | .png×7 .dds×1 | 1/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 144 | 5 7α | .png×9 .dds×1 | 2/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 145 | 5 7α | .png×10 .dds×1 | 3/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 146 | 5 7α | .png×9 .dds×1 | 2/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 147 | 5 | .png×15 | 3/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 148 | 5 | .png×13 | 3/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 150 | 5 | .png×16 | 6/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 151 | 5 | .png×15 | 4/1 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 153 | 5 7α | .png×13 .dds×2 | 3/3 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 157 | 5 7α | .png×13 .dds×2 | 3/3 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 161 | 5 7α | .png×13 .dds×2 | 0/3 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 164 | 5 | .png×14 | 3/0 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |
| 165 | none(5) 1 2 3 4 5 6α 7α | .png×62 |  |  |  | 4 | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  | 4802 | 2614 | 5 | 24 | 4968 | 4 |  |
| 167 | 4 6α | .jpg×19 .png×11 | 4/2 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 168 | 4 6α | .jpg×19 .png×11 | 4/2 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  | trailing 97B |
| 169 | 7α 24 25α | .png×29 |  |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  | 504 |  | 4 |  |  |  |
| 170 | 4 6α | .jpg×19 .png×11 | 4/2 |  |  |  | 2=1,3=0,4=3,5=4 | X=R+ Y=G- Z=B+ |  |  |  |  | 4 |  |  |  |

### D. 汇总

**D1. 高度分布**(唯一文件;"角色" = 找到髋骨与头骨、头骨高于髋骨、顶点 ≥ 5000、网格覆盖头骨且最低点 ≤ 0.3×髋骨高度)

- 全部唯一模型的 bbox 高度: n=147, min=0.239, P25=1.677, median=1.730, P75=1.810, max=2.129
- 角色模型 bbox 高度: n=139, min=1.519, P25=1.689, median=1.731, P75=1.815, max=2.129
- 角色模型(排除文件名含 pose 的姿势变体): n=123, min=1.519, P25=1.679, median=1.730, P75=1.796, max=2.095
- 角色模型默认可见高度(排除 `-` 默认隐藏网格): n=123, min=1.519, P25=1.679, median=1.730, P75=1.796, max=2.095
- 角色模型地面偏移 minY: n=123, min=-0.253, P25=-0.016, median=-0.003, P75=0.001, max=0.047
- 角色模型 头骨Y / bbox高度: n=123, min=0.705, P25=0.854, median=0.880, P75=0.893, max=0.927
- 角色模型 髋骨Y / bbox高度: n=123, min=0.436, P25=0.551, median=0.576, P75=0.585, max=0.671
- 角色模型 骨架高度(骨骼 head Y 极差): n=123, min=1.513, P25=1.629, median=1.667, P75=1.704, max=25.936
- 角色模型 头骨 Y(绝对值): n=123, min=1.388, P25=1.488, median=1.528, P75=1.544, max=1.880
- 角色模型 髋骨 Y(绝对值): n=123, min=0.860, P25=0.950, median=0.993, P75=1.019, max=1.406
- 角色模型 bbox高度 − 头骨Y(头骨以上的网格,含发型/帽子/耳朵等): n=123, min=0.039, P25=0.178, median=0.193, P75=0.240, max=0.512
- bbox 最矮 5 个: #37 alana (flame falcon) H=1.519 头骨Y=1.396; #54 phoenix (naked) H=1.542 头骨Y=1.388; #39 alana (naked) H=1.544 头骨Y=1.393; #36 alana (blackwing ★ noir) H=1.583 头骨Y=1.391; #20 alana (archdemon baal) H=1.585 头骨Y=1.391
- bbox 最高 5 个: #41 alana (steelhare) H=1.973 头骨Y=1.391; #10 rouffe (maiden flora) H=1.988 头骨Y=1.537; #98 Divine Grace (Lynn) H=1.999 头骨Y=1.633; #5 inase (blesser) H=2.055 头骨Y=1.543; #104 One Punch Man Fubuki by Animanpower H=2.095 头骨Y=1.880
- 非角色(道具/部件/无骨架)共 8 个: #1 #Stellar Blade - Eve (Cooling)/hair.ascii (H=1.265, bones=354); #7 weapon/xps.xps (H=0.877, bones=1); #24 shield/xps.xps (H=0.981, bones=1); #25 sword/xps.xps (H=1.557, bones=1); #27 staff/xps.xps (H=0.239, bones=1); #85 Cooling Suit crazy/Stellar Blade - Eve (Cooling Suit).xps (H=1.516, bones=579); #101 Jill Gantz/pl2000.meshout.mesh.ascii (H=1.447, bones=191); #132 Gantz Reika suit V2/Knife.mesh (H=1.241, bones=1)

**D2. 骨骼命名约定**(唯一文件)

顶层分类: `xnalara_generic` 109, `other` 21, `daz_g8` 17(共 147 个唯一文件)

| 约定 | 数量 | 文件 # |
|---|---|---|
| xnalara_generic | 109 | 1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15, 20, 21, 22, 23, 26, 34, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 74, 76, 78, 79, 81, 87, 88, 89, 94, 95, 96, 99, 103, 104, 106, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 129, 133, 136, 137, 140, 141, 142, 143, 144, 145, 146, 147, 148, 150, 151, 153, 157, 161, 164, 169 |
| daz_g8 | 13 | 16, 17, 18, 19, 82, 83, 90, 91, 92, 93, 167, 168, 170 |
| prop(<=3 bones) | 5 | 7, 24, 25, 27, 132 |
| other:auto_rig_pro | 4 | 30, 31, 105, 165 |
| daz_g8+xnalara_generic | 4 | 32, 33, 97, 98 |
| other:3dsmax_biped | 4 | 61, 84, 85, 86 |
| other:lr_prefix | 3 | 28, 29, 107 |
| other:re_engine | 3 | 100, 101, 102 |
| other:unreal | 1 | 11 |
| other:valve_biped | 1 | 128 |

**D3. 全语料使用的渲染组**(按网格计数,唯一文件)

| RG | alpha | 贴图槽 | 光照 | 使用该 RG 的模型数 | 网格数 |
|---|---|---|---|---|---|
| 1 | 否 | diffuse, lightmap, bump, mask, bump1, bump2 | lit | 1 | 2 |
| 2 | 否 | diffuse, lightmap, bump | lit | 4 | 10 |
| 3 | 否 | diffuse, lightmap | lit | 3 | 5 |
| 4 | 否 | diffuse, bump | lit | 38 | 403 |
| 5 | 否 | diffuse | lit | 42 | 373 |
| 6 | 是 | diffuse, bump | lit | 35 | 138 |
| 7 | 是 | diffuse | lit | 95 | 142 |
| 8 | 是 | diffuse, lightmap, bump | lit | 8 | 30 |
| 9 | 是 | diffuse, lightmap | lit | 2 | 2 |
| 22 | 否 | diffuse, lightmap, bump, mask, bump1, bump2, specular | lit | 9 | 38 |
| 23 | 是 | diffuse, lightmap, bump, mask, bump1, bump2, specular | lit | 2 | 4 |
| 24 | 否 | diffuse, lightmap, bump, specular | lit | 89 | 770 |
| 25 | 是 | diffuse, lightmap, bump, specular | lit | 80 | 420 |
| 26 | 否 | diffuse, bump, environment, mask | lit/unlit | 6 | 14 |
| 27 | 是 | diffuse, bump, environment, mask | lit/unlit | 11 | 98 |
| 28 | 否 | diffuse, bump, mask, bump1, bump2, environment | lit/unlit | 1 | 1 |
| 29 | 是 | diffuse, bump, mask, bump1, bump2, environment | lit/unlit | 3 | 5 |
| 30 | 否 | diffuse, bump, emission | lit/unlit | 2 | 2 |
| 31 | 是 | diffuse, bump, emission | lit/unlit | 3 | 9 |
| 38 | 否 | diffuse, bump, specular, emission | lit/unlit | 17 | 31 |
| 39 | 是 | diffuse, bump, specular, emission | lit/unlit | 1 | 1 |
| 40 | 否 | diffuse, bump, specular | lit | 14 | 109 |
| 41 | 是 | diffuse, bump, specular | lit | 8 | 39 |
| 无前缀(按 5) | 否 | diffuse | lit | 2 | 11 |

**D4. 版本 / 布局直方图**(唯一文件)

| 格式 | 版本 | 顶点布局 | 数量 |
|---|---|---|---|
| bin | 3.15 | notan+varw | 68 |
| bin | 2.15 | notan+w4 | 64 |
| ascii | no header | notan+w4 | 10 |
| bin | no header | tan+w4 | 3 |
| ascii | no header | notan+varw | 2 |

**D5. 权重、可选项、命名细节**(唯一文件)

- 有顶点权重和 > 1.01 的模型: 5 / 147(顶点合计 28832)
- 有顶点权重和 < 0.99(非零)的模型: 6;有全零权重顶点的模型: 1
- 有 > 4 个非零影响顶点的模型: 7(最大影响数分布: {1: 5, 3: 4, 4: 131, 8: 2, 9: 1, 11: 1, 24: 1, 33: 2})
- 含可选项(+/−)的模型: 108;使用 `|` 分组的模型: 21
- 含 nPart 分片网格的模型: 6;网格名以 Blender 式 `.00N` 结尾的模型: 35
- 含 `unused*` 骨骼的模型: 99
- 骨骼/网格/贴图名含非 ASCII 字符的模型: 2(#2: Degradê Cinza 5C.png; #86: Rootì†Œì¼“)
- 头部嵌入默认姿势(settings type 1 长度>0)的模型: 20
- 二进制文件 flags 组合: `2=1,3=0,4=3,5=4` ×105; `2=1,3=0,4=2,5=4` ×27; `(无 / 旧格式)` ×3
- settings 条目序列: `[(1, 0, 0), (2, 4, 4), (0, 256, 0)]` ×94; `[(1, 0, 243), (2, 4, 4), (0, 256, 0)]` ×2; `[(1, 0, 192), (2, 4, 4), (0, 256, 0)]` ×2; `[(1, 0, 241), (2, 4, 4), (0, 256, 0)]` ×2; `[(1, 0, 275), (2, 4, 4), (0, 256, 0)]` ×2; `[(1, 11941, 305), (2, 4, 4), (0, 256, 0)]` ×2; `[(1, 0, 250), (2, 4, 4), (0, 256, 0)]` ×2; `[(1, 0, 177), (2, 4, 4), (0, 256, 0)]` ×2; `[(1, 0, 138), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 18325, 482), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 31718, 731), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 0, 263), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 0, 414), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 0, 399), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 0, 239), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 11390, 294), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 26522, 725), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 7864, 217), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 17209, 499), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 6482, 171), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 0, 630), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 13230, 349), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 13267, 350), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 20410, 528), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 17944, 465), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 5760, 157), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 17922, 468), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 9898, 264), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 11455, 314), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 7686, 207), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 7092, 190), (2, 4, 4), (0, 256, 0)]` ×1; `[(1, 8249, 213), (2, 4, 4), (0, 256, 0)]` ×1
- 警告类型: trailing NB ×103
- 尾随字节长度分布: {73: 2, 77: 1, 97: 100}
- validate_model 问题: 19 条,涉及 5 个模型(权重和>1 的条目也计入)

**D6. 解析失败 / 跳过**

- 无

**D7. `.pose` 文件**(load_pose 解析检查)

- day_work/mmd/aya_sitting_down_pose/ayasettingsmile.pose: 211 条骨骼
- day_work/mmd/doa_mai_pose_pack_1_by_marcelievsky_db3mqzs/DOA Mai hit 1.pose: 379 条骨骼
- day_work/mmd/doa_mai_pose_pack_1_by_marcelievsky_db3mqzs/DOA Mai punch 1.pose: 379 条骨骼
- day_work/work/gantz/already/DOA-Shimohira Reika/default.pose: 482 条骨骼
- day_work/work3/Reika_Tropical_Bikini_by_SSPD077/Reika_Tropical_Bikini_by_SSPD077/default.pose: 305 条骨骼
- day_work/work5/Reika_Shimohira_by_SSPD077/Reika_Shimohira_by_SSPD077/default.pose: 305 条骨骼
- day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/default.pose: 349 条骨骼
- day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Asagi_Igawa_by_SSPD077/default.pose: 350 条骨骼
- day_work/work5/Taimanin_Asagi_Beta_Pack_by_SSPD077/Oboro_by_SSPD077/default.pose: 264 条骨骼
- 4090/tifa/change/Misaki (Cumin Wear)/default.pose: 312 条骨骼

**D8. 同目录已有 PMX 的 XPS 文件**(PMX 顶点 bbox 高度 ÷ XPS bbox 高度 = 既有转换所用的缩放系数)

| # | XPS 文件(每目录取一个) | XPS bbox 高度 | 头骨 Y | PMX 文件 | PMX bbox 高度 | PMX/XPS |
|---|---|---|---|---|---|---|
| 10 | day_work/work/Reika/rouffe (maiden flora)/xps.xps | 1.988 | 1.537 | rouffe.pmx | 19.884 | 10.00 |
| 10 | day_work/work/Reika/rouffe (maiden flora)/xps.xps | 1.988 | 1.537 | rouffe_finnal.pmx | 24.855 | 12.50 |
| 20 | day_work/work/model/alana (archdemon baal)/xps.xps | 1.585 | 1.391 | alana.pmx | 19.815 | 12.50 |
| 20 | day_work/work/model/alana (archdemon baal)/xps.xps | 1.585 | 1.391 | alana_bone_l_g2_final.pmx | 19.815 | 12.50 |
| 20 | day_work/work/model/alana (archdemon baal)/xps.xps | 1.585 | 1.391 | alana_bone_l_g2_final2.pmx | 19.815 | 12.50 |
| 20 | day_work/work/model/alana (archdemon baal)/xps.xps | 1.585 | 1.391 | alana_bone_l_g2_final3.pmx | 19.815 | 12.50 |
| 33 | day_work/work/riseoferos/Super Moon (Misaki)- Rise Of Eros/xps.xps | 1.872 | 1.597 | normal pose_new.pmx | 18.668 | 9.97 |
| 34 | day_work/work/riseoferos/alana (aberrant corpse)/xps.xps | 1.634 | 1.391 | xps_new.pmx | 16.344 | 10.00 |
| 36 | day_work/work/riseoferos/alana (blackwing ★ noir)/xps.xps | 1.583 | 1.391 | xps_new.pmx | 15.834 | 10.00 |
| 42 | day_work/work/riseoferos/alana (tempting tidings)/xps.xps | 1.658 | 1.391 | xps_new.pmx | 16.576 | 10.00 |
| 43 | day_work/work/riseoferos/cartilla (denim hotpants)/xps.xps | 1.753 | 1.564 | xps_new.pmx | 17.529 | 10.00 |
| 44 | day_work/work/riseoferos/cartilla (holy slayer)/xps.xps | 1.832 | 1.537 | xps_new.pmx | 18.319 | 10.00 |
| 45 | day_work/work/riseoferos/eileen (deep sea diva)/xps.xps | 1.716 | 1.527 | xps_new.pmx | 17.165 | 10.00 |
| 46 | day_work/work/riseoferos/eileen (frostblossom)/xps.xps | 1.737 | 1.539 | xps_new.pmx | 17.366 | 10.00 |
| 47 | day_work/work/riseoferos/inase (goddess of envy invidia)/xps.xps | 1.760 | 1.543 | xps_new.pmx | 17.601 | 10.00 |
| 48 | day_work/work/riseoferos/inase (naked)/inase (naked)/xps.xps | 1.718 | 1.545 | xps_new.pmx | 17.183 | 10.00 |
| 49 | day_work/work/riseoferos/inase (purifier)/xps.xps | 1.749 | 1.544 | xps_new.pmx | 17.494 | 10.00 |
| 50 | day_work/work/riseoferos/lynn (flight attendant)/xps.xps | 1.727 | 1.528 | xps_new.pmx | 17.273 | 10.00 |
| 51 | day_work/work/riseoferos/lynn (furious pirate)/xps.xps | 1.865 | 1.528 | xps_new.pmx | 18.653 | 10.00 |
| 52 | day_work/work/riseoferos/misaki 02/xps.xps | 1.810 | 1.595 | xps_new.pmx | 18.104 | 10.00 |
| 53 | day_work/work/riseoferos/pc_a02_ld/xps.xps | 1.736 | 1.556 | xps_new.pmx | 17.363 | 10.00 |
| 54 | day_work/work/riseoferos/phoenix (naked)/phoenix (naked)/xps.xps | 1.542 | 1.388 | xps_new.pmx | 15.417 | 10.00 |
| 55 | day_work/work/riseoferos/rouffe (empress of snows)/xps.xps | 1.798 | 1.537 | xps_new.pmx | 17.978 | 10.00 |
| 56 | day_work/work/riseoferos/rouffe (enchanting coach)/xps.xps | 1.713 | 1.541 | xps_new.pmx | 17.131 | 10.00 |
| 57 | day_work/work/riseoferos/rouffe (glistening grace)/xps.xps | 1.765 | 1.537 | xps_new.pmx | 17.650 | 10.00 |
| 58 | day_work/work/riseoferos/rouffe (goddess of love aphrodite)/xps.xps | 1.801 | 1.537 | xps_new.pmx | 18.006 | 10.00 |
| 59 | day_work/work/riseoferos/rouffe (inked gold)/xps.xps | 1.712 | 1.537 | xps_new.pmx | 17.116 | 10.00 |
| 61 | day_work/work/riseoferos/rouffe (naked)/rouffe (naked)/rouffe.mesh.ascii | 1.706 | 1.541 | rouffe_new.pmx | 17.055 | 10.00 |
| 63 | day_work/work/riseoferos/rouffe (obsidian armor)/xps.xps | 1.731 | 1.537 | xps_new.pmx | 17.308 | 10.00 |
| 64 | day_work/work/riseoferos/rouffe (pasionate gift)/xps.xps | 1.765 | 1.537 | xps_new.pmx | 17.655 | 10.00 |
| 65 | day_work/work/riseoferos/rouffe (sash)/xps.xps | 1.742 | 1.537 | xps_new.pmx | 17.415 | 10.00 |
| 66 | day_work/work/riseoferos/rouffe (tigerstripe)/xps.xps | 1.829 | 1.537 | rouffe.pmx | 18.295 | 10.00 |
| 66 | day_work/work/riseoferos/rouffe (tigerstripe)/xps.xps | 1.829 | 1.537 | xps_new.pmx | 18.295 | 10.00 |
| 67 | day_work/work/riseoferos/rouffe (virgin killer)/xps.xps | 1.714 | 1.541 | vk10.pmx | 17.142 | 10.00 |
| 67 | day_work/work/riseoferos/rouffe (virgin killer)/xps.xps | 1.714 | 1.541 | xps_new.pmx | 17.142 | 10.00 |
| 69 | day_work/work/riseoferos2/cartilla (pure white love song)_pmx/xps.xps | 1.940 | 1.538 | cartilla (pure white love song).pmx | 19.400 | 10.00 |
| 69 | day_work/work/riseoferos2/cartilla (pure white love song)_pmx/xps.xps | 1.940 | 1.538 | cartilla_pure.pmx | 24.249 | 12.50 |
| 69 | day_work/work/riseoferos2/cartilla (pure white love song)_pmx/xps.xps | 1.940 | 1.538 | xps_new.pmx | 19.399 | 10.00 |
| 71 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps.xps | 1.737 | 1.537 | cartilla (tombshadow).pmx | 17.367 | 10.00 |
| 71 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps.xps | 1.737 | 1.537 | cartilla.pmx | 1.737 | 1.00 |
| 71 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps.xps | 1.737 | 1.537 | cartilla_413_12.5.pmx | 21.708 | 12.50 |
| 71 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps.xps | 1.737 | 1.537 | cartilla_bones_new.pmx | 21.708 | 12.50 |
| 71 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps.xps | 1.737 | 1.537 | test50413_2.pmx | 21.708 | 12.50 |
| 71 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx2/xps.xps | 1.737 | 1.537 | xps_new.pmx | 17.367 | 10.00 |
| 72 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx3/normal pose.xps | 1.737 | 1.537 | cartilla413.pmx | 21.708 | 12.50 |
| 72 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx3/normal pose.xps | 1.737 | 1.537 | cartilla413_standbone_lie_body.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla419.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla419_bone_lie_r2_body.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla419_bone_lie_r2_body_r.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla420_bone_lie_r3_body.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla420_bone_lie_r3_body2.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla420_bone_lie_r3_body3.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla420_bone_lie_r3_body4.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla_bone_lier2_gang_body.pmx | 21.708 | 12.50 |
| 74 | day_work/work/riseoferos2/cartilla (tombshadow)_pmx5/normal pose.xps | 1.737 | 1.537 | cartilla_bone_lier2_gang_body2.pmx | 21.708 | 12.50 |
| 76 | day_work/work/riseoferos2/inase (arbiter)_pmx/normal pose.xps | 1.722 | 1.544 | arbiter_nomal.pmx | 21.530 | 12.50 |
| 76 | day_work/work/riseoferos2/inase (arbiter)_pmx/normal pose.xps | 1.722 | 1.544 | inase_arbiter.pmx | 17.224 | 10.00 |
| 76 | day_work/work/riseoferos2/inase (arbiter)_pmx/normal pose.xps | 1.722 | 1.544 | normal pose_new.pmx | 17.224 | 10.00 |
| 76 | day_work/work/riseoferos2/inase (arbiter)_pmx/normal pose.xps | 1.722 | 1.544 | xps_new.pmx | 17.224 | 10.00 |
| 78 | day_work/work/riseoferos2/inase (auditioner)/xps.xps | 1.724 | 1.544 | xps_new.pmx | 17.239 | 10.00 |
| 79 | day_work/work/riseoferos2/inase (heart stealer)/xps.xps | 1.750 | 1.545 | xps_new.pmx | 17.500 | 10.00 |
| 81 | day_work/work/riseoferos2/inase (nightcrawler)_pmx/xps.xps | 1.722 | 1.544 | inase (nightcrawler).pmx | 17.225 | 10.00 |
| 81 | day_work/work/riseoferos2/inase (nightcrawler)_pmx/xps.xps | 1.722 | 1.544 | xps_new.pmx | 17.225 | 10.00 |
| 87 | day_work/work11(model)/keleira (vespermas star)/xps.xps | 1.767 | 1.530 | keleira.pmx | 17.666 | 10.00 |
| 87 | day_work/work11(model)/keleira (vespermas star)/xps.xps | 1.767 | 1.530 | keleira0.1.pmx | 1.767 | 1.00 |
| 94 | day_work/work3/Reika_Tropical_Bikini_by_SSPD077/Reika_Tropical_Bikini_by_SSPD077/Generic_Item.mesh.ascii | 1.632 | 1.394 | reika.pmx | 16.582 | 10.16 |
| 106 | day_work/work5/Lisa gantz hairstyle 2/xps.xps | 1.658 | 1.482 | lisa.pmx | 21.059 | 12.70 |
| 106 | day_work/work5/Lisa gantz hairstyle 2/xps.xps | 1.658 | 1.482 | xps_new.pmx | 16.581 | 10.00 |
| 108 | day_work/work5/Reika_Shimohira_by_SSPD077/Reika_Shimohira_by_SSPD077/Generic_Item.mesh.ascii | 1.648 | 1.394 | Generic_Item_new.pmx | 16.715 | 10.14 |
| 111 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/1.mesh.ascii | 1.674 | 1.495 | asagi.pmx | 17.088 | 10.21 |
| 111 | day_work/work5/Taimanin_Asagi_Asagi_Igawa_by_SSPD077/Asagi_Igawa_by_SSSPD077/1.mesh.ascii | 1.674 | 1.495 | finalasagi_new.pmx | 17.088 | 10.21 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 None.pmx | 20.963 | 12.52 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V1.pmx | 20.913 | 12.49 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V2.pmx | 20.933 | 12.50 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V3.pmx | 20.772 | 12.40 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V4.pmx | 20.929 | 12.50 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V5.pmx | 20.917 | 12.49 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V6.pmx | 20.907 | 12.48 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V7.pmx | 20.964 | 12.52 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party 18 V8.pmx | 21.120 | 12.61 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party Children.pmx | 20.690 | 12.35 |
| 128 | day_work/work6/Diana Burnwood Dress Party 18/clothes hitman party2.xps | 1.675 | 1.553 | Diana Burnwood Dress Party Inase.pmx | 21.178 | 12.65 |
| 129 | day_work/work6/Wonder Woman Movie by Mokujin Hornywood Default by Animanpower/xps.xps | 1.971 | 1.689 | Wonder.pmx | 18.886 | 9.58 |
| 129 | day_work/work6/Wonder Woman Movie by Mokujin Hornywood Default by Animanpower/xps.xps | 1.971 | 1.689 | Wonder_Inase.pmx | 19.159 | 9.72 |
| 136 | day_work/work7/lynn (deathblossom)/xps.xps | 1.701 | 1.528 | lynn12.pmx | 20.418 | 12.00 |
| 137 | day_work/work7/misaki (mooncaller)/xps.xps | 1.865 | 1.634 | misaki.pmx | 23.310 | 12.50 |
| 169 | mywork/add_on/inase (purifier)_lezisell-A/xps.xps | 1.749 | 1.571 | 329-1.pmx | 21.867 | 12.50 |
| 169 | mywork/add_on/inase (purifier)_lezisell-A/xps.xps | 1.749 | 1.571 | 329.pmx | 21.867 | 12.50 |
| 170 | mywork/mymodel/Purifier (Inase)/xps-A.xps | 1.907 | 1.630 | 329_converted.pmx | 1.907 | 1.00 |

- PMX/XPS 比值(每个 PMX 文件计一次,共 89 个): ×10: 43, ×12.5: 31, ×1: 3, ×10.2: 3, ×12.4: 2, ×12.6: 2, ×12.7: 1, ×10.1: 1, ×9.6: 1, ×9.7: 1, ×12: 1
- 比值统计: n=89, min=1.00, P25=10.00, median=10.00, P75=12.50, max=12.70
- 仅骨骼(0 顶点)或无法读取、未计入比值的 PMX: #10: maiden flora_bones.pmx, maiden flora_bones_wan.pmx, maiden flora_bones_wan_naibone.pmx, maiden flora_bones_wan_naibone_gang.pmx; #20: alana_bone.pmx, alana_bone_l_g.pmx, alana_bone_l_g2.pmx; #69: cartilla_pure_bone.pmx; #71: cartilla2.pmx, cartilla3.pmx, cartilla_413_12.5_standbone.pmx, cartilla_413_12.5_standbone_lie.pmx, cartilla_bones.pmx, cartilla_bones_lie.pmx; #72: cartilla413_standbone.pmx, cartilla413_standbone_lie.pmx; #74: cartilla419_bone.pmx, cartilla419_bone_lie.pmx, cartilla419_bone_lie_r.pmx, cartilla419_bone_lie_r2.pmx, cartilla419_lie.pmx, cartilla420_bone.pmx, cartilla420_bone_lie.pmx, cartilla420_bone_lie_r.pmx, cartilla420_bone_lie_r2.pmx, cartilla420_bone_lie_r3.pmx, cartilla_bone.pmx, cartilla_bone_lier.pmx, cartilla_bone_lier2.pmx, cartilla_bone_lier2_gang.pmx; #76: arbiter_normal_bonse.pmx, arbiter_normal_bonse12.5.pmx, arbiter_normal_bonse12.5_lie.pmx

<!-- END GENERATED -->
