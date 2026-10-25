# XPS / XNALara 模型格式与 Blender 导入侧调研

> 调研日期:2026-10-24。本文是 "XPS → PMX" Blender 插件方案的格式/导入侧基础笔记。
>
> **本地源码路径缩写**(下文引用均以缩写开头):
> - `XNALaraMesh/` = `C:\Users\haoni\AppData\Roaming\Blender Foundation\Blender\4.5\scripts\addons\XNALaraMesh\`(johnzero7 XPS Tools 2.0.2,`__init__.py` `bl_info` version (2,0,2),部分文件带本机改动,见第 7 节)
> - `b2xps_addon/` = `C:\Users\haoni\AppData\Roaming\Blender Foundation\Blender\4.5\scripts\addons\b2xps_addon\`(B2XPS 1.1.0)
>
> 引用写法 `XNALaraMesh/read_bin_xps.py::readHeader` 表示该文件中的函数。

---

## 1. XPS/XNALara 文件格式:.mesh.ascii / .mesh / .xps 的精确布局、版本分支、编码与上限

### Takeaway
XPS 三种容器共享同一套"骨骼表 + 网格表"数据模型;`.xps` 多一个以 magic `323232` 开头的头部(含版本号、settings 块、可选默认姿势与渲染 flags)。导入器只在两件事上按版本分支:(1) 是否每个 UV 层后跟一个 float4 切线(有头部且 version ≤ 2.12,或无头部的 `.mesh`,则有切线);(2) 每顶点骨骼权重是固定 4 个还是变长(有头部且 major ≥ 3 则变长,前置 int16 计数)。字符串为 .NET 风格 7‑bit 变长长度前缀 + UTF‑8;骨骼索引/父索引为 int16,面索引为 uint32。

### Cited Findings

**容器与头部检测**
- 导入入口按扩展名分流:`.mesh`/`.xps` → 二进制读取器,`.ascii` → 文本读取器,其他返回 `None`(报 "File Format unrecognized")— `XNALaraMesh/import_xnalara_model.py::loadXpsFile`,`XNALaraMesh/xps_tools.py::Import_Xps_Model_Op.execute`
- 二进制读取不靠扩展名判断是否有头部,而是读文件头 4 字节 uint32 与 `MAGIC_NUMBER = 323232` 比较,相等才解析头部,否则 `header=None` 直接从骨骼表开始 — `XNALaraMesh/read_bin_xps.py::findHeader`,`XNALaraMesh/xps_const.py`
- 常量:`XPS_VERSION_MAYOR = 3`,`XPS_VERSION_MINOR = 15`,`XNA_ARAL = 'XNAaraL'`,`SETTINGS_LEN = 1080`,`LIMIT = 128`,`STRLEN = 275`,`ROUND_MULTIPLE = 4`,`ENCODING_READ = 'utf-8-sig'`,`ENCODING_WRITE = 'utf-8'` — `XNALaraMesh/xps_const.py`
- 所有数值为小端(`struct` 格式 `'<B' '<h' '<H' '<I' '<f'`)— `XNALaraMesh/bin_ops.py::TypeFormat`
- 字符串长度前缀:先读 1 字节 `b1`;若 `b1 >= 128` 再读 `b2`;`length = (b1 % 128) + b2 * 128`;随后读 `length` 字节并按 `utf-8-sig` 解码 — `XNALaraMesh/read_bin_xps.py::readFilesString`,`XNALaraMesh/bin_ops.py::readString/decodeBytes`
- B2XPS 对同一规则的独立描述:"7-bit variable-length encoding (.NET BinaryReader style)",长度 < 128 写 1 字节,否则写 `[length % 128 + 128, length // 128]` — `b2xps_addon/writer.py::_write_string`

**`.xps` 头部布局(按读取顺序)**

| 顺序 | 字段 | 类型 | 说明 | 来源 |
|---|---|---|---|---|
| 1 | `magic_number` | uint32 | 固定 `323232` | `read_bin_xps.py::readHeader` |
| 2 | `version_mayor` | uint16 | 写出时为 3(或导出选项 V2) | 同上;`xps_tools.py::Export_Xps_Model_Op.xps_version_mayor` |
| 3 | `version_minor` | uint16 | 写出时为 15 | 同上 |
| 4 | `xna_aral` | 变长字符串 | 固定 `"XNAaraL"` | 同上 |
| 5 | `settingsLen` | uint32 | settings 块长度,单位是 **uint32 个数**(读取时 `settingsLen * 4` 字节) | `readHeader`;写入注释 "Settings Len (unit32*4)" `write_bin_xps.py::writeHeader` |
| 6 | `machineName` | 变长字符串 | 机器名 | `readHeader` |
| 7 | `userName` | 变长字符串 | 用户名 | 同上 |
| 8 | `files` | 变长字符串 | 源文件信息 | 同上 |
| 9 | settings 块 | `settingsLen*4` 字节 | 旧格式(有切线版本)整块跳过;新格式按下表解析 | 同上 |

- settings 块新格式解析:先读 `hash`(uint32)、`items`(uint32),然后循环 `items` 次读 `(optType, optcount, optInfo)` 三个 uint32:`optType==0` → 跳过 `optcount` 个 uint32;`optType==1` → 默认姿势:`optcount` = 姿势文本未对齐字节长度,`optInfo` = 骨骼行数,按行读取 `.pose` 文本后把长度向上取整到 4 的倍数并吃掉填充;`optType==2` → flags:读 `optcount` 对 `(flag uint32, value uint32)`;其他类型 → 把剩余到 `settingsLen` 的字全部当作 waste 读掉 — `XNALaraMesh/read_bin_xps.py::readHeader/readNone/readDefaultPose/readFlags`
- 写入侧(mock 数据)可见的 settings 布局:`hash=180`,`items=3`,`type=1` + `poseLength` + `boneCount` + 姿势字节;随后 `type=2, count=4, info=4` 以及一串 flag 值 `2,1,3,0`、`4,3,5,4,0,256`,其余补零;最终 `settingsLen = len(settings)//4` — `XNALaraMesh/mock_xps_data.py::buildHeader`;B2XPS 同样写 `275` 个 uint32(1100 字节),`hash=180, items=3, type=1`,接 `0,0`(pose length, bone count)和 `2,4,4,2,1,3,0,4,3,5,4,0,256`,其余补零 — `b2xps_addon/writer.py::_write_header`
- flags 编号与默认值:`0 backFaceCulling=False`,`1 alwaysForceCulling=False`,`2 modelCastShadows=True`,`3/4/5 TangentSpaceRed/Green/Blue = 0/1/0`(即法线贴图通道 swizzle `X+ Y- Z+`,取 `value % 2`),`6 gloss=10`,`7 hasBoneDirections=False`;flag 0/1/2/6/7 转 bool,3/4/5 取 `value % 2` — `XNALaraMesh/read_bin_xps.py::flagName/flagsDefault/flagValue/printNormalMapSwizzel`,`XNALaraMesh/xps_const.py`
- `hasBoneDirections`(flag 7)在整个读取器中**只作为 flag 被记录**,没有任何读取骨骼方向/尾部数据的代码;上游 master 的 `read_bin_xps.py` 同样如此 — 本地 `XNALaraMesh/read_bin_xps.py`;[johnzero7/XNALaraMesh master read_bin_xps.py](https://raw.githubusercontent.com/johnzero7/XNALaraMesh/master/read_bin_xps.py)

**版本分支函数**

| 判断 | 有头部(.xps) | 无头部(.mesh) | 来源 |
|---|---|---|---|
| `hasTangentVersion` | `verMinor <= 12 and verMayor <= 2` | 恒 `True` | `XNALaraMesh/bin_ops.py::hasTangentVersion` |
| `hasVariableWeights` | `verMayor >= 3` | 恒 `False` | `XNALaraMesh/bin_ops.py::hasVariableWeights` |
| `hasHeader` | 按导出格式字符串 `== '.xps'` | — | `XNALaraMesh/bin_ops.py::hasHeader` |

- 读取网格时若文件无头部,`verMayor/verMinor` 取 0 并把 `hasHeader=False` 传入上述函数 — `XNALaraMesh/read_bin_xps.py::readMeshes`
- 导出器 UI:`.xps` 可选 `V3`("Supports Unlimited Bone Weights (compatibli with XPS 1.8.9)")或 `V2`("Supports 4 Bone Weights");minor 固定 `15`;`.mesh`/`.ascii` 无此选项 — `XNALaraMesh/xps_tools.py::Export_Xps_Model_Op`
- XPS 官方发布说明(XPS 11.8.9,2020‑02‑20):权重 ≤ 4 的模型保存为 "XPS 2.x format",可被旧版 XPS、Blender、3ds Max 读取;"Only if the model has more than 4 weights per vertex, then the model must be be saved as XPS Format 3.x (and required 11.8.9 or higher to support up to 32k bones per vertex)" — [xnalara.forumotion.com XPS 11.8.9 release 189](https://xnalara.forumotion.com/t327-xna-posing-studio-11-8-9-view-mode-edition-release-189)

**骨骼表与网格表(二进制,.mesh 与 .xps 相同)**

| 区块 | 字段 | 类型 | 备注 | 来源 |
|---|---|---|---|---|
| Bones | `boneCount` | uint32 | | `read_bin_xps.py::readBones` |
| 每骨骼 | `name` | 变长字符串 | | 同上 |
| | `parentId` | **int16**(有符号) | `-1` 表示无父;导入时 `parentId >= 0` 才设父 | 同上;`import_xnalara_model.py::importBones` |
| | `position` | float32 ×3 | 仅 head 位置,无尾部/无 roll | 同上 |
| Meshes | `meshCount` | uint32 | | `read_bin_xps.py::readMeshes` |
| 每网格 | `name` | 变长字符串 | 空名 → `'unnamed'`(ASCII 读取器用 `'xxx'`) | 同上;`read_ascii_xps.py::readMeshes` |
| | `uvLayerCount` | uint32 | | 同上 |
| | `textureCount` | uint32 | | 同上 |
| 每贴图 | `file` | 变长字符串 | 读取时取 `ntpath.basename` | 同上 |
| | `uvLayerId` | uint32 | 该贴图使用的 UV 层索引 | 同上 |
| | `vertexCount` | uint32 | | 同上 |
| 每顶点 | `position` | float32 ×3 | | 同上 |
| | `normal` | float32 ×3 | | 同上 |
| | `color` | uint8 ×4 (RGBA) | | `readVertexColor` |
| | 每 UV 层:`uv` | float32 ×2 | 紧跟其后若 `hasTangent` 则 `tangent` float32 ×4(**每个 UV 层各一个**) | `readMeshes` 循环体 |
| | 权重计数 | int16(仅 `hasVariableWeights`) | 否则固定 4 | 同上 |
| | 骨骼索引 | int16 ×N | 先全部索引 | 同上 |
| | 权重 | float32 ×N | 后全部权重 | 同上 |
| | `triCount` | uint32 | | 同上 |
| 每三角 | 索引 | **uint32 ×3** | | `readTriIdxs` |

- 若骨骼表为空(`boneCount == 0`),顶点中**不存在**索引/权重字段(`hasBones=False`)— `XNALaraMesh/read_bin_xps.py::readXpsModel/readMeshes`
- 写出侧:权重按从大到小排序后写出;V3 变长时写 uint16 计数 + uint16 索引 + float 权重;固定 4 时用 `write4UInt16`(实际用 `writeInt16`)和 `write4Float`;有切线版本写占位切线 `[1,0,0,0]` — `XNALaraMesh/write_bin_xps.py::writeMeshes/write4UInt16`;B2XPS 写骨骼索引用 `'<H'`/`'<4H'`(无符号) — `b2xps_addon/writer.py::_write_model_data`

**`.mesh.ascii` 文本布局**
- 按行读取;`#` 之后为注释(`ignoreComment` / `splitValues` 把 `#` 替换为空格再 split);文件以 `utf-8-sig` 打开 — `XNALaraMesh/ascii_ops.py`,`XNALaraMesh/read_ascii_xps.py::readIoStream`
- 顺序:`boneCount` → 每骨骼 `name` 行、`parentId` 行、`x y z` 行 → `meshCount` → 每网格 `name`、`uvCount`、`texCount`、每贴图 `filename` 行 + `uvLayer` 行、`vertexCount`、每顶点 `pos` 行、`normal` 行、`r g b a` 四整数行、每 UV 层 `u v` 行、(有骨骼时)`骨骼索引` 行、`权重` 行 → `faceCount` → 每面 `i0 i1 i2` — `XNALaraMesh/read_ascii_xps.py::readBones/readMeshes`
- ASCII 读取器**不读切线**(源码中 `# tangent????` 被注释掉);索引/权重行用 `fillArray(values, 4, 0)` 补齐到至少 4 个值,多于 4 个也会全部读入 — `XNALaraMesh/read_ascii_xps.py::readMeshes/readBoneId/readBoneWeight`
- ASCII 写出器:索引行与权重行各一行、按权重降序、注释如 `{:d} # faces` — `XNALaraMesh/write_ascii_xps.py`

**`.pose` 文本格式**
- 每行 `boneName: rx ry rz tx ty tz sx sy sz`(以 `:` 分割骨名与数据,数据用空格分割,不足 9 个用 1 补齐;前三项旋转、中三项平移、后三项缩放)— `XNALaraMesh/read_ascii_xps.py::poseData`;写出时旋转保留 1 位小数、平移 4 位、缩放 3 位 — `XNALaraMesh/write_ascii_xps.py::writePose/roundRot/roundTrans/roundScale`
- 头部中内嵌的默认姿势就是这段文本(按行 `readline()` 读 `poseBones` 行后解析)— `XNALaraMesh/read_bin_xps.py::readDefaultPose`

### Inferences
- 骨骼索引用 int16 读取,与 XPS 公告的 "up to 32k bones" 一致:格式上单文件最多 32767 根可被顶点引用的骨骼(B2XPS 以无符号写出,理论 65535,但与 XNALaraMesh 读取器不一致,超过 32767 会读成负数)。
- 面索引为 uint32,格式本身没有 65535 顶点/网格的限制;网格拆分(`nPart!`,见第 3 节)应来自工具而非格式。
- "切线按 UV 层数重复"意味着解析器必须先读 `uvLayerCount` 再决定每顶点字节数;自写读取器可以直接跳过切线(导入器也丢弃它)。
- XPS 2.x 与 3.x 的分水岭是 11.8.9(2020‑02);XNALaraMesh 代码中的 "XPS 1.8.9" 应为 11.8.9 的笔误。
- 自写读取器只需实现:magic 检测 → 头部(按 `hasTangent` 决定 settings 块处理)→ 骨骼 → 网格,并按两个布尔分支即可覆盖 `.mesh`/`.xps`(2.x/3.x)/`.ascii` 全部变体。

### Gaps
- settings 块里 `hash=180`、`type=2` 之后那串常量(`2,4,4,2,1,3,0,4,3,5,4,0,256`)的语义没有任何文档说明;只知道其中 flag 对 `(3,0)(4,1)(5,0)...` 对应 tangent-space swizzle。未找到 XNAaraL 的官方格式说明。
- `hasBoneDirections`(flag 7)为真时文件里是否真的多出骨骼方向数据、放在何处,没有任何可用实现读取它;需要拿到一个 XPS 11.x 保存的带该 flag 的样本文件逆向验证。
- ASCII 格式有多个社区变体(Daemon 修改版带骨骼旋转/轴,见第 8 节),本调研没有拿到这些变体的规格文本。

---

## 2. XPS 不携带的数据,以及 PMX 需要而 XPS 缺少的内容

### Takeaway
XPS 只携带:骨骼名/父/头位置、每网格的名字(内嵌渲染组与 3 个数值参数)、贴图文件名+UV 层号、顶点(位置/法线/RGBA/UV/切线/权重)、三角面,外加少量全局 flags 与可选默认姿势。没有形态键、物理、骨骼尾部/roll、骨骼显示/IK/限制、材质数值参数(颜色、边缘线、toon、sphere)等。面部表情在 XPS 生态里靠面部骨骼或可选网格切换实现。

### Cited Findings
- 骨骼只有 `name/parentId/co`(位置)三项;`XpsBone` 类也只有这三项+id — `XNALaraMesh/read_bin_xps.py::readBones`,`XNALaraMesh/xps_types.py::XpsBone`;写出同样只写这三项 — `XNALaraMesh/write_bin_xps.py::writeBones`
- 材质信息全部来自网格名解析(渲染组号、`specularity`、`texRepeater1/2`、第 6 段 `val4`)和贴图文件名列表 — `XNALaraMesh/xps_material.py::makeRenderType`
- 全局渲染 flags 只有:背面剔除、强制剔除、投影、法线通道 swizzle、gloss、hasBoneDirections — `XNALaraMesh/read_bin_xps.py::flagsDefault`
- XPS/XNALara 模型"大多数有标准面部骨骼,转换到 MMD 后编辑者和用户必须在 MMD 里手动移动面部骨骼来控制表情";该作者的工具给出 46 个面部骨骼名(从 `head eyebrows middle` 到 `head cheek right 4`),前提是模型骨骼名与之完全一致且已刷权重 — [Riveda1972: XPS/XNAlara to MMD Facial Expressions (2016-03-09)](https://www.deviantart.com/riveda1972/art/XPS-XNAlara-to-MMD-Facial-Expressions-UPDATED-595551582)
- XPS 可选项(optional items)可用 `|` 分组,官方示例正是表情网格:`+ "FAU|happy"`、`- "FAU|neutral"` — [搜索结果引用 xnalara.org "XPS -- How to make items optional"](http://xnalara.org/viewtopic.php?f=28&t=1678)
- XPS 与 MMD "work differently and manage textures, morphs/expressions, lights and bones in different ways" — [Jargonfox: Some tips for MMD, PMXEditor, and Blender](https://www.deviantart.com/jargonfox/journal/Some-tips-for-MMD-PMXEditor-and-Blender-907027358)
- XPS 导入 Blender 时导入器把每个 XPS 网格建成一个独立 Mesh 对象、每对象一个材质、按骨骼索引建顶点组、加 Armature 修改器并以骨架为父 — `XNALaraMesh/import_xnalara_model.py::importMesh/setArmatureModifier/setParent/makeVertexGroups`
- 顶点法线以自定义法线(`normals_split_custom_set_from_vertices`)导入 — `XNALaraMesh/import_xnalara_model.py::importMesh`

### Inferences
- 转 PMX 时需要**由插件生成**而 XPS 完全没有的东西:骨骼尾部/显示方向(可用导入器的"子骨骼中点"启发式,见第 6 节)、骨骼标志(可旋转/可移动/显示/IK 等)、显示框(表示枠)、全局标准骨(センター、グルーブ、全ての親、腰、IK 腿脚)、形态键(至少空列表;表情需另行从面部骨骼姿势烘焙为顶点形变)、刚体/Joint、材质数值(漫反射/高光/环境色、边缘线、toon/sphere)、材质双面/阴影标志(可由渲染组 alpha 与全局 `backFaceCulling` 推断)、日英双语名(由 BoneDict 翻译,见第 4 节)。
- XPS 每网格一材质,材质名=网格名,因此 PMX 材质数 = 导入对象数(若不合并);PMX 的材质顺序决定绘制顺序,alpha 渲染组(见第 3 节)应排在后面。
- XPS 顶点权重已归一(导出时 B2XPS 做归一;XPS 自身输出一般为归一),但 PMX BDEF4 需要 ≤ 4 根骨骼;读到 V3 变长权重时需截断到前 4 大并重新归一(导入器已按权重降序写出)。

### Gaps
- 没有在本次调研中核对 PMX 2.0/2.1 规格原文(由另一位研究者负责);以上 PMX 侧需求列表是基于 XPS 缺失项的推断。
- 未找到 XPS 顶点权重是否保证归一化的正式说明。

---

## 3. 渲染组(Render Group)完整表、网格命名(参数/可选项/分组/`nPart!`)、"Haydee"/XPS 11.x 扩展

### Takeaway
导入器 `xps_material.RenderGroup` 内置 1–43 号渲染组(含 34/35 只定义贴图槽),每组决定贴图槽顺序、是否 alpha 混合、是否 shadeless/顶点光照、是否可摆姿势、高光与 micro-bump 重复参数的使用。网格名格式 `RG_Name_Spec_Bump1Rep_Bump2Rep[_val4]`;首段不是数字时默认 RG=5。可选项用 `+`/`-` 前缀(默认显示/隐藏)、`|` 分组、`.` 后缀把多网格合并为一个菜单项;前缀放在名字段上(如 `40_+hat_0.5_0_0`)。"Haydee" 只是 README 复制错误,不是 XPS 扩展。

### Cited Findings

**网格名解析规则**
- `makeRenderType` 用 `_` 切分,最多取 8 段;第 0 段能转为数字 → `renderGroupNum=int`,后续段依次为 `meshName`、`specularity`、`texRepeater1`、`texRepeater2`、第 5 段存为 `val4`;第 0 段不是数字 → `renderGroupNum` 保持默认 **5**,名字取第 0 段,参数依次后移;缺省 `specularity=1`、`texRepeater1=0`、`texRepeater2=0`,解析失败(NaN)保留默认 — `XNALaraMesh/xps_material.py::makeRenderType`
- 社区文档(XNAaraL 2011 年补充的表):格式 `[RenderGroup]_[MeshName]_[Value1]_[Value2]_[Value3]`,Value1 = 高光强度(默认 0.1),Value2 = Bump map 1 重复次数(0 = 忽略),Value3 = Bump map 2 重复次数;示例 `2_body_0.1_0_0` — [xnalara.forumotion Lesson 5 "What is render groups?"](https://xnalara.forumotion.com/t71-lesson-5-what-is-render-groups)
- "每个网格部件必须有渲染组号才能在 XNALara 中可见;数字决定贴图数量、贴图顺序和使用的效果(shadeless、transparent…)";RG1 = 6 张(diffuse‑light‑bump‑mask‑bump1‑bump2,如裤子),RG2 = 3 张(diffuse‑light‑bump,如皮肤),RG25 = 4 张(带高光的头发);"24/25 已弃用应改用 22/23,26/27 已弃用应改用 28/29" — [搜索摘要,来源 Tomb Raider Forums XNALara Mesh Modding Tutorials 与 junkymana 列表](https://www.tombraiderforums.com/showthread.php?t=173087);[junkymana: XNALara/XPS Render Groups (2015-06-30)](https://www.deviantart.com/junkymana/art/XNALara-XPS-Render-Groups-543000260)
- 2018 年 XnaFreak 的"新渲染组"并不是新编号,而是把模型存成 NGFF(obj/mtl)后在 `.mtl` 中加 `shader NewRGs;DiffuseEnvBumpGlow` / `shader NewRGs;DiffuseEnvBumpSpecular`,复用 RG 24/25 的 4 个槽(lightmap 槽放环境贴图,specular 槽放发光图)— [XnaFreak: New XPS Render Groups (2018-07-13)](https://www.deviantart.com/xnafreak/art/New-XPS-Render-Groups-754288680)

**导入器内置渲染组表**(来源:`XNALaraMesh/xps_material.py::RenderGroup.__init__`;D=diffuse, L=lightmap, B=bump, M=mask, B1/B2=micro bump 1/2, S=specular, E=environment, Em=emission;"光照"列为 `rgShadding`:Yes=正常光照,False=shadeless,Vertex=顶点光照,Yes/No=可切换)

| RG | alpha | 贴图槽顺序 | 光照 | 可摆姿势 | 高光 | Bump1Rep/Bump2Rep | 备注 |
|---|---|---|---|---|---|---|---|
| 1 | 否 | D, L, B, M, B1, B2 | Yes | 是 | Yes | T/T | 6 张 |
| 2 | 否 | D, L, B | Yes | 是 | Yes | F/F | |
| 3 | 否 | D, L | Yes | 是 | No | F/F | |
| 4 | 否 | D, B | Yes | 是 | Yes | F/F | |
| 5 | 否 | D | Yes | 是 | No | F/F | 未知 RG 的默认值也是 5 |
| 6 | **是** | D, B | Yes | 是 | Yes | F/F | |
| 7 | **是** | D | Yes | 是 | No | F/F | |
| 8 | **是** | D, L, B | Yes | 是 | Yes | F/F | |
| 9 | **是** | D, L | Yes | 是 | No | F/F | |
| 10 | 否 | D | False(shadeless) | 是 | No | F/F | |
| 11 | 否 | D, B | Vertex | 否 | Yes | F/F | |
| 12 | **是** | D, B | Vertex | 否 | Yes | F/F | |
| 13 | 否 | D | False | 否 | No | F/F | |
| 14 | 否 | D, B | False | 否 | Yes | F/F | |
| 15 | **是** | D, B | False | 否 | Yes | F/F | |
| 16 | 否 | D | Yes | 否 | No | F/F | |
| 17 | 否 | D, L | Yes | 否 | No | F/F | |
| 18 | **是** | D | Yes | 否 | No | F/F | |
| 19 | **是** | D, L | Yes | 否 | No | F/F | |
| 20 | **是** | D, L, B, M, B1, B2 | Yes | 是 | Yes | T/T | RG1 的 alpha 版 |
| 21 | **是** | D | False | 是 | No | F/F | |
| 22 | 否 | D, L, B, M, B1, B2, S | Yes | 是 | Yes | T/T | 7 张 |
| 23 | **是** | D, L, B, M, B1, B2, S | Yes | 是 | Yes | T/T | 7 张 |
| 24 | 否 | D, L, B, S | Yes | 是 | Yes | F/F | 社区称已弃用 |
| 25 | **是** | D, L, B, S | Yes | 是 | Yes | F/F | 社区称已弃用 |
| 26 | 否 | D, B, E, M | Yes/No | 是 | Yes intensity | F/F | 环境反射;社区称已弃用 |
| 27 | **是** | D, B, E, M | Yes/No | 是 | Yes intensity | F/F | |
| 28 | 否 | D, B, M, B1, B2, E | Yes/No | 是 | Yes intensity | T/T | B1 用 `texRepeater2` |
| 29 | **是** | D, B, M, B1, B2, E | Yes/No | 是 | Yes intensity | T/T | 同上 |
| 30 | 否 | D, B, Em | Yes/No | 是 | Yes intensity | F/F | |
| 31 | **是** | D, B, Em | Yes/No | 是 | Yes intensity | F/F | |
| 32 | 否 | D | Yes | 是 | Yes | F/F | |
| 33 | **是** | D | Yes | 是 | Yes | F/F | |
| 34 | (默认 否) | D, B, M, S | (默认) | (默认) | (默认) | (默认) | 代码只设置了贴图槽 |
| 35 | (默认 否) | D, B, M, S | (默认) | (默认) | (默认) | (默认) | 同上,**未标 alpha** |
| 36 | 否 | D, B, Em | Yes/No | 是 | Yes intensity | T/F | 发光图用 `param1` 缩放 |
| 37 | **是** | D, B, Em | Yes/No | 是 | Yes intensity | T/F | 同上 |
| 38 | 否 | D, B, S, Em | Yes/No | 是 | Yes intensity | T/F | |
| 39 | **是** | D, B, S, Em | Yes/No | 是 | Yes intensity | T/F | |
| 40 | 否 | D, B, S | Yes | 是 | Yes | F/F | |
| 41 | **是** | D, B, S | Yes | 是 | Yes | F/F | |
| 42 | 否 | D, B, S | Yes | 是 | Yes | F/F,`rgSpec1Rep=True` | 高光图重复 |
| 43 | **是** | D, B, S | Yes | 是 | Yes | F/F,`rgSpec1Rep=True` | |

- 未匹配任何编号时的默认值:`rgTexType = [D, M, M, M, M, M]`,`rgTexCount=6`,`rgAlpha=False`,`rgShadding='Yes'` — `XNALaraMesh/xps_material.py::RenderGroup.__init__` 开头
- 贴图类型枚举及其注释序号:`DIFFUSE 1, LIGHT(lightmap) 2, BUMP 3, MASK 4, BUMP1 5, BUMP2 6, SPECULAR 7, ENVIRONMENT 8, EMISSION 9` — `XNALaraMesh/xps_material.py::TextureType`
- B2XPS 自带的渲染组表只有 10 组,并声称 "Must match XNALaraMesh xps_material.py definitions exactly":`4:(F,[D,B]) 5:(F,[D]) 6:(T,[D,B]) 7:(T,[D]) 36:(F,[D,B,Em]) 37:(T,[D,B,Em]) 38:(F,[D,B,S,Em]) 39:(T,[D,B,S,Em]) 25:(F,[D,B,S]) 26:(T,[D,B,S])`;`choose_render_group` 对"漫反射+法线+高光"返回 25(不透明)/26(alpha)— `b2xps_addon/materials.py::RENDER_GROUPS/choose_render_group`

**可选项与分组命名**
- `'+'` = "show optional item by default 'yes'",`'-'` = "show optional item by default 'no'";用 `'|'` 作为组名与菜单名的分隔符,例 `+ "FAU|happy"`、`- "FAU|neutral"`;前缀写在名字段上,如 `40_hat_0.5_0_0` → `40_+hat_0.5_0_0`;由多个网格组成的一个可选项(如眼镜的镜片与镜框)给同一个菜单名加 `.` 后缀:`-glasses.glass`、`-glasses.frame` — [搜索摘要引用 xnalara.org "XPS -- How to make items optional"](http://xnalara.org/viewtopic.php?f=28&t=1678) 与 [Tomb Raider Forums XNALara Mesh Modding Tutorials](https://www.tombraiderforums.com/showthread.php?t=173087)(注:xnalara.org 页面本次直接抓取失败——TLS/JS 跳转,引文来自搜索引擎摘录)
- Valerie-Bosco 分支的导入器把 "Optional" 网格放进专用集合,命名格式 `model_name_here | OPTIONAL` — [Valerie-Bosco/XNALara-io-Tools README](https://github.com/Valerie-Bosco/XNALara-io-Tools)
- XPS 10.9.4 "Wardrobe Edition"(2013‑01‑21)引入 "make items optional with a preview function" 与可穿戴 `Outfit.mesh`(只需必要骨骼,加载后吸附到角色同名骨骼)— [XNALARAITALIA: XPS 10.9.4 Wardrobe Edition](https://www.deviantart.com/xnalaraitalia/journal/XPS-10-9-4-Wardrobe-Edition-349764705)
- XNALaraMesh 导入器**不处理** `+`/`-`/`|`:`makeRenderType` 把它们留在 `meshName` 里,导入后对象/材质名原样保留;源码中没有任何按前缀设置可见性的逻辑 — `XNALaraMesh/xps_material.py::makeRenderType`,`XNALaraMesh/import_xnalara_model.py`(全文无 `'+'`/`'-'` 处理)

**`nPart!` 网格分片**
- `joinMeshParts` 选项说明:"Join MeshParts (meshes that contain 'nPart!' in the name)";实现用正则 `(!.*)*([\d]+nPart)*!` 把名字中 `!` 及其后缀去掉,同名的网格按名字排序后合并(顶点索引偏移、共用首个网格的贴图与 UV 层数)— `XNALaraMesh/xps_tools.py::Import_Xps_Model_Op.joinMeshParts`,`XNALaraMesh/import_xnalara_model.py::createJoinedMeshes`
- XPS 工具有 "automatic splitter",选项中有 "bone limit count" 可提高以控制网格拆分 — [搜索摘要,来源 mariokart64n XnaLara Converter 讨论](https://art.cleberg.net/post/mariokart64n/XnaLara-Converter-675360368?p=1)

**"Haydee" 与 XPS 11.x**
- 本地 README 第一行 "Blender an addon to Export/Import Haydee assets." — `XNALaraMesh/README.md`
- johnzero7 另有独立仓库 HaydeeTools:"Blender addon to import/export Haydee game models, animations, poses, etc."(创建 2017‑06‑24,最后 push 2023‑10‑28,无 license)— [GitHub API johnzero7/HaydeeTools](https://api.github.com/repos/johnzero7/HaydeeTools)
- XPS 11.x 发布线:10.9.4 Wardrobe(2013)、11.3 Wolf Bane(release 180)、11.8.8 Thumbnail(release 188)、11.8.9 View Mode(release 189,2020‑02‑20)— [xnalara.forumotion 11.3](https://xnalara.forumotion.com/t314-xna-posing-studio-xps-11-3-wolf-bane-edition-release-180);[11.8.8](https://xnalara.forumotion.com/t321-xna-posing-studio-xps-11-8-8-thumbnail-edition-release-188);[11.8.9](https://xnalara.forumotion.com/t327-xna-posing-studio-11-8-9-view-mode-edition-release-189)

### Inferences
- 对 XPS→PMX 转换真正有用的渲染组信息只有三类:(1) 贴图槽顺序 → 找到 diffuse(PMX 唯一贴图)、可选 specular/emission/lightmap(可烘焙或忽略)、bump(PMX 无法线贴图,只能丢弃或烘焙);(2) `rgAlpha` → PMX 材质的绘制顺序/双面/透明处理;(3) shadeless(10/13/14/15/21)→ 可映射为 PMX 的"无阴影/不接受自阴影"标志。
- B2XPS 的 25/26 定义与 XNALaraMesh(24/25 = D,L,B,S;26 = D,B,E,M)不符:B2XPS 把 "D+B+S" 导出为 RG25/26,在 XPS 中会被当作 "D,L,B,S"/"D,B,E,M" 解释(贴图槽错位)。更合适的应是 40/41(D,B,S)。这是 B2XPS 的 bug,写自己的读取器时不要照抄 B2XPS 的表。
- 导入器对 35 未置 alpha,很可能是上游遗漏(编号规律是奇数/后一个为 alpha 版);自写实现可把 35 视为 34 的 alpha 版,但需用真实模型验证。
- `|` 分组和 `.` 后缀在转换器中可用于:把同一可选项的多网格合并成一个 PMX 材质组,并把 `-` 前缀的默认隐藏网格映射为"初始不显示"(PMX 无显示开关,可选方案:生成材质形态(材质モーフ)把它们透明度置 0,或在导出时直接剔除)。
- "Haydee"与 XPS 无关:README 文案是从 HaydeeTools 复制来的笔误;没有发现 XPS 存在"Haydee 扩展"。

### Gaps
- 没有拿到 XNAaraL 官方的渲染组原表(junkymana 的列表是图片,xnalara.org 原帖抓取失败);34/35、40–43 的官方语义只能以 XNALaraMesh 代码为准。
- `val4`(名字第 6 段)的含义不明,导入器只是保存并在重命名时原样写回。
- `nPart!` 命名的确切来源(XPS 自动拆分器还是某个 3ds Max 脚本)未得到一手确认。

---

## 4. XNALara "generic" 骨骼命名约定与 BoneDict.txt 机制

### Takeaway
XNALara 通用骨名是小写、空格分隔、"部位 + 侧 + 细分"的英文短语(如 `arm left shoulder 1`、`leg right knee`、`head neck upper`),`root hips`/`root ground` 为根,面部 46 根以 `head ...` 开头,无权重骨骼常以 `unused` 前缀标记。BoneDict.txt 是逐行 `原始骨名;通用骨名` 的文本文件:放在 XPS.exe 同目录可在加载时实时改名;XNALaraMesh 提供生成/按字典改名/还原三个操作;社区(如 Riveda1972)以同一格式分发 XPS→MMD 日文骨名字典。

### Cited Findings

**通用骨名(有出处的部分)**

| 部位 | XPS 通用骨名 | MMD 对应(Riveda1972) | 来源 |
|---|---|---|---|
| 根 | `root hips` | センター | [Riveda1972 XPS to MMD bones reference list (2016-07-05)](https://www.deviantart.com/riveda1972/art/MMD-XPS-to-MMD-bones-reference-list-619693351) |
| 根(地面) | `root ground` | — | 导入器对 `"root ground"` 或无父骨骼特殊处理 `XNALaraMesh/import_xnalara_model.py::boneTailMiddle` |
| 骨盆 | `pelvis` | 下半身 | Riveda1972 列表 |
| 脊柱 | `spine lower`, `spine lower b`(常缺), `spine upper`, `spine upper b`(常缺) | 上半身, 上半身b, 上半身2, 上半身3 | 同上 |
| 颈/头 | `head neck lower`, `head neck upper` | 首, 頭 | 同上;Sapper's blog 亦列 `head neck upper` |
| 眼球 | `head eyeball left/right` | 左目/右目 | Riveda1972 列表 |
| 腿 | `leg left/right thigh`, `knee`, `ankle`, `toes` | 左/右足, ひざ, 足首, つま先 | 同上;[Sapper's blog (2016-02)](http://sappersblog.blogspot.com/2016/02/copy-trle-animation-frame-to-xnalara.html) |
| 臂 | `arm left/right shoulder 1`, `shoulder 2`, `elbow`, `wrist` | (列表给出 shoulder 1/2, elbow, wrist 对应) | Riveda1972 列表;Sapper's blog 列 `arm left shoulder 2`、`arm left elbow`、`arm left wrist` |
| 手指 | 5 指 × 3 节,后缀 `a/b/c`(即 `arm left finger 1a` … `5c`) | 对应 MMD 指骨 | Riveda1972 列表 "5 fingers (each with 3 segments: a, b, c)" |
| 面部 | 46 根,从 `head eyebrows middle` 到 `head cheek right 4` | 工具生成 46 个表情 | [Riveda1972 Facial Expressions](https://www.deviantart.com/riveda1972/art/XPS-XNAlara-to-MMD-Facial-Expressions-UPDATED-595551582) |
| 无权重 | 以 `unused` 开头 | — | `XNALaraMesh/import_xnalara_model.py::hideBonesByName`;`XNALaraMesh/xps_toolshelf.py::ArmatureBonesHideByName_Op`('Move bones starting with "unused" to the armature layer 2') |

- "XPS 模型实际上没有统一标准,因为大多数模型是从游戏提取或从其他格式移植的,各自带有自己的骨名";`*twist` 骨骼需要评估后合并到父骨或删除 — [Riveda1972 bones reference list](https://www.deviantart.com/riveda1972/art/MMD-XPS-to-MMD-bones-reference-list-619693351)
- 模型的主骨可能叫 `root`、`hip`、`root ground` 或 `root hips` — [hanshelia ascii-pose-bone-renamer 商品页摘要](https://hanshelia.gumroad.com/l/rsnxdo)
- XPS 11.5+ 保存 Generic Item 时有 "save only visible" 与 "hidden unused bones" 选项,之后可 "Modify → Clean Armature" — [Tokami-Fuko: Converting XPS to MMD with bones (2016-03-22)](https://www.deviantart.com/tokami-fuko/art/Converting-XPS-to-MMD-with-bones-598167627)
- 导入器的左右命名转换:正则匹配子串 `left`/`right`(忽略大小写)→ 替换为占位符 `*side*` 并追加 `.L`/`.R`;逆向时去掉后缀再把 `*side*` 换回 — `XNALaraMesh/import_xnalara_pose.py::renameBoneToBlender/renameBoneToXps`(常量 `PLACE_HOLDER='*side*'`,`LEFT_XPS_SUFFIX='left'`)
- 导入器把 Blender 顶点组名限制(63 字符)记在注释里 — `XNALaraMesh/import_xnalara_model.py::makeVertexGroups`

**BoneDict.txt 机制**
- XPS 10.9.4(2013‑01‑21):"Put a file called BoneDict.txt inside the same folder like XNALara XPS.exe";格式为"原始骨名;XNALara 命名约定",示例 `Upper_arm.L;arm left shoulder 2`;用途是加载含游戏原始骨名的模型时实时改名 — [XNALARAITALIA: XPS 10.9.4 Wardrobe Edition](https://www.deviantart.com/xnalaraitalia/journal/XPS-10-9-4-Wardrobe-Edition-349764705)
- XNALaraMesh 解析:按行 split,`;` 分割成恰好 2 段才有效,`oldName → newName` 存 rename 字典、反向存 restore 字典 — `XNALaraMesh/read_ascii_xps.py::boneDictData/readBoneDict`
- 改名时先尝试把字典键转换成 Blender 命名(`renameBoneToBlender(key)`)查找骨骼,找不到再用原名 — `XNALaraMesh/import_xnalara_model.py::renameBonesUsingDict`
- 生成字典:把所有骨名(先转回 XPS 命名)排序后写 `name;name` 行,默认文件名 `BoneDict.txt` — `XNALaraMesh/export_xnalara_model.py::boneDictGenerate`,`XNALaraMesh/xps_tools.py::ArmatureBoneDictGenerate_Op`
- 三个操作符:`xps_tools.bones_dictionary_generate`、`bones_dictionary_rename`、`bones_dictionary_restore` — `XNALaraMesh/__init__.py` 注册表,`XNALaraMesh/xps_tools.py`
- 社区分发示例:Riveda1972 "XNALara 2 MMD - Bones names translator" 就是一个 `old;new` 结构的 BoneDict.txt,把 XPS 骨名译成 MMD 日文名,放入 XPS 主目录后加载模型即自动翻译,再导出转 PMX;v1.10(2017‑08‑02)加入 DAZ/Poser 支持;不翻译面部骨 — [Riveda1972 Bones names translator](https://www.deviantart.com/riveda1972/art/XNALara-2-MMD-Bones-names-translator-UPD-1-10-630415138)
- 其他支持 BoneDict 模板的工具:XPS ASCII Editor v1.9(zareef)— [XPS ASCII Editor](https://www.deviantart.com/zareef/journal/XPS-ASCII-Editor-v1-8-Tool-539369755);hanshelia 的 ascii/pose 骨骼重命名器 — [GitHub hanshelia/ascii-pose-bone-renamer-xnalara](https://github.com/hanshelia/ascii-pose-bone-renamer-xnalara)

### Inferences
- 对本项目,BoneDict 的 `old;new` 行格式是现成的"游戏骨名 → 通用骨名"与"通用骨名 → MMD 日文名"两级映射载体;可以直接兼容读取社区字典,再叠加自己的"通用名 → PMX 标准骨"表。
- 匹配时应与导入器一致:大小写不敏感、容忍 `.L/.R` 与 `left/right` 两种写法、`*twist|ctr|root|adj\d*` 视为辅助骨(导入器计算骨尾时就排除这些)。
- `unused` 前缀骨骼和"无任何顶点组引用的骨骼链"是两类可以直接剔除(或转为 PMX 不显示骨)的对象。

### Gaps
- 没有找到 XNAaraL 发布的完整官方通用骨名清单(含 `head eyelid ...`、`head jaw ...`、`breast left/right` 等);本表只收录有出处的名字,任务中提到的其他名字需用真实模型或 XPS 自带 Generic_Item 核对。
- Riveda1972 面部 46 骨名的完整清单在 DeviantArt 页面图片/附件中,本次只拿到首尾两项。

---

## 5. 坐标系、朝向与单位:XNALara ↔ Blender ↔ MMD

### Takeaway
XNALara 基于 XNA:右手系、+X 右、+Y 上、+Z 朝向观察者。XNALaraMesh 导入时 Blender 坐标 = `(x, -z, y)`,导出时 `(x, z, -y)`,面索引翻转绕向以保持法线朝外,UV 的 V 翻转 `v' = 1 - v`;**不做任何缩放**(1 XPS 单位 = 1 Blender 单位)。导入后模型面向 Blender 的 -Y(即正对 Front 视图)。XPS 单位的"米"属性没有找到正式文档,只能从导入器的骨骼长度常量间接推断为近似米制。

### Cited Findings
- "The XNA Framework uses a right-handed coordinate system, with the positive x-axis pointing to the right, the positive y-axis pointing up, and the positive z-axis pointing toward the observer" — [Microsoft Learn: Vector3.Forward (XNA Game Studio 3.5)](https://learn.microsoft.com/en-us/previous-versions/windows/silverlight/dotnet-windows-silverlight/bb196940(v=xnagamestudio.35));[Vector3.Backward (XNA 4.1)](https://learn.microsoft.com/en-us/previous-versions/windows/xna/bb195065(v=xnagamestudio.41))
- 导入坐标变换:`x, y, z = coords; z = -z; return (x, z, y)` → Blender `(X, Y, Z) = (x_xps, -z_xps, y_xps)`;法线用同一函数 — `XNALaraMesh/import_xnalara_model.py::coordTransform`,`importMesh`
- 面绕向:`faceTransform(face) = [face[0], face[2], face[1]]` — `XNALaraMesh/import_xnalara_model.py::faceTransform`
- UV:`u = u + uvDisplX; v = 1 + uvDisplY - v` — `XNALaraMesh/import_xnalara_model.py::uvTransform`(导出为 `v = 1 - uvDisplY - v`,`export_xnalara_model.py::uvTransform`)
- 导出坐标变换:`y = -y; return (x, z, y)` → XPS `(x_b, z_b, -y_b)` — `XNALaraMesh/export_xnalara_model.py::coordTransform`;B2XPS 同样 `coord_transform(co) = (co[0], co[2], -co[1])`,`uv_transform = (u, 1 - v)`,面 `(i0, i2, i1)` — `b2xps_addon/exporter.py`
- 姿势导入的旋转:向量先经 `(x, -z, y)` 变换,再按 Euler 顺序 `'YXZ'`(角度制转弧度)转四元数,并用骨骼 `matrix_local` 的旋转做相似变换进入骨骼局部空间;平移同样变换后旋入局部空间;缩放不变换 — `XNALaraMesh/import_xnalara_pose.py::xpsBoneRotToEuler/vectorTransform/xpsBoneRotate/xpsBoneTranslate/xpsBoneScale`
- 导入器与两个导出器的坐标函数均无乘法缩放因子 — `XNALaraMesh/import_xnalara_model.py::coordTransform`,`XNALaraMesh/export_xnalara_model.py::coordTransform`,`b2xps_addon/exporter.py::coord_transform`
- 导入器中的尺度常量:`MIN_BONE_LENGHT = 0.005`;新建骨骼初始尾部 `head + (0, 0, -0.1)`;根骨(`root ground` 或无父)尾部 `head + (0, -0.5, 0)`;零长度骨尾部 `head - (0, 0.001, 0)` — `XNALaraMesh/import_xnalara_model.py::importBones/boneTailMiddle/setMinimumLenght`
- Blender 手册 Viewpoint 页只列出 Front = Numpad1、Right = Numpad3、Top = Numpad7 等热键并说明它们对齐到全局轴,未在正文给出轴向文字 — [Blender Manual: Viewpoint](https://docs.blender.org/manual/en/latest/editors/3dview/navigate/viewpoint.html)
- 关于单位/模型身高:多轮检索均未找到说明 XNALara 1 单位等于多少米、或典型 XPS 角色高度的文档(XPS→MMD 教程 Riveda1972 v1.1 与 Tokami-Fuko 均未给出缩放系数)— [Riveda1972 conversion guide v1.1 (2016-12-26)](https://www.deviantart.com/riveda1972/art/MMD-XNALara-to-MMD-Model-conversion-guide-v1-1-653374127);[Tokami-Fuko (2016-03-22)](https://www.deviantart.com/tokami-fuko/art/Converting-XPS-to-MMD-with-bones-598167627)

### Inferences
- 轴映射总结:XPS +X → Blender +X;XPS +Y(上)→ Blender +Z(上);XPS +Z(朝观察者)→ Blender -Y。Blender 的 Front 视图从 -Y 一侧看向 +Y,因此 XPS 中面向默认相机(+Z)的角色导入后正对 Blender Front 视图;导入器把根骨尾部指向 -Y 也印证了"-Y 是前方"。
- 这是一次手性翻转(行列式为 -1 的轴置换需要配合取负才能保持右手系;这里 `(x, -z, y)` 是绕 X 轴 +90° 的纯旋转,行列式 +1),所以严格说没有手性翻转——两者都是右手系;但面索引仍被翻转,原因是 XNALara/DirectX 以顺时针为正面、Blender 以逆时针为正面。自写读取器若保留 XNALaraMesh 的做法(翻转绕向)即可得到正确的外向法线。
- 单位:导入器以 0.005 为最小骨长、0.5 为根骨尾长、0.1 为默认尾长,这些数字只有在模型以米为单位(角色高 ≈ 1.5–2 单位)时才合理;结合 XNALara 原始用途(Tomb Raider Underworld 资源),推断 XPS 单位近似米。**但这是推断,需要用真实模型测量验证**(建议插件在导入后测量 `root ground`→头顶的包围盒高度,按目标身高自动求 MMD 缩放系数,而不是硬编码)。
- 若 1 MMD 单位 ≈ 8 cm(由另一位研究者核实),则米制模型转 PMX 的缩放约 ×12.5;但由于 XPS 模型多为游戏提取、单位不一,应允许用户覆盖。

### Gaps
- XNALara/XPS 的单位定义与典型角色高度:无文档、本机也没有任何 `.mesh/.ascii/.xps` 样本可测量(`find` 搜索项目目录、Downloads、Documents、Desktop 均为空)。
- 未找到明确写出"XPS 模型面向 +Z"的文档;朝向结论是由 XNA 相机约定 + 导入器映射推出的。

---

## 6. johnzero7 XNALaraMesh 2.0.2 导入器行为:选项、骨骼尾部/连接/AutoIK、`unused`、材质、姿势

### Takeaway
导入器选项共 10 个(UV 位移 X/Y、默认姿势、合并撕裂顶点、合并网格分片、标记缝合边、顶点色、连接骨骼、AutoIK、导入法线)。骨骼尾部完全由启发式生成:根骨指向 -Y 0.5,其余指向可见子骨骼头部的平均点(排除 twist/ctr/root/adj 辅助骨),无子骨骼则沿"父尾→本头"的方向延伸;`connectBones` 只在子骨头部恰好等于父骨尾部时设 `use_connect`;`autoIk` 只是打开 Pose 的 Auto IK 开关。`unused` 前缀骨骼与无顶点组引用的骨骼链被移到骨骼层 2(隐藏)。材质按渲染组贴图槽接入自定义 "XPS Shader" 节点组。XPS 格式中**不存在**骨骼 roll/朝向信息。

### Cited Findings

**导入选项**(来源:`XNALaraMesh/xps_tools.py::Import_Xps_Model_Op`;`XNALaraMesh/xps_types.py::XpsImportSettings`)

| 属性 | UI 名 | 默认 | 说明文字 / 实现 |
|---|---|---|---|
| `uvDisplX` / `uvDisplY` | UV Displace X/Y | 0 / 0 | "Displace UV X/Y axis",整数,加到 u / v 上(`uvTransform`) |
| `impDefPose` | Default Pose | False | "Import Default Pose":若头部含姿势则导入后应用 `setXpsPose` |
| `markSeams` | Mark Seams | True | "Mark as Seams the edged merged by the addon";仅当 `joinMeshRips` 为真才生效(`self.markSeams and self.joinMeshRips`) |
| `vColors` | Vertex Colors | True | 建 `vertex_colors` 层,按 loop 写入 `byte/255` |
| `joinMeshRips` | Merge Doubles by Normal | True | "Merge vertices with the same position and normal":顶点键 `str(co)+str(norm)`;关闭时键包含原顶点 id(不合并) |
| `joinMeshParts` | Join MeshParts | True | 合并名字含 `nPart!` 的网格(见第 3 节) |
| `connectBones` | Connect Bones | True | "Connect Bones all bones" |
| `autoIk` | AutoIK | True | `armature_ob.pose.use_auto_ik = autoIk` |
| `importNormals` | Import Normals | True | "Import Custom Normals":`create_normals_split` + `normals_split_custom_set_from_vertices` + `use_auto_smooth=True` |

- 导入流程:新建以文件名命名的 Collection → `createArmature`(显示类型 STICK、`show_in_front`)→ `importBones` → `importMeshesList` → `use_auto_ik` → `hideUnusedBones` → `boneTailMiddleObject` → 可选默认姿势 — `XNALaraMesh/import_xnalara_model.py::xpsImport`
- 导入前会尝试 `material_creator.create_group_nodes()`,失败只打印 "Warning: skipping group nodes" — `XNALaraMesh/xps_tools.py::Import_Xps_Model_Op.execute`

**骨骼创建与尾部**
- 第一遍为每根骨骼建 `edit_bone`,`head = coordTransform(co)`,`tail = head + (0,0,-0.1)`,再 `setMinimumLenght`;第二遍按 `parentId >= 0` 设父;Blender 分配的实际骨名记录在 `blenderBoneNames`(处理重名改名),顶点组按原索引查名 — `XNALaraMesh/import_xnalara_model.py::importBones/addBoneName/getBoneName/assignVertexGroup`
- `boneTailMiddle`:辅助骨正则 `\b(hip)?(twist|ctr|root|adj)\d*\b`;`root ground` 或无父 → `tail = head + (0, -0.5, 0)`;可见骨只考虑可见且非辅助的子骨,隐藏骨考虑所有非辅助子骨;有子骨 → `tail = 子骨 head 平均`;无子骨 → 若 `head != parent.tail` 则 `delta = head - parent.tail`,否则 `delta = parent.tail - parent.head`,`tail = head + delta`;随后对所有骨设最小长度,再 `connectEditBones` — `XNALaraMesh/import_xnalara_model.py::boneTailMiddle`
- `connectEditBones`:仅当 `bone.head == bone.parent.tail`(精确相等)时 `bone.use_connect = connectBones` — `XNALaraMesh/import_xnalara_model.py::connectEditBones`;工具架另有 "Set Bones Connection" 操作符可事后切换 — `XNALaraMesh/xps_toolshelf.py::ArmatureBonesConnect_Op`
- 骨骼 roll:导入器从不设置 `roll`;XPS 数据只有 head 位置(见第 1 节)— `XNALaraMesh/import_xnalara_model.py::importBones`
- 姿势导入时用 `poseBone.bone.matrix_local.to_quaternion()` 把 XPS 的世界轴向旋转变换到骨骼局部空间,说明 XPS 的姿势旋转是定义在模型世界轴上的,与骨骼 roll 无关 — `XNALaraMesh/import_xnalara_pose.py::xpsBoneRotate`

**`unused` 与隐藏**
- `hideUnusedBones` = `hideBonesByVertexGroup`(从根递归,整条链上没有任何子网格顶点组引用的骨骼 → 隐藏)+ `hideBonesByName`(`name.lower().startswith('unused')` → 隐藏);隐藏实现为 `bone.layers[1]=True; bone.layers[0]=False` — `XNALaraMesh/import_xnalara_model.py::hideUnusedBones/recurBones/hideBone`
- 每个网格导入后创建一个 `pose.bone_groups` 并随机配色,把该网格顶点组对应的骨骼归入 — `XNALaraMesh/import_xnalara_model.py::makeBoneGroups`

**材质创建**
- 每网格新建材质 `bpy.data.materials.new(meshFullName)`,`use_nodes=True`,输出节点 ← 节点组 `'XPS Shader'`;`rgAlpha` 为真则 `blend_method='BLEND'` 并把 diffuse 的 Alpha 接到 shader 的 Alpha — `XNALaraMesh/material_creator.py::makeMaterial/makeNodesMaterial`
- 贴图路径 = 模型所在目录 + 文件 basename;文件不存在时生成 1024×1024 占位图并设 `source='FILE'`;`alpha_mode='CHANNEL_PACKED'` — `XNALaraMesh/material_creator.py::makeImageFilepath/loadImage`
- 槽位接法:Diffuse→`Diffuse`;Light→`Lightmap`;Bump→`Bump Map`(图像设 `is_data`);Specular→`Specular`(`is_data`);Environment→改用 `ShaderNodeTexEnvironment` 并用 TexCoord 的 `Reflection` 输出驱动;Mask→`Bump Mask`;Bump1→`MicroBump 1`,Mapping 节点 Scale = `texRepeater1`(RG 28/29 用 `texRepeater2`);Bump2→`MicroBump 2`,Scale=`texRepeater2`;Emission→`Emission`,RG 36/37 时 Scale=`param1`;超出 `rgTexType` 长度的多余贴图只建图像节点不连接 — `XNALaraMesh/material_creator.py::makeNodesMaterial`
- "XPS Shader" 节点组内部:Diffuse × Lightmap(MULTIPLY)→ Principled Base Color;Specular → RGB→BW → Power(2) → Invert → Roughness;Alpha → Alpha;Emission → Emission;三张法线各经 "Invert Channel" 组(默认 R/G/B 反转因子 0/0/0,源码中按 flags 设置的行被注释掉)→ "Normal Mask" / "Normal Mix" → Normal Map 节点 → Normal;Environment → Emission shader 与 Principled 做 Add Shader — `XNALaraMesh/material_creator.py::xps_shader_group/mix_normal_group/invert_channel_group/normal_mask_group`
- 节点组 "XPS Shader" 仍用 `shader.inputs.new(...)` / `shader.outputs.new(...)` 旧 API;其余三个组已在本机被改为 `_compat_new_input/_compat_new_output`(注释 "B2XPS compat patch for Blender 4.x")— `XNALaraMesh/material_creator.py`
- 材质创建失败不会中断导入(`try/except` 打印 "Warning: material creation failed")— `XNALaraMesh/import_xnalara_model.py::importMesh`(但见第 7 节的语法错误)

**姿势导入**
- `.pose` 导入操作符要求活动对象为骨架;按骨名(或转换为 Blender 命名后)找 pose bone,依次设旋转(四元数)、平移、缩放,然后对所有选中骨插入 `LocRotScale` 关键帧 — `XNALaraMesh/xps_tools.py::Import_Xps_Pose_Op`,`XNALaraMesh/import_xnalara_pose.py::setXpsPose/xpsPoseBone`
- 序列导入:同目录下去掉末尾数字后同名的 `.pose` 文件按名排序,每个一帧 — `XNALaraMesh/import_xnalara_pose.py::getInputPoseSequence`
- "New Rest Pose":对每个绑定网格复制并应用 Armature 修改器,再 `pose.armature_apply` — `XNALaraMesh/xps_toolshelf.py::NewRestPose_Op`

### Inferences
- 为 PMX 生成骨骼"尾部/显示方向"可直接复用 `boneTailMiddle` 的三条规则(平均子骨头部、沿父向延伸、根骨朝前),并沿用其辅助骨正则;PMX 的"接続先"可以在"单一子骨且其 head == 本骨 tail"时设为子骨索引(对应 `connectEditBones` 的条件),否则用偏移向量。
- XPS 没有 roll/朝向,所以 PMX 的"固定轴/局部轴"信息(手指、手臂的局部轴)必须由插件按骨骼方向自行计算;MMD 标准骨的局部轴约定要在 PMX 侧笔记中确认。
- `unused` 判断 + 顶点组引用检测两条规则可直接作为"可删除骨骼"的默认策略;但 `root ground`/`root hips` 等无权重的根骨不应删除(它们是层级根)。
- 材质侧对 PMX 只需 diffuse 文件名与 alpha 标志;其余贴图可记录到自定义属性以便后续烘焙。

### Gaps
- 导入器没有记录每张贴图的 `uvLayerId`(读取后在材质创建里被注释掉 `# textureUvLayer = textureInfo.uvLayer`),所以多 UV 层模型的贴图-UV 对应关系在导入后丢失;自写读取器应保留。
- 未验证 `boneTailMiddle` 在"隐藏骨骼"分支下的实际视觉效果(依赖 `bone.layers`,在 4.x 已失效)。

---

## 7. 许可、维护状态与 Blender 4.2–5.x 可用分支

### Takeaway
上游 johnzero7/XNALaraMesh 自 2021‑06‑10 起无代码提交(2023‑11 仅 push),**仓库没有 LICENSE 文件**(GitHub API `license: null`),只有从 Blender 官方 OBJ 插件/CGCookie updater 复制来的文件带 GPL 头。目前活跃的两个分支都在 2026‑09‑08 有更新:mayloglog 的 "XPS Import/Export" 以 GPL‑3.0‑or‑later 发布在 extensions.blender.org(Blender 5.0+,v2.1.0 支持 4.4,但禁用了二进制 .xps 导出);Valerie‑Bosco 的 XNALara‑io‑Tools 支持 3.6–5.2(zip 安装,仓库无 LICENSE)。本机 2.0.2 在 4.5 上已不可用(依赖已删除 API,且 `import_xnalara_model.py` 本机改动引入了语法错误)。

### Cited Findings

| 项目 | 类型 | Blender 支持 | 许可 | 最近活动 | 其他 | 来源 |
|---|---|---|---|---|---|---|
| johnzero7/XNALaraMesh | 上游 | README:v2.0.0+ 需 2.80+,1.8.5/1.8.7 for 2.79;`bl_info blender=(2,80,0)` | GitHub API `license.spdx_id = null`;`import_obj.py`/`export_obj.py`/`addon_updater*.py` 带 GPL 头 | 最后提交 2021‑06‑10("Addon updater"),`pushed_at` 2023‑11‑15;创建 2014‑12‑24;600★/110 forks;未归档 | 文档站 johnzero7.github.io/XNALaraMesh 只有简介与下载链接;gitee 有镜像 | [GitHub API](https://api.github.com/repos/johnzero7/XNALaraMesh);[commits](https://api.github.com/repos/johnzero7/XNALaraMesh/commits?per_page=3);本地 `XNALaraMesh/README.md`、`__init__.py`;[docs](https://johnzero7.github.io/XNALaraMesh/);[gitee 镜像](https://gitee.com/toolkit/XNALaraMesh) |
| mayloglog/XNALaraMesh‑blender4.4 → 扩展 "XPS Import/Export"(io‑xnalara) | fork(parent = johnzero7) | 扩展页:5.0 及以上;README:v2.1.0 对应 4.4,v2.2.0+ 对应 5.0+ | 扩展页:GPL‑3.0‑or‑later;GitHub API `license: null` | `pushed_at` 2026‑09‑08;扩展 v2.3.1 发布 2025‑11‑25、约一个月前更新;创建 2025‑02‑25;22★;235 commits | 下载 31,799,评分 4.5/5(10 评);**禁用二进制 .xps 导出**(1080 字节 settings 块 "byte misalignment",重导入失败)改为 ASCII;2.3.1 增加损坏/截断网格的错误处理 | [extensions.blender.org/add-ons/io-xnalara](https://extensions.blender.org/add-ons/io-xnalara);[GitHub](https://github.com/mayloglog/XNALaraMesh-blender4.4);[GitHub API](https://api.github.com/repos/mayloglog/XNALaraMesh-blender4.4) |
| Valerie‑Bosco/XNALara‑io‑Tools(tangled.org 镜像 xnalara_io_tools) | fork(parent = johnzero7) | 描述 "BL 3.6‑5.x",README 3.6–5.2 仅官方正式版 | GitHub API `license: null` | `pushed_at` 2026‑09‑08;releases v1.4.1(2026‑09‑04)、v1.4.2(09‑05)、v1.4.3(09‑08,"fix: BL 4.2 incompatible due to module manager requiring python 3.12");创建 2024‑05‑28;95★;342 commits | 修复骨架结构导入导出、按版本调用正确材质 API、可选网格进独立集合;4.2+ 用 "install from disk" 安装 zip | [GitHub](https://github.com/Valerie-Bosco/XNALara-io-Tools);[GitHub API](https://api.github.com/repos/Valerie-Bosco/XNALara-io-Tools);[releases](https://api.github.com/repos/Valerie-Bosco/XNALara-io-Tools/releases?per_page=3);[tangled.org](https://tangled.org/valerie-bosco.tngl.sh/xnalara_io_tools) |
| Darkblader24/XPS‑XNALara‑Scene‑Importer | 独立插件(导入 XPS 场景 .scene) | — | `license: null` | `pushed_at` 2023‑05‑30;22★ | | [GitHub API](https://api.github.com/repos/Darkblader24/XPS-XNALara-Scene-Importer) |

- Blender 4.0 Python API 变更:"Layers and bone groups have been removed with all associated properties and methods. Bone collections have been added instead.";节点组接口改为 `NodeTree.interface`(`tree.interface.new_socket()` 取代 `tree.inputs.new()`/`tree.outputs.new()`)— [Blender 4.0 Python API release notes](https://developer.blender.org/docs/release_notes/4.0/python_api/)
- Blender 4.1:"use_auto_smooth is removed"、"create_normals_split, calc_normals_split, and free_normals_split are removed"、"Custom normals should be created by normals_split_custom_set or normals_split_custom_set_from_vertices" — [Blender 4.1 Python API release notes](https://developer.blender.org/docs/release_notes/4.1/python_api/)
- 本地 2.0.2 使用了上述已删除 API:`bone.layers[...]`(`hideBone/showBone/visibleBone`)、`armature_ob.pose.bone_groups.new`(`makeBoneGroups`)、`mesh_da.create_normals_split()` 与 `mesh_da.use_auto_smooth = True`(`importMesh`)、`shader.inputs.new`(`xps_shader_group`)— `XNALaraMesh/import_xnalara_model.py`,`XNALaraMesh/material_creator.py`
- 本机 `import_xnalara_model.py` 第 614–618 行 `try:` 后的语句未缩进,`ast.parse` 报 `IndentationError: expected an indented block after 'try' statement on line 614`;该文件与 `material_creator.py`、`xps_tools.py`、`export_xnalara_model.py` 的修改时间为 5 月 23 日(其余文件为 2025‑07‑27),即本机做过手工改动 — 本次 `python -c "import ast..."` 语法检查;目录列表 `ls -la`
- 上游 README 自述功能:导入/导出带骨架的 XPS/XNALara 模型、姿势、自定义法线,导入时创建材质,设置新静止姿势 — `XNALaraMesh/README.md`

### Inferences
- **依赖决策**:上游无许可声明意味着默认"保留所有权利",作为依赖或复制代码在法律上有瑕疵;mayloglog 分支在扩展平台以 GPL‑3.0‑or‑later 发布,若本项目也采用 GPL 则可依赖/复用它,但它禁用了二进制导出且面向 5.0+(4.4 需 v2.1.0)。Valerie 分支覆盖版本最广但同样无 LICENSE 文件。
- 两个活跃分支都只是"让旧代码在新版本上跑",没有改变数据模型;而本项目只需要**读取**,格式本身很小(第 1 节),自写一个无依赖的 XPS 读取器(约几百行)比依赖任一分支更可控,并能保留导入器丢弃的信息(贴图 `uvLayerId`、切线、flags、默认姿势、`+/-/|` 可见性)。
- 本机 2.0.2 不能作为运行时依赖:语法错误 + 4.x 已删 API;只能作为参考实现阅读。

### Gaps
- 未逐文件比对两个分支与上游的代码差异(例如是否仍用 `bone.layers`、是否保留二进制读取路径、是否解析 `+`/`-`),只核对了 README/发布说明。
- Valerie‑Bosco 分支是否在 extensions.blender.org 上架、其 zip 内 `blender_manifest.toml` 声明的许可证,未能确认。

---

## 8. 其他读写器:B2XPS、Noesis 插件、3ds Max/其他 Blender 脚本、XPS 自带工具

### Takeaway
B2XPS 1.1.0(本机)是独立的 Blender→XPS 导出器,对二进制格式的描述与 XNALaraMesh 一致,但有三处与标准/UI 不符(.mesh 实际带头部且无切线;ASCII 权重写成"计数+成对"非标准布局;RG 25/26 槽位表错误)。Noesis 侧有 REDxEYE/noe_xna(`fmt_xna_ascii.py`,仅 ASCII)和 Tosyk/ASCII‑Plugins(`fmt_Daemon_ascii.py`,基于 `fmt_xps_0_9_6.py`,支持 Daemon 变体的骨骼旋转/轴、64K+ 顶点,另含 SecaProject 的 Blender 脚本与 mariokart64n 的 3ds Max `xnalara_io.ms`)。XPS 自身也能导出 NGFF(obj/mtl)。

### Cited Findings

**B2XPS 1.1.0(本地)**
- `bl_info`:name "B2XPS - Universal Blender to XPS Exporter",author "b2xps",version (1,1,0),blender (4,0,0);UI 三种格式:`MESH` "Standard binary format, no header, with tangent"、`XPS` "Binary format with header, no tangent"、`ASCII` — `b2xps_addon/__init__.py`
- 但 `write_binary`(用于 .mesh)与 `write_xps` 实现完全相同:都先 `_write_header` 再 `has_tangent=False, variable_weights=True` — `b2xps_addon/writer.py::write_binary/write_xps`
- ASCII 写出:每顶点先写权重个数一行,再每个权重一行 `idx weight` — `b2xps_addon/writer.py::write_ascii`;而 XNALaraMesh 读取器期望"索引一行 + 权重一行" — `XNALaraMesh/read_ascii_xps.py::readMeshes`
- 导出流程:三角化、取 `corner_normals` 或 `calc_normals_split`、多 UV 层、颜色属性、顶点组权重(>1e‑4,无权重则绑到骨 0 权重 1)、按材质槽拆子网格、按 `(vi, normal, uv0)` 去重、面 `(i0, i2, i1)`、名称 `f"{rg}_{base}.{mat}"`(单材质则 `f"{rg}_{base}"`),去掉对象名已有的 `^\d+_` 前缀;无骨架时写一根 `root` 骨 — `b2xps_addon/exporter.py::_prepare_mesh_data/_build_submesh/export_mesh/export_bones`
- 材质识别:Principled 输入(Base Color/Normal/Specular IOR Level/Specular/Emission Color/Emission)→ 图像节点追溯;其次节点组输入名;最后按文件名关键字(`_n`、`normal`、`_s`、`spec`、`_orm`、`_e`、`emiss`)猜测;alpha 判定看 `surface_render_method=='BLENDED'`/`blend_method`/Alpha 输入 — `b2xps_addon/materials.py`
- 贴图 `uvLayerId` 固定写 0;切线占位 `(1,0,0,0)`;固定 4 权重时截断前 4 大并归一 — `b2xps_addon/writer.py::_write_model_data`

**Noesis / 其他**
- REDxEYE/noe_xna:"Noesis XNA .ascii mesh loader",主文件 `fmt_xna_ascii.py`;页面未显示许可与提交日期 — [GitHub REDxEYE/noe_xna](https://github.com/REDxEYE/noe_xna)
- Tosyk/ASCII‑Plugins:Noesis `fmt_Daemon_ascii.py`("originally fmt_xps_0_9_6.py was taken as a base and modified",支持 Daemon 的骨骼旋转/轴加载、RAPI、64K+ 顶点)、Blender `blender_ascii_import_seca.py`(SecaProject,2.8+–3.0+,带骨骼旋转/轴、自动贴图)、3ds Max `xnalara_io.ms`(mariokart);README 未写许可 — [Tosyk/ASCII-Plugins README](https://github.com/Tosyk/ASCII-Plugins/blob/main/README.md)
- 社区曾有 "Noesis to XNALara/XPS importer/exporter plugin" 讨论帖(xnalara.org,本次无法抓取正文)— [xnalara.org t=1139](https://www.xnalara.org/viewtopic.php?t=1139&start=10);Hime‑Works 曾收到 XNALara Noesis 插件请求 — [Hime-Works/Requests #296](https://github.com/Hime-Works/Requests/issues/296)
- mariokart64n 的 "Xnalara to MMD Converter" 可直接把 XPS 转为 MMD,但要求模型有 `xps.xps` 文件 — [Jargonfox tips (搜索摘要)](https://www.deviantart.com/jargonfox/journal/Some-tips-for-MMD-PMXEditor-and-Blender-907027358)
- XPS 可将模型保存为 NGFF(obj/mtl),XNALaraMesh 也提供 "XPS NGFF (.obj)" 导入/导出菜单项 — [XnaFreak New XPS Render Groups](https://www.deviantart.com/xnafreak/art/New-XPS-Render-Groups-754288680);`XNALaraMesh/xps_tools.py::XpsImportSubMenu`(`ImportXpsNgff`)
- 其他 Blender 侧工具:CATS Blender Plugin(内置 mmd_tools)常被用于 XPS→MMD 流程 — [Jargonfox tips](https://www.deviantart.com/jargonfox/journal/Some-tips-for-MMD-PMXEditor-and-Blender-907027358);[Yusarina Cats 功能页](https://github.com/Yusarina/Cats-Blender-Plugin-Unofficial-/wiki/Features)

### Inferences
- B2XPS 可作为"第二份独立的二进制格式描述"参考(头部常量、字符串编码、顶点布局与 XNALaraMesh 一致),但不能作为渲染组或 ASCII 格式的权威来源;本项目若需要回写 XPS,不要复用其 25/26 映射与 ASCII 权重写法。
- Daemon 变体 ASCII(带骨骼旋转/轴)说明社区里存在"有骨骼朝向"的非标准文件;自写读取器遇到每骨骼多出的行时应能容错(例如检测骨骼块里的额外数值行)。
- Noesis 插件对本项目价值有限(都是 ASCII 读入,且无 PMX 直连),但 `fmt_xps_0_9_6.py` 系列是另一个可交叉验证 ASCII 解析细节的实现。

### Gaps
- 未下载并阅读 `fmt_xna_ascii.py` / `fmt_Daemon_ascii.py` 源码,无法给出它们对二进制 `.mesh/.xps` 的支持情况与许可证。
- `fmt_xps_0_9_6.py` 的原始作者与出处未确认。
