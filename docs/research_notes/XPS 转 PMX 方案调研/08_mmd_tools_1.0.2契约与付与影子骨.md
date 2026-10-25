# mmd_tools v1.0.2（Blender 3.6 本机安装版）导出契约，及付与 / Dummy 骨 / 影子骨深挖

> 调研对象：`C:\Users\haoni\AppData\Roaming\Blender Foundation\Blender\3.6\scripts\addons\mmd_tools`（legacy add-on，包名 `mmd_tools`，`bl_info["version"] == (1, 0, 2)`），下文简写 `src/`；同机 `mmd_uuunyaa_tools` v1.8.0（`...\addons\mmd_uuunyaa_tools`，简写 `uuu/`）。
> 对照基线：同目录 [02_mmd_tools导出契约.md](02_mmd_tools导出契约.md)（v4.5.5）。本笔记只写 1.0.2 的事实与差异；凡未写明的 4.5.5 行为，**不要**默认 1.0.2 也有。
> 方法：逐文件阅读 1.0.2 源码（引用格式 `文件:行号`）；在 Blender 3.6.15（Python 3.10.13）里 headless 跑了 4 批脚本做实测；下载官方 v1.0.2 zip 与本机逐字节 diff；用 GitHub API 查 tag/commit。
> 实测证据（会话临时文件，关键结果已抄进正文）：**实测V** = [verify_mmd_tools_102.json](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)（版本 / 算子清单 / 函数签名 / RNA 属性清单）；**实测A–F** = [verify_live_102.json](assets/08_mmd_tools_1.0.2/verify_live_102.json)（A：`Model.create`+付与直接 apply+导出；B：PMX 导入往返，含付与/IK/表示枠；C：`rename_bones=True`；D：骨序覆盖网格；E：材质贴图；F：刚体/Joint）；**实测G–J** = [verify_live2_102.json](assets/08_mmd_tools_1.0.2/verify_live2_102.json)（G：无覆盖网格时的骨序与可见性；H：`Model.create(armature=现有骨架)`；I：写 `mmd_material` 是否改节点；J：算子/API 是否存在、报错行为、Pose Library、UI 语言）；**实测K** = [verify_live3_102.json](assets/08_mmd_tools_1.0.2/verify_live3_102.json)（枚举 ID-prop 映射、toon ID-prop、`vertex_group_sort`）。
> 日期：2026-10-25。

---

## Q1. 版本与身份：bl_info、运行时检测、模块布局、支持的 Blender/Python、对应的上游 commit、新版功能是否已有

### Takeaway
本机 mmd_tools 是官方 **v1.0.2** 的原样拷贝（tag 指向 commit `94a2208`，2021-12-04 发布），唯一改动是 `auto_scene_setup.py` 里本地加了 `int()` 强转。它是 legacy add-on 包 `mmd_tools`（不是 `bl_ext.*`），没有 `MMD_TOOLS_VERSION`；在 Blender 3.6.15 / Python 3.10.13 下能正常注册 140 个类。比 Blender 3.6 官方推荐的 v2.10.3 老一个大版本。它已经有 SDEF、Display Item Quick Setup、Convert Model、翻译算子、Material Sorter、`mmd_ik_target_override` / `mmd_ik_limit_override`；但**没有** bone_id 排序 / `fix_bone_order`、模型校验、`mmd_root.ik_loop_factor`，也没有骨骼 morph → 顶点 morph 转换。

### Cited Findings
- bl_info：`"name": "mmd_tools"`、`"author": "sugiany"`、`"version": (1, 0, 2)`、`"blender": (2, 83, 0)`、`"description": "Utility tools for MMD model editing. (UuuNyaa's forked version)"`，`tracker_url` 指向 `UuuNyaa/blender_mmd_tools/issues` — [src/__init__.py:3-15](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/__init__.py)。
- 运行时实测：`import mmd_tools; mmd_tools.bl_info["version"]` → `(1, 0, 2)`；`bl_info["blender"]` → `(2, 83, 0)`；`mmd_tools.__package__ == "mmd_tools"`；`hasattr(mmd_tools, "MMD_TOOLS_VERSION")` → `False`；`"mmd_tools" in bpy.context.preferences.addons` → `True`。Blender `3.6.15`，Python `3.10.13` — [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。
- 注册方式：用 `register_wrap` 装饰器收集类，`register()` 里逐个 `bpy.utils.register_class`，再 `properties.register()` 把属性挂到 `bpy.types.Object/Material/PoseBone`。唯一的 app handler 是 `load_post` 上的 `load_handler`（清 SDEF 缓存、注册 SDEF 驱动函数）。控制台会打印 `mmd_tools registed 140 classes` — [src/__init__.py:17-31,202-231](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/__init__.py)、[实测J 日志](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。1.0.2 **没有** `handlers.py`，也没有 depsgraph / frame_change handler（全目录 grep 只命中 `load_post`）。
- 模块布局（`src/`）：
  - `core/{bone,model,material,morph,rigid_body,sdef,shader,camera,lamp}.py`
  - `core/pmx/{__init__,importer,exporter}.py`，其中 `core/pmx/__init__.py` 是不依赖 bpy 的纯 Python PMX 读写器
  - `core/pmd/`、`core/vmd/`、`core/vpd/`
  - `operators/{fileio,model,misc,display_item,material,morph,rigid_body,sdef,view,animation,camera,lamp,addon_updater}.py`
  - `panels/{tool,util_tools,prop_bone,prop_object,prop_material,prop_camera,prop_lamp,view_prop,view_header}.py`
  - `properties/{root,bone,material,morph,rigid_body,camera}.py`
  - `bpyutils.py`、`utils.py`、`translations.py`、`cycles_converter.py`、`auto_scene_setup.py`、`m17n.py`
  - 共约 18.8k 行（本会话 `find`/`wc -l` 统计）。
- 上游对应：
  - GitHub `UuuNyaa/blender_mmd_tools` 现在解析到 `MMD-Blender/blender_mmd_tools` — [Releases API（UuuNyaa 路径）](https://api.github.com/repos/UuuNyaa/blender_mmd_tools/releases?per_page=40)。
  - tag `v1.0.2` → commit `94a2208b974dcb54021a9bce06ee05204808d2d4`，提交信息 "Release preparation"，2021-12-04T13:01:11Z。
  - Release "Release v1.0.2" 发布于 2021-12-04T13:06:28Z，资产 `mmd_tools-v1.0.2.zip`（208 KB），API 里 body 为空 — [Releases API v1.0.2](https://api.github.com/repos/MMD-Blender/blender_mmd_tools/releases/tags/v1.0.2)、[Commits API 2021-12-03~12](https://api.github.com/repos/MMD-Blender/blender_mmd_tools/commits?since=2021-12-03T00:00:00Z&until=2021-12-12T00:00:00Z&per_page=60)。
  - HTML 发布页的抓取摘要说 notes 是 "Support for Blender 3.0"，与 API 的空 body **矛盾** — [Release 页](https://github.com/MMD-Blender/blender_mmd_tools/releases/tag/v1.0.2)。
- 相邻 tag：v1.0.0=`2755fd1`、v1.0.1=`d932aa2`、v2.0.0=`d943a25` … v2.10.3=`d148bdb` — [Tags API](https://api.github.com/repos/MMD-Blender/blender_mmd_tools/tags?per_page=100)。v1.0.2 之前同一天的提交有 "Refactor"、"Merge pull request #8 from Vwings/fix/rig_body_radius_lost"、"Specify the support period"、"Add translations"；之后第一条是 2021-12-11 的 "Change default scales to 0.08" — [Commits API](https://api.github.com/repos/MMD-Blender/blender_mmd_tools/commits?since=2021-12-03T00:00:00Z&until=2021-12-12T00:00:00Z&per_page=60)。
- 逐字节核对：下载官方 `mmd_tools-v1.0.2.zip`，与本机目录 `diff -rq`（排除 `__pycache__`），只有 `auto_scene_setup.py` 不同。本机把 `frame_start/frame_end` 和刚体缓存帧的赋值改成了 `int(s)`/`int(e)`，只影响 VMD 导入后设置帧范围，与 PMX 无关 — [官方 zip](https://github.com/MMD-Blender/blender_mmd_tools/releases/download/v1.0.2/mmd_tools-v1.0.2.zip)（diff 在本会话执行）。
- 它就是 v1.0.2 的佐证：
  - 导入、导出、Create Model 的 `scale` 默认都是 **1.0**；改成 0.08 是 v1.0.2 之后 12-11 才发生的。
  - 非碰撞阈值仍在偏好 `non_collision_threshold` 里；12-15 才挪进操作选项。
  - 仍用 `register_wrap` 而非 `auto_load`；2022-03-30 才改。
  - 证据：[src/operators/fileio.py:90-94,436-440](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)、[src/operators/model.py:181-185](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)、[src/__init__.py:90-96](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/__init__.py)、[Commits API（path=operators/model.py）](https://api.github.com/repos/MMD-Blender/blender_mmd_tools/commits?path=mmd_tools/operators/model.py&since=2021-12-01T00:00:00Z&until=2023-06-30T00:00:00Z&per_page=50)。
- 支持的 Blender 版本：
  - `bl_info["blender"]=(2, 83, 0)`；代码里还留着 `< (2, 80, 0)` 的 2.7x 分支（此时 `bl_info['blender']` 被改写成 `(2, 70, 0)`） — [src/__init__.py:53-54](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/__init__.py)。
  - `bpyutils.makeSphere` 有 `>= (3, 0, 0)` 分支，旁边注释 `# SUPPORT_UNTIL: 3.3 LTS` — [src/bpyutils.py:190-216](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)。
  - v1.0.2 的 README 没有版本支持表 — [README@v1.0.2](https://raw.githubusercontent.com/MMD-Blender/blender_mmd_tools/v1.0.2/README.md)。
  - 当前仓库首页写明：Blender 3.6 对应 v2.x（分支 `blender-v3`，v2.10.3），且 "Blender 3.6 is no longer maintained" — [仓库首页](https://github.com/MMD-Blender/blender_mmd_tools)；另见 [02 笔记 Q10](02_mmd_tools导出契约.md)。
- v2.10.3（Blender 3.6 这条线的最新版）对照：
  - bl_info 是 `(2, 10, 3)`，`blender` 是 `(2, 93, 0)` — [v2.10.3 __init__](https://raw.githubusercontent.com/MMD-Blender/blender_mmd_tools/v2.10.3/mmd_tools/__init__.py)。
  - 导出器**仍**按 `mmd_bone_order_override` 的顶点组顺序决定骨序（exporter.py:338-344）— [v2.10.3 exporter](https://raw.githubusercontent.com/MMD-Blender/blender_mmd_tools/v2.10.3/mmd_tools/core/pmx/exporter.py)。
  - 影子 / Dummy 骨仍放骨骼层 8/9（bone.py:390/401）— [v2.10.3 bone.py](https://raw.githubusercontent.com/MMD-Blender/blender_mmd_tools/v2.10.3/mmd_tools/core/bone.py)。
  - 不同点：IK 迭代因子改成了 `root.mmd_root.ik_loop_factor`（exporter.py:500）。
- 内置更新器：`operators/addon_updater.py` 提供 `mmd_tools.check_addon_update` / `mmd_tools.update_addon`，`config.owner = 'UuuNyaa'`，从 GitHub releases/branches 下载 zip 覆盖安装 — [src/operators/addon_updater.py:123-130,417](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/addon_updater.py)。偏好面板里有 "Check mmd_tools add-on update" 和 "(Danger) Manual Update" — [src/__init__.py:113-177](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/__init__.py)。
- 1.0.2 全部 82 个算子 id（`dir(bpy.ops.mmd_tools)` 实测）：`apply_additional_transform, apply_bone_morph, apply_bone_morph_offset, apply_material_morph_offset, apply_uv_morph, attach_meshes, bone_fixed_axis_setup, bone_local_axes_setup, build_rig, change_mmd_ik_loop_factor, check_addon_update, clean_additional_transform, clean_rig, clean_shape_keys, clear_bone_morph_view, clear_temp_materials, clear_uv_morph_view, convert_materials_for_cycles, convert_to_mmd_camera, convert_to_mmd_lamp, convert_to_mmd_model, create_mmd_model_root_object, create_work_material, display_item_add, display_item_find, display_item_frame_add, display_item_frame_move, display_item_frame_remove, display_item_move, display_item_quick_setup, display_item_remove, display_item_select_current, edge_preview_setup, edit_bone_morph_offset, edit_uv_morph, execute_translation_script, export_pmx, export_vmd, export_vpd, flip_pose, import_model, import_vmd, import_vpd, join_meshes, joint_add, joint_remove, material_morph_offset_init, material_open_sphere_texture, material_open_texture, material_remove_sphere_texture, material_remove_texture, morph_add, morph_copy, morph_move, morph_offset_add, morph_offset_remove, morph_overwrite_from_active_pose_library, morph_remove, morph_slider_setup, move_material_down, move_material_up, object_move, object_select, recalculate_bone_roll, reset_shading, rigid_body_add, rigid_body_remove, rigid_body_select, rigid_body_world_update, sdef_bind, sdef_cache_reset, sdef_unbind, select_bone_morph_offset_bone, separate_by_materials, set_frame_range, set_glsl_shading, set_shadeless_glsl_shading, show_global_translation_popup, translate_mmd_model, update_addon, view_bone_morph, view_uv_morph` — [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。
- 新版功能在 1.0.2 中有没有（源码 + 实测）：

| 功能 | 1.0.2 中的情况 | 证据 |
|---|---|---|
| 模型校验 `validate_bones/morphs/textures`、`fix_*_issues` | 无 | 算子清单里没有，见 [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json) |
| Material Sorter（`move_material_up/down`）和 Meshes Sorter（`object_move`） | 有 | [src/panels/util_tools.py:39-125](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/util_tools.py) |
| 按 bone_id 决定骨序、`fix_bone_order`、`bone_id_move_*` | 无。bone_id 只当引用键用 | `fix_bone_order` 不在 `dir()` 里，`bpy.types.MMD_TOOLS_OT_fix_bone_order` 不存在，见 [实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json) |
| 翻译算子 | 有 `translate_mmd_model`，以及实验性的 `show_global_translation_popup` + `execute_translation_script`；没有 CSV 导入/导出算子，没有 OpenCC | [src/operators/model.py:321-589](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py) |
| SDEF | 有：`sdef_bind/unbind/cache_reset` 和 `mmd_root.use_sdef` | [src/core/sdef.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/sdef.py)、[src/operators/sdef.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/sdef.py) |
| Display Item Quick Setup | 有：`RESET/FACIAL/GROUP_LOAD/GROUP_APPLY`，基于 pose bone groups | [src/operators/display_item.py:232-265](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/display_item.py) |
| Convert Model（`convert_to_mmd_model`） | 有，只有 4 个选项 | [src/operators/model.py:196-319](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py) |
| `mmd_ik_target_override` / `mmd_ik_target_custom` / `mmd_ik_limit_override` / `mmd_ik_limit_custom%d` | 有 | [src/core/pmx/importer.py:359-410](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)、[src/core/pmx/exporter.py:433-526](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py) |
| `ik_loop_factor` | 没有 `mmd_root.ik_loop_factor`，也没有导入选项；只有骨架对象自定义属性 `arm['mmd_ik_loop_factor']` 和算子 `change_mmd_ik_loop_factor` | [exporter.py:482](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[src/operators/misc.py:267-318](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/misc.py)；实测 `MMDRoot_has_ik_loop_factor: false`，见 [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json) |
| `display_connection_type/bone`（表示先属性） | 无 | 实测 `MMDBone_has_display_connection_type: false`，见 [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json) |
| `convert_bone_morph_to_vertex_morph` 等 morph 转换 | 无 | [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json) |
| 模型合并/拆分（`model_join_by_bones` 等） | 无 | [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json) |
| 导出选项 `copy_textures_mode` / `fix_bone_order` / `normal_handling` / `ik_angle_limits` / `export_vertex_colors_as_adduv2` | 无，只有 `copy_textures` 布尔值等 | [src/operators/fileio.py:426-494](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py) |

### Inferences
- 运行时识别：
  - 版本用 `mmd_tools.bl_info["version"]` 做元组比较。
  - 用 `hasattr(mmd_tools, "MMD_TOOLS_VERSION")` 区分 4.x 扩展版。
  - 功能探测用 `"fix_bone_order" in dir(bpy.ops.mmd_tools)` 或 `getattr(bpy.types, "MMD_TOOLS_OT_fix_bone_order", None)`，两种都已实测有效。
  - 不要用 `hasattr(bpy.ops.mmd_tools, x)`：`bpy.ops` 对任意名字都返回包装对象（这是 Blender 的一般行为，本次没有单独实测）。
- 用户随时可能通过内置更新器把 1.0.2 升级到 v2.x，所以插件每次运行都要检测版本，对 1.0.2 和 2.x 走不同分支：两者骨序机制相同，IK 因子存放位置不同。
- 本机代码与官方 zip 一致，所以本笔记的结论适用于任何装了官方 v1.0.2 的环境。
- v1.0.2 发布于 2021-12，比 Blender 3.6 系列早得多，官方从未声明支持 3.6。本次实测在 3.6.15 上可用（见 Q13 第 18 条）。

### Gaps
- v1.0.2 的 release notes 是否真写了 "Support for Blender 3.0"：API body 为空、HTML 摘要有这句，两者矛盾，未能核实。"Specify the support period" 这次提交的具体内容也没看。
- fandom wiki（Manual / Bone Order 页面）两种抓取方式都返回 HTTP 402，没能对照官方文档措辞。

---

## Q2. 模型结构契约：`Model.create`、查找 API、`mmd_type`、`mmd_root`、表示枠初始化

### Takeaway
1.0.2 的对象层级与 4.5.5 相同：
- `mmd_type=="ROOT"` 的 Empty（挂 `mmd_root`）；
- 它的第一个 ARMATURE 子对象是骨架；
- 骨架的递归子对象中，`type=="MESH"` 且 `mmd_type=="NONE"` 的是网格；
- 刚体和 Joint 分别挂在名为 `rigidbodies` / `joints` 的分组 Empty 下。

不同点有四个：
- API 名字不一样：`Model.create(..., armature=...)`、`Model.findRoot`、`Model(root).meshes()`、`Model.initialDisplayFrames`。
- **`Model.create` 不建任何骨骼组或骨骼集合。**
- 影子 / Dummy 骨靠**骨骼层 8/9**，不靠 `mmd_shadow`/`mmd_dummy`；这两个名字在 1.0.2 里根本不存在。
- 没有 `attach_mesh_objects` 这类挂网格 API。

### Cited Findings
- `Model.create` 的精确签名（`inspect.signature` 实测）是 `(name, name_e='', scale=1, obj_name=None, armature=None, add_root_bone=False)` — [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)、[src/core/model.py:599-639](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。它依次做这些事：
  - **建 root**：`bpy.data.objects.new(name=obj_name, object_data=None)`，设 `mmd_type='ROOT'`、`mmd_root.name=name`、`mmd_root.name_e=name_e`、`empty_display_size = scale/0.2`，再 `SceneOp(bpy.context).link_object(root)` 链接到 **`bpy.context.collection`** — [model.py:605-610](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)、[src/bpyutils.py:462-463](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)。
  - **传入 `armature` 时**：`armObj.parent_type='OBJECT'`、`armObj.parent=root`、`root.matrix_world = 原 armObj.matrix_world`、`armObj.matrix_local.identity()`。不传时新建骨架数据 `obj_name` 和对象 `obj_name+'_arm'` — [model.py:612-624](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。
    - 实测：骨架原位置 (1,2,3)、绕 Z 转 1 rad、缩放 0.5 → root 继承了这个变换（location (1,2,3)、scale 0.5）；骨架 `matrix_local` 变成单位阵；骨架和子网格的世界矩阵都不变；骨架对象名不变（仍叫 "Armature"）；已有修改器也不改名 — [实测H](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
  - **骨架对象设置**：`lock_rotation/lock_location/lock_scale` 全部 True，`show_in_front=True`，`display_type='WIRE'` — [model.py:625-627](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)、[实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测H](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
  - **`add_root_bone=True`**：建骨 `全ての親`（head (0,0,0)，tail (0,0,empty_display_size)），设 `name_j='全ての親'`、`name_e='Root'` — [model.py:629-636](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。实测 `scale=1` 时这根骨长 5 单位，`scale=0.08` 时长 0.4 — [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测G](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
  - **收尾**：`bpyutils.select_object(root)` 会切到 OBJECT 模式、取消所有选择、选中并激活 root，然后返回 `Model(root)` — [model.py:638-639](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)、[src/bpyutils.py:42-69](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)。实测创建后活动对象是 root — [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
  - **不创建**骨骼组、表示枠，也不写 `mmd_tools_version` 自定义属性。实测 `bone_groups_after_create == []`、`display_frames_after_create == []` — [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- 查找与遍历（实测方法清单）：
  - `FnModel` 只有 `find_root(obj)`（沿 parent 找 ROOT）、`find_armature(root)`（root.children 里第一个 ARMATURE）、`find_rigid_group`、`find_joint_group`、`all_children`、`child_meshes(obj)`（递归，`type=='MESH' and mmd_type=='NONE'`）、`translate_in_presets`。
  - `Model` 有 `findRoot`、`rootObject()`、`armature()`、`meshes()`、`firstMesh()`、`findMesh(name)`（匹配对象名或网格数据名）、`findMeshByIndex`、`getMeshIndex`、`rigidBodies()`（`is_built` 时还包含骨架下的刚体）、`joints()`、`temporaryObjects()`、`materials()`、`renameBone()`、`allObjects()`。
  - `rigidGroupObject()` / `jointGroupObject()` / `temporaryGroupObject()` 在不存在时会新建名为 `rigidbodies` / `joints` / `temporary` 的 Empty，设 `hide=hide_select=True` 并锁定变换。
  - 证据：[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)、[src/core/model.py:515-1034](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。
  - `Model.__init__` 遇到非 ROOT 对象会抛 `ValueError('must be MMD ROOT type object')` — [model.py:589-597](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。
- 1.0.2 **没有** `FnModel.attach_mesh_objects`，也没有 `Model.attachMeshes`。挂网格只有两条路，且都**不加** Armature 修改器：
  - 算子 `mmd_tools.attach_meshes`：把 `context.visible_objects` 中不属于其它模型的网格的最顶层父对象 parent 到骨架，保持 `matrix_world` — [src/operators/misc.py:231-265](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/misc.py)。
  - `ConvertToMMDModel` 的私有方法 `__attach_meshes_to`：只收编已经带有指向该骨架的 ARMATURE 修改器的对象 — [src/operators/model.py:259-283](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)。
- Convert Model（`mmd_tools.convert_to_mmd_model`）：
  - **选项**：只有 `ambient_color_source`（`DIFFUSE`/`MIRROR`）、`edge_threshold`（0.1）、`edge_alpha_min`（0.5）、`middle_joint_bones_lock`（False）。
  - **poll**：活动对象是 ARMATURE 且不在 EDIT 模式。
  - **执行**：固定 `scale = 1`；若骨架没有 root 父级，就调 `Model.create('New MMD Model', 'New MMD Model', 1, armature=armature)`；然后收编网格并 `loadMorphs()`；对每个材质调 `FnMaterial.convert_to_mmd_material`，并设 `ambient_color = 0.5 × diffuse`（或 mirror 色）；用 freestyle `line_color` 推出描边；最后 `DisplayItemQuickSetup.load_bone_groups` → `initialDisplayFrames(reset=False)` → `load_facial_items`。
  - 证据：[src/operators/model.py:196-319](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)。
  - `create_mmd_model_root_object` 的 `name_j`/`name_e` 默认 "New MMD Model"、`scale` 默认 1.0，内部调用 `Model.create(..., add_root_bone=True)` 再 `initialDisplayFrames()` — [model.py:164-194](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)。
- 实测发现：启用 uuunyaa 时，`Model` 上多出 `clothGroupObject`、`cloths` 两个方法。它们不是 1.0.2 的代码，而是 `mmd_uuunyaa_tools` 在 import 时 monkey-patch 进来的（`inspect.getsourcefile` 指向 `uuu/converters/physics/cloth.py`）— [实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)、[uuu/converters/physics/cloth.py:15-46](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/physics/cloth.py)。
- `Object.mmd_type` 枚举（默认 `NONE`，描述 "Internal MMD type of this object (DO NOT CHANGE IT DIRECTLY)"）共 14 个值：`NONE, ROOT, RIGID_GRP_OBJ, JOINT_GRP_OBJ, TEMPORARY_GRP_OBJ, PLACEHOLDER, CAMERA, JOINT, RIGID_BODY, LIGHT, TRACK_TARGET, NON_COLLISION_CONSTRAINT, SPRING_CONSTRAINT, SPRING_GOAL` — [src/properties/__init__.py:25-49](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/__init__.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。
- 其它挂接的属性：
  - `Object.mmd_root/mmd_camera/mmd_rigid/mmd_joint/is_mmd_glsl_light/mmd_data_query`
  - `Material.mmd_material`
  - `PoseBone.mmd_bone/is_mmd_shadow_bone/mmd_shadow_bone_type/mmd_ik_toggle`
  - Blender 2.80+ 下还给 `Object` 打了两个补丁属性：`select`（get/set 映射到 `select_get/select_set`）和 `hide`（映射到 `hide_get/hide_set`，set 时同时置 `hide_viewport=False`）
  - 证据：[src/properties/__init__.py:50-81](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/__init__.py)。
- `mmd_root`（`MMDRoot`）实测属性全集：`name, name_e, comment_text, comment_e_text, show_meshes, show_rigid_bodies, show_joints, show_temporary_objects, show_armature, show_names_of_rigid_bodies, show_names_of_joints, use_toon_texture(True), use_sphere_texture(True), use_sdef(True), use_property_driver(False), is_built, active_rigidbody_index, active_joint_index, display_item_frames, active_display_item_frame, material_morphs, uv_morphs, bone_morphs, vertex_morphs, group_morphs, active_morph_type(默认 vertex_morphs), active_morph, active_mesh_index` — [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)、[src/properties/root.py:268-450](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/root.py)。
  - 相比 4.5.5，**缺** `ik_loop_factor`、`show_japanese_name/show_english_name`、`active_bone_index`、`morph_panel_show_settings`、`translation` — 对照 [02 笔记 Q1](02_mmd_tools导出契约.md)。
  - `comment_text/comment_e_text` 存的是 `bpy.data.texts` 里文本块的名字 — [src/core/pmx/exporter.py:1219-1227](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
- 表示枠初始化 `Model.initialDisplayFrames(reset=True)` — [model.py:645-669](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - `reset=True` 时先清空。
  - 确保存在 `Root`（name_e `Root`，`is_special=True`）和 `表情`（name_e `Facial`，`is_special=True`）。
  - 若 Root 为空且骨架有骨，就加入 `arm.data.bones[0].name`。
  - `reset=False` 时把这两个枠移到索引 0 和 1。
  - 实测结果：`[('Root','Root',True,[('BONE','全ての親')]), ('表情','Facial',True,[])]` — [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- 导入器建立的结构 — [src/core/pmx/importer.py:94-98,108-110,131-132,769-774,851-856](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)：
  - 网格对象 `<root名>_mesh`，parent=骨架。
  - 每根 PMX 骨一个同名顶点组（按 PMX 顺序），外加 `mmd_edge_scale`、`mmd_vertex_order`。
  - ARMATURE 修改器**名为 `mmd_bone_order_override`**（4.5.5 里叫 `mmd_armature`）。
  - 即使不导入 MESH（types 不含 MESH），也会建一个 0 顶点网格，专门承载骨序顶点组。实测导入 `{'ARMATURE','DISPLAY'}` 得到 `('…_mesh', ['mmd_bone_order_override:ARMATURE'], 0 顶点)` — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
  - 还会写 `root['import_folder']=PMX 所在目录`，并建文本块 `<obj_name>` / `<obj_name>_e` 存注释。
  - root 名来自 `bpy.path.display_name(filepath)`，会把 `_` 换成空格并首字母大写。实测 "mmd_tools_102_rt_in.pmx" → "Mmd Tools 102 Rt In" — [importer.py:74-92](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)、[实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。

### Inferences
- 插件收编 XPS 骨架用 `Model.create(name_j, name_e, scale, obj_name, armature=xps_armature, add_root_bone=False)`。注意关键字参数在 1.0.2 叫 `armature`，4.5.5 叫 `armature_object`，需要写兼容层。收编后插件还要自己做三件事：
  1. 把网格 parent 到骨架，并保证每个网格有 ARMATURE 修改器；
  2. 建骨序承载网格（见 Q3）；
  3. 调 `rig.initialDisplayFrames()`。
- XPS 骨架若带旋转或缩放，`Model.create` 会把它转移给 root，导出时会被烘焙进 PMX（导出用的是 `arm.matrix_world`）。所以转换前应先对 XPS 骨架和网格 Apply 变换，让 root 保持单位矩阵。
- 题设说"Blender 3.6 下 `mmd_shadow`/`mmd_dummy` 是 pose bone groups"，这对 1.0.2 不成立：它用的是骨骼层（见 Q4）。检查器不应去找这两个组名。

### Gaps
- `Object.children` 的顺序会影响 `find_armature`（root 下有多个骨架时）和骨序面板选中哪个网格；Blender 3.6 中 `children` 的排序规则没有实测。

---

## Q3. 骨骼顺序（BONE ORDER）与変形階層

### Takeaway
1.0.2 的导出骨序**只由一个机制决定**：
1. 导出时网格先按对象名排序；在其中找到第一个带有名为 **`mmd_bone_order_override`** 修改器的网格。
2. 按这个网格的**顶点组索引**给 pose bones 排序。
3. 在该网格上没有对应顶点组的骨（例如 IK 骨、控制骨）排到最后，彼此之间保持 `pose.bones` 原有顺序。
4. 影子骨直接跳过。

如果没有这样的网格，骨序就是 `arm.pose.bones` 的顺序；实测这是骨架层级的深度优先先序，**不是**骨的创建顺序。

`bone_id` 不参与排序。`transform_order` 和 `transform_after_dynamics` 原样写进 PMX，1.0.2 不做任何自动重排或修正（没有 `fix_bone_order`）。

### Cited Findings
- 导出代码。没有专门的 helper 函数，逻辑直接内联在 `__exportBones` 里 — [src/core/pmx/exporter.py:334-343](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  ```python
  vtx_grps = {}
  for mesh in meshes:                      # meshes 已按 x.name 排序
      if mesh.modifiers.get('mmd_bone_order_override', None):
          vtx_grps = mesh.vertex_groups
          break
  class _Dummy: index = float('inf')
  sorted_bones = sorted(pose_bones, key=lambda x: vtx_grps.get(x.name, _Dummy).index)
  ```
  - 网格先排序：`meshes = sorted(args.get('meshes', []), key=lambda x: x.name)` — [exporter.py:1230](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
  - 影子骨跳过：`if p_bone.is_mmd_shadow_bone: continue` — [exporter.py:358-360](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
  - 1.0.2 中不存在 `__get_bone_order`、`bone_order_mesh_object` 之类的函数。全目录 grep `bone_order` 只命中 exporter、importer、sdef 和 util_tools 面板（本会话 grep）。
- 导出器只认修改器的**名字**：不检查修改器类型，也不要求该网格有顶点（0 顶点网格实测可用）— [exporter.py:337](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- 实测 D（显式骨序网格）— [实测D](assets/08_mmd_tools_1.0.2/verify_live_102.json)：
  - 骨按 C、A、B、D_shadowless 的顺序创建；网格上只有顶点组 A、B、C，并带修改器 `mmd_bone_order_override` → 导出顺序为 `A, B, C, D_shadowless`（没有顶点组的 D 排在最后）。
  - 用 `bpy.ops.object.vertex_group_move(direction='UP')` 连按两次，把 C 移到首位 → 导出顺序变为 `C, A, B, D_shadowless`。
  - 把修改器改名为 "Armature" → 回退为 pose.bones 顺序。
  - 权重里的骨索引也按导出后的骨序同步：顶点 0 有 A=1.0、B=0.5 → BDEF2，骨 `[0,1]`，权重 0.6667。
- 实测 G（没有骨序网格）— [实测G](assets/08_mmd_tools_1.0.2/verify_live2_102.json)：
  - 创建顺序 `R, X1, R2, X2, Y1`，其中 X1、X2 的父骨是 R，Y1 的父骨是 X1，R2 是根骨。
  - `data.bones`、`pose.bones` 和导出顺序三者都是 `R, X1, Y1, X2, R2`，即层级深度优先先序，兄弟骨按加入顺序排列。
  - 实测 B 中，导入后 `data.bones` 里的影子骨插在其父骨子树的末尾（例如 `_dummy_左肩C` 排在 `左腕` 之后），同样符合这个规律 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- 往返实测 B：一个 21 骨的 PMX（含付与、IK、変形階層为 1 的足D）导入后再导出，骨序与输入逐一相同，骨数 21=21（4 根影子骨被跳过）。这一结果由导入器建立的 `mmd_bone_order_override` 网格的顶点组保证 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- Bone Order 面板（`OBJECT_PT_mmd_tools_bone_order`，标签 "Bone Order"，位于侧栏 MMD 页）— [src/panels/util_tools.py:297-339](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/util_tools.py)：
  - 用 `next((i for i in armature.children if 'mmd_bone_order_override' in i.modifiers), None)` 找骨序网格。它**只看骨架的直接子对象**，源码注释为 `#TODO consistency issue`。
  - 找到时调用 `template_list("MMD_TOOLS_UL_ModelBones", "", bone_order_object, 'vertex_groups', bone_order_object.vertex_groups, 'active_index')`；只有当该网格是活动对象时，才显示 Blender 自带的 `object.vertex_group_move`（`direction` UP/DOWN）按钮。
  - 找不到时列出 `armature.pose.bones`，并显示 `No mesh object with "mmd_bone_order_override" modifier`。
  - 1.0.2 没有任何 mmd_tools 自己的骨序算子 — [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。`mmd_tools.object_move` 只用来给网格、刚体和 Joint 改名排序，与骨序无关 — [src/operators/misc.py:35-94](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/misc.py)。
- 面板对每根骨显示的内容 — [util_tools.py:215-283](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/util_tools.py)：
  - 顶点组序号。
  - 父骨序号：rank 违规时显示 `ERROR`，否则显示 `INFO`（父序号更大时）或 `FILE_PARENT`。
  - 付与亲序号：图标 `IPO_QUAD` 表示转+移，`IPO_EXPO` 表示回転付与，`IPO_LINEAR` 表示移動付与；违规时显示 `ERROR`。
  - 相关 IK 的 `mmd_ik_toggle` 开关：`LINKED` 表示链节，`HOOK` 表示目标，`ERROR` 表示序号无效或链节排在 IK 骨之后，`QUESTION` 表示其它情况。
  - `transform_after_dynamics` 开关和 `transform_order` 滑块。
  - rank 公式是 **`index + transform_order*len(pose_bones)`**，不含 `transform_after_dynamics`。这些都只是警告显示，不会自动修正。
- `transform_order`（Int，min 0，max 100，soft_max 7，"Deformation tier"）写到 `pmx_bone.transform_order`；`transform_after_dynamics` 写到 `pmx_bone.transAfterPhis` — [src/properties/bone.py:63-81](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)、[exporter.py:377-378](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。导入器原样写回 — [src/core/pmx/importer.py:424-425](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)。
- `bone_id`（Int，默认 -1，描述 "Unique ID for the reference of bone morph and rotate+/move+"）在 1.0.2 中只在以下地方使用，导出排序不读它 — [src/core/bone.py:37-52](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)、[properties/bone.py:22-40](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)、[properties/morph.py:105-126](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/morph.py)：
  - `FnBone.bone_id`：值为 -1 时取 max+1 并写回。
  - `FnBone.from_bone_id`：返回**第一个**匹配的骨。
  - 付与目标和骨骼 morph 的 getter/setter。
  - 导入器也**不**给骨赋 bone_id：实测导入后只有被付与引用的目标骨有 bone_id（0..4），其余都是 -1 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- 与 4.5.x 对照：4.5.x 按 `bone_id` 升序导出，并提供 `fix_bone_order` / `realign_bone_ids`；其 `fix_bone_order` 会把旧版 `mmd_bone_order_override` 修改器按顶点组顺序迁移成 bone_id，并把修改器改名为 `mmd_armature` — [02 笔记 Q2](02_mmd_tools导出契约.md)。v2.10.3 仍用顶点组机制 — [v2.10.3 exporter:338-344](https://raw.githubusercontent.com/MMD-Blender/blender_mmd_tools/v2.10.3/mmd_tools/core/pmx/exporter.py)。
- 其它依赖这个修改器名字的功能：SDEF 的 `FnSDEF.has_sdef_data` 只认 `mmd_bone_order_override` — [src/core/sdef.py:76-82](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/sdef.py)。
- Blender 3.6 提供 `bpy.ops.object.vertex_group_sort(sort_type='NAME'|'BONE_HIERARCHY')` — [实测K](assets/08_mmd_tools_1.0.2/verify_live3_102.json)。

### Inferences
- **推荐的骨序设定方法**：建一个专用的"骨序承载网格"。
  - **网格本身**：0 顶点即可，作为骨架的**直接子对象**。
  - **对象名**：排在所有网格最前，例如 `000_mmd_bone_order`（与 `MoveObject` 的前缀格式一致）。
  - **顶点组**：按目标 PMX 顺序依次 `vertex_groups.new(name=<Blender 骨名>)`，覆盖**全部**非影子骨，包括 IK 骨、控制骨和 D 骨。
  - **修改器**：`modifiers.new('mmd_bone_order_override', 'ARMATURE')`，`object=骨架`。
  - **其它网格**：真实 XPS 网格的修改器改成普通名字（例如 "Armature"），保证全模型只有承载网格带这个名字。
- 这样做的理由：
  1. 导出（按名排序取第一个）和面板（取第一个直接子对象）都会选中它。
  2. XPS 网格各自只有一部分顶点组，不适合承载完整顺序。
  3. 顶点组顺序只能靠创建顺序或 `vertex_group_move` 调整，新建最可控。
  4. 推论（未实测）：若用户之后执行 `mmd_tools.join_meshes`（按名排序、以第一个为活动对象合并），承载网格会成为合并目标，其顶点组顺序与修改器得以保留。
- 要改已有顺序时，最稳妥的是**删掉承载网格再按新顺序重建**；不要依赖 `vertex_group_move`，它需要活动对象上下文，而且是 O(n²)。
- 骨重命名：用 `Model.renameBone()`，或直接改 `pose_bone.name`，都能让顺序保持有效。后者依赖 Blender 自动重命名骨架子网格（及带 Armature 修改器网格）上的同名顶点组，这一点本次未实测。
- 为兼容 4.5.x 和将来的升级，同时把 `mmd_bone.bone_id` 设为目标 PMX 索引（0..N-1，唯一）。注意**先设 bone_id，再设付与目标**：setter 会读取目标骨当时的 bone_id 存进 `additional_transform_bone_id`；顺序反了，引用就会指向错误的骨（见 Q4）。
- 変形階層规则需要我们自己保证，1.0.2 不会修正：
  - PMX 规范的变形顺序是"物理前/后 → 変形階層 → Index"。
  - 因此父骨、付与亲、IK 链节都应排在被影响的骨之前。
  - 足D 系通常设 `transform_order=1`，并排在 IK 骨之后。
  - 依据见 [03 笔记](03_MMD骨骼规范与准标准骨.md) 引用的 PMX 仕様和 korarei 的说明。
- VMD 导出（`ExportVmd`）在没有 morph 滑块时会用 `rig.firstMesh()` 取表情形态键。如果承载网格恰好是第一个子网格，表情动画可能导不出来（推论，未实测），因此该网格不应该作为 children 中的第一项去承担表情。

### Gaps
- 未实测：在编辑模式新增骨或改父骨之后，`pose.bones` 的顺序是否总与 `data.bones` 的深度优先序一致（本次三组样例都一致）。
- 未实测 `join_meshes` 对承载网格的实际效果。

---

## Q4. 付与（回転付与 / 移動付与；mmd_tools 称 Additional Transform / Rotate+ / Move+）、Dummy 骨与影子骨深挖

### Takeaway
- **导出只看属性**：付与数据存放在 `pose_bone.mmd_bone` 上的 6 个属性里（两个标志、目标、目标 bone_id、影响度、dirty）。导出只读这些属性，与 Blender 约束、影子骨都无关。
- **Blender 侧只是预览**，由 `FnBone.apply_additional_transformation(armature)` 生成。对每根有付与（或 dirty）的骨：
  - 建 TRANSFORM 约束 `mmd_additional_rotation`（±π 映射到 ±π×影响度）和/或 `mmd_additional_location`（±100 映射到 ±100×影响度），空间为 LOCAL→LOCAL。
  - 如果本骨与目标骨的 X、Y 轴点积都 >0.99，约束直接以目标骨为 subtarget。
  - 否则新建两根辅助骨，约束改为指向 `_shadow_<骨名>`：
    - `_dummy_<骨名>`：父骨=目标骨，放在第 9 层，`mmd_shadow_bone_type='DUMMY'`；
    - `_shadow_<骨名>`：父骨=目标骨的父骨，放在第 8 层，类型 `'SHADOW'`，带 COPY_TRANSFORMS 约束 `mmd_tools_at_dummy`。
- **负影响度**只是把 to 区间反过来（to_min=+π，to_max=−π）。1.0.2 不设置 euler 顺序和混合模式，保持 Blender 默认值 AUTO/AUTO/ADD。
- **没有任何自动 handler**：dirty 标志只在调用 apply 时才被消费。

### Cited Findings
**属性（`MMDBone`，[src/properties/bone.py:43-183](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)）**
- `has_additional_rotation` / `has_additional_location`：Bool，默认 False，`update=_updateMMDBoneAdditionalTransform` — [bone.py:140-152](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)。
- `additional_transform_bone`：String，读写都经过 bone_id — [bone.py:22-40,154-160](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)：
  - getter 读 ID-prop `additional_transform_bone_id`；值 <0 时返回 `''`，否则返回 `FnBone.from_bone_id(arm, id)` 找到的骨名。
  - setter 先置 `is_additional_transform_dirty=True`；名字不在 `arm.pose.bones` 里时，**静默写入 -1**，不报错。
  - 否则写入 `FnBone(pose_bone).bone_id`；目标骨的 bone_id<0 时，会当场给它分配 max+1。
- `additional_transform_bone_id`：Int，默认 -1，update 回调同上 — [bone.py:162-166](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)。
- `additional_transform_influence`：Float，默认 1，soft_min -1，soft_max 1，`update=_updateAdditionalTransformInfluence` — [bone.py:168-175](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)。
- `is_additional_transform_dirty`：Bool，默认 **True**。UI 中处于 dirty 状态时，"Rotate +/Move +" 那一行会显示 `ERROR` 图标 — [bone.py:177-180](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)、[src/panels/prop_bone.py:86-93](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/prop_bone.py)。
- update 回调的行为 — [bone.py:9-20](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)、[src/core/bone.py:329-336](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)：
  - `_updateMMDBoneAdditionalTransform`：置 dirty；**只有当 `context.active_pose_bone` 正好是这根骨**时，才立即调用 `FnBone.apply_additional_transformation(prop.id_data)`。
  - `_updateAdditionalTransformInfluence`：若是活动骨，只改约束的 min/max（`update_additional_transform_influence`）；否则只置 dirty。
- 实测：设置目标之后，被引用的**目标骨**获得 bone_id（両目→0，左肩P→1，左足→2），被付与的骨自身仍是 -1；此时 dirty=True，还没有约束 — [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)。

**`FnBone.apply_additional_transformation(armature)`（[src/core/bone.py:262-294](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)）**
- 选骨：非影子骨，且满足 `has_additional_rotation or has_additional_location` 或 `is_additional_transform_dirty` — [bone.py:265-272](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)。
- 对每根选中的骨调用 `__setup_constraints` — [bone.py:296-327](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)：
  - 若 `not target_bone`、两个标志都为 False、或 `influence == 0`：删除两个约束；只要确实删掉了约束，就登记一个 `_AT_ShadowBoneRemove`。
  - 否则登记一个 `_AT_ShadowBoneCreate(bone, target)`，并配置约束。
- 约束配置函数 `__config(name, mute, map_type, value)` — [bone.py:315-325](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)：
  - `mute` 为真时删除该约束；
  - 否则：`TransformConstraintOp.create(constraints, name, map_type)`，设 `c.target = 骨架对象`，把约束加入影子骨的待改 subtarget 池，再 `TransformConstraintOp.update_min_max(c, value, influence)`。
  - 旋转用参数 `('mmd_additional_rotation', 'ROTATION', pi)`，位移用 `('mmd_additional_location', 'LOCATION', 100)`。
- 之后用 `with bpyutils.edit_object(armature)` 进入编辑模式，更新或删除影子骨；再回到姿态侧设置标志与约束；最后把所有被处理骨的 dirty 置为 False — [bone.py:281-294](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)。
- `TransformConstraintOp.create` — [src/bpyutils.py:342-357](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)：
  - 已有同名约束且类型是 TRANSFORM 时**复用**；类型不符就删掉重建。
  - 设置 `use_motion_extrapolate=True`、`target_space=owner_space='LOCAL'`、`map_from=map_to=map_type`、`map_to_x/y/z_from='X'/'Y'/'Z'`、`influence=1`。
  - **不**设置 `from_rotation_mode`、`to_euler_order`、`mix_mode_rot`。
- `update_min_max`：`from_min_*=-value`、`from_max_*=value`、`to_min_*=-value*influence`、`to_max_*=value*influence`；旋转用带 `_rot` 后缀的属性 — [bpyutils.py:359-386](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)。
- 实测约束（Blender 3.6）— [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)：
  - 字段：`type TRANSFORM, name mmd_additional_rotation, target <骨架>, influence 1.0, map_from/map_to ROTATION, owner_space/target_space LOCAL, use_motion_extrapolate True, from_rotation_mode AUTO, to_euler_order AUTO, mix_mode_rot ADD`。
  - 影响度 1：from ±3.1416 → to ±3.1416。
  - 影响度 −1（左肩C←左肩P）：`to_min_x_rot=+3.1416, to_max_x_rot=−3.1416`。

**Dummy / 影子骨（`_AT_ShadowBoneCreate`，[src/core/bone.py:349-418](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)）**
- 对齐判定 `__is_well_aligned` 的条件是 `bone0.x_axis.dot(bone1.x_axis) > 0.99 and bone0.y_axis.dot(bone1.y_axis) > 0.99`。若 `bone != target_bone` 且对齐，就删除已有的 `_dummy_/_shadow_` 并返回，不建影子骨 — [bone.py:357-358,368-373](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)。
- 不对齐时，编辑骨的处理 — [bone.py:375-395](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)：

| 骨 | 创建（不存在时） | 每次更新 |
|---|---|---|
| `_dummy_<骨名>` | `layers=[x == 9 …]`（只在索引 9，即第 10 层），`use_deform=False` | `parent=目标骨`；`head=目标骨.head`；`tail=head + (本骨.tail − 本骨.head)`；`roll=本骨.roll` |
| `_shadow_<骨名>` | `layers=[x == 8 …]`（索引 8），`use_deform=False` | `parent=目标骨.parent`；head/tail 与 dummy 相同；`roll=本骨.roll` |

- 姿态侧的处理 — [bone.py:397-418](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)：
  - 若 `_shadow_` 不存在（对齐的情况），约束 subtarget 设为目标骨。
  - 否则：dummy 设 `is_mmd_shadow_bone=True`、`mmd_shadow_bone_type='DUMMY'`；shadow 设 `True` / `'SHADOW'`。
  - shadow 上若没有 `mmd_tools_at_dummy`，新建 COPY_TRANSFORMS 约束：`target=骨架`、`subtarget=_dummy_<骨名>`、`target_space=owner_space='POSE'`。
  - 付与约束的 subtarget 设为 `_shadow_<骨名>`。
- `_AT_ShadowBoneRemove` **按名字**删除 `_dummy_<名>` 和 `_shadow_<名>`，不检查 `is_mmd_shadow_bone` — [bone.py:339-347](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)。
- 实测（导入 PMX）哪些付与会生成影子骨 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)：
  - `左肩C←左肩P(−1)`：会生成。原因是 `左肩P` 属于 `AUTO_LOCAL_AXIS_SEMI_STANDARD_ARMS`，导入器自动改了它的 roll，X 轴不再对齐。
  - `左足首D←左足首`：会生成，两骨方向不同。
  - `左目←両目`、`左足D←左足`、`左ひざD←左ひざ`：都对齐，不生成，约束直接指向目标骨。
- 实测影子骨属性 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)：

| 骨 | 类型 | 父骨 | 层 | 约束 |
|---|---|---|---|---|
| `_dummy_左肩C` | `DUMMY` | `左肩P` | `[9]` | 无 |
| `_shadow_左肩C` | `SHADOW` | `上半身`（即 左肩P 的父骨） | `[8]` | `COPY_TRANSFORMS mmd_tools_at_dummy → _dummy_左肩C (POSE/POSE)` |
| `_dummy_左足首D` | `DUMMY` | `左足首` | `[9]` | 无 |
| `_shadow_左足首D` | `SHADOW` | `左ひざ` | `[8]` | `mmd_tools_at_dummy` |

  - 四根影子骨都是 `is_mmd_shadow_bone True`、`use_deform False`，没有骨骼组。
  - `左肩C` 的 `mmd_additional_rotation.subtarget == '_shadow_左肩C'`。
  - 骨架的可见层实测只有 `[0]`，所以第 8、9 层默认看不见 — [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- `rename_bones=True` 导入时，影子骨按**改名后的** Blender 骨名生成（`_dummy_肩C.L`、`_shadow_肩C.L`…）。原因是导入器先执行 `__renameLRBones`，再执行 `apply_additional_transformation` — [实测C](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[importer.py:857-864](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)。

**`FnBone.clean_additional_transformation(armature)`（[src/core/bone.py:237-260](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)）**
- 对所有 pose bone：
  1. 置 `is_additional_transform_dirty=True`；
  2. 删除约束 `mmd_additional_rotation` 和 `mmd_additional_location`；
  3. 若删到了旧版的 `mmd_additional_parent` 约束，就把 `bone.use_inherit_rotation` 设回 True；
  4. 最后删除满足 `is_mmd_shadow_bone and mmd_shadow_bone_type ∈ {'DUMMY','SHADOW','ADDITIONAL_TRANSFORM','ADDITIONAL_TRANSFORM_INVERT'}` 的骨。
- 实测：clean 之后约束全部清掉，所有骨（包括没有付与的 `センター`）都变成 dirty=True；再 apply 一次即可恢复 — [实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- `mmd_shadow_bone_type` 的全部取值 — [src/core/morph.py:575-590](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/morph.py)、[exporter.py:528-538](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、本会话 grep：
  - 1.0.2 只会**创建**三种：`'DUMMY'`、`'SHADOW'`（付与用）和 `'BIND'`（morph 滑块的 `.dummy_armature` 中的 `mmd_bind*` / `mmd_bind_ctrl_base`，它们在另一个骨架对象里）。
  - `'ADDITIONAL_TRANSFORM'`、`'ADDITIONAL_TRANSFORM_INVERT'` 只出现在 clean 的删除集合里。
  - `'IK_TARGET'` 只被导出器读取（`__get_ik_control_bone` 遇到时取其父骨）。
  - 后三种都是旧版遗留，1.0.2 从不创建。

**影子骨在哪些地方被排除**
- 这些地方都会跳过 `is_mmd_shadow_bone` 为真的骨：
  - 导出的 `__exportBones`、`__exportIK`、`__get_ik_target_bone`
  - `translate_bone`、`get_selected_pose_bones`
  - `apply_bone_fixed_axis`、`apply_bone_local_axes`、`apply_auto_bone_roll`
  - Bone Order 面板的骨数计数；骨属性面板（会显示 "MMD Shadow Bone!"）
  - 证据：[exporter.py:358-360,485,492-494,550](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[src/operators/model.py:449-454](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)、[src/core/bone.py:65-72,96,154,186](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)、[util_tools.py:157-160](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/util_tools.py)、[prop_bone.py:38-40](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/prop_bone.py)。
- 影子骨没有顶点组，所以即使不跳过，它们也会排在骨序末尾。

**UI 与算子（"transform bone" 在 1.0.2 中指什么）**
- 骨属性面板 "MMD Bone Tools"：有 `Rotate +` / `Move +` 两个开关、`additional_transform_bone` 的骨名搜索框和 `Influence` 滑块 — [src/panels/prop_bone.py:86-93](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/prop_bone.py)。
- 3D 视图 MMD 侧栏的 Operator 面板中，"Bone Constraints:" 下有两个按钮 — [src/panels/tool.py:66-71](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/tool.py)、[src/operators/model.py:72-100](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)、[src/core/model.py:1417-1425](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - `Apply` → `mmd_tools.apply_additional_transform`（"Translate appended bones of selected object for Blender"），内部调用 `Model.applyAdditionalTransformConstraints` → `FnBone.apply_additional_transformation(arm)`。
  - `Clean` → `mmd_tools.clean_additional_transform`（"Delete shadow bones of selected object and revert bones to default MMD state"）。
  - 实测：以 root 为活动对象调用 `bpy.ops.mmd_tools.apply_additional_transform()`，返回 `{'FINISHED'}` — [实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
- `bone_fixed_axis_setup` / `bone_local_axes_setup` 选 `APPLY` 时，改完 roll 后会再调用一次 `apply_additional_transformation` — [model.py:126-128,157-159](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)。

**导入器如何设置付与（[src/core/pmx/importer.py:444-450,864](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)）**
```python
if pmx_bone.hasAdditionalRotate or pmx_bone.hasAdditionalLocation:
    bone_index, influ = pmx_bone.additionalTransform
    mmd_bone.has_additional_rotation = pmx_bone.hasAdditionalRotate
    mmd_bone.has_additional_location = pmx_bone.hasAdditionalLocation
    mmd_bone.additional_transform_influence = influ
    if 0 <= bone_index < len(pose_bones):
        mmd_bone.additional_transform_bone = pose_bones[bone_index].name
...
FnBone.apply_additional_transformation(self.__armObj)   # 骨阶段末尾一次性应用
```
- 骨属性循环按 `transform_order` 排序后遍历 — [importer.py:418](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)。
- 实测往返：以下付与全部原样回到 PMX，`additionalTransform` 是目标骨在导出顺序中的索引 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)：
  - `左目←両目 1.0`
  - `左肩C←左肩P −1.0`
  - `左足D/ひざD/足首D←足/ひざ/足首 1.0`（transform_order 1）

**导出器如何读回（[src/core/pmx/exporter.py:367-369,409-417](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)）**
```python
pmx_bone.hasAdditionalRotate = mmd_bone.has_additional_rotation
pmx_bone.hasAdditionalLocation = mmd_bone.has_additional_location
pmx_bone.additionalTransform = [mmd_bone.additional_transform_bone, mmd_bone.additional_transform_influence]
...
i.additionalTransform[0] = r.get(i.additionalTransform[0], -1)   # Blender 骨名 → 导出索引
```
- 两个标志**无条件**写出。目标为空、或指向没有导出的骨（例如影子骨）时，索引变成 **-1**。
- PMX 层的 `Bone.save` 只要任一标志为真，就会写入 `(index, influence)` — [exporter.py:367-369,417](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[src/core/pmx/__init__.py:1048-1101](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/__init__.py)。对照：4.5.5 在目标为空时会清掉标志并给出警告，见 [02 笔记 Q2](02_mmd_tools导出契约.md)。
- PMX 层只支持 0x0100 / 0x0200 两个标志：不写 0x0080（ローカル付与），也从不设置外部親（`externalTransKey`）— [src/core/pmx/__init__.py:1056-1068](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/__init__.py)。

**外部插件的现成样例**
- 本机的 `xps_to_mmd-main`，就是 [07 笔记](07_社区实际工作流与现有转换器.md) 中的 killinux/xps_to_mmd。它在 足D、肩C、捩骨 等算子中：
  - 直接写 `mmd_bone.has_additional_rotation=True`、`additional_transform_bone=<源骨>`、`additional_transform_influence=1.0/−1.0/0.25…`；
  - 在一键流程的最后调用 `bpy.ops.mmd_tools.apply_additional_transform()`；
  - 还预先手工建了同名 TRANSFORM 约束，设 `from_rotation_mode='XYZ'`、`to_euler_order='XYZ'`、`mix_mode_rot='ADD'`。由于 `TransformConstraintOp.create` 复用同名约束、且不改这三个字段，这些设置会被保留。
  - 证据：[xps_to_mmd-main/operators/add_leg_d_bones_operator.py:250-285](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/xps_to_mmd-main/operators/add_leg_d_bones_operator.py)、[operators/one_click_operator.py:137-142](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/xps_to_mmd-main/operators/one_click_operator.py)、[src/bpyutils.py:342-357](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)。

### Inferences
- **外部插件设置付与的正确顺序**：
  1. （可选）先给全部骨分配唯一的 `bone_id`。
  2. 对每根骨，按导入器的顺序写入：`has_additional_rotation` / `has_additional_location` → `additional_transform_influence` → 最后 `additional_transform_bone=<目标 Blender 骨名>`。写完读回确认非空，因为 setter 遇到不存在的名字会静默写 -1。
  3. 写属性时，确保 `context.active_pose_bone` 不是正在修改的骨（例如处于 OBJECT 模式，或骨架没有活动骨），避免每改一个属性就触发一次编辑模式往返。
  4. 全部写完后，调用一次 `FnBone.apply_additional_transformation(armature)`；或者调用 `bpy.ops.mmd_tools.apply_additional_transform()`，这需要活动对象属于该模型。
  5. 之后如果又改了骨的 roll、头尾或父子关系（例如 Apply Fixed/Local Axes、`recalculate_bone_roll`），再 apply 一次，必要时先 clean。
- 导出并不需要约束或影子骨：只要属性正确，跳过第 4 步也能得到正确的 PMX。apply 只是为了在 Blender 里预览，以及让检查器看到与导入器一致的状态。
- 1.0.2 的预览是 Euler 重映射加 ADD 混合（Blender 默认值），多轴大角度时与 MMD 的结果不完全一致。不要用 Blender 预览判断付与是否正确，应检查属性和导出结果。
- 绝不要给真实骨起带 `_dummy_` / `_shadow_` 前缀的名字，apply/clean 会按名字把它们删掉。
- 复制骨或合并骨架时，要把复制出来的 `bone_id` 重置为 -1。否则 `from_bone_id` 只返回第一个匹配的骨，付与和骨骼 morph 的引用会串到错误的骨上。
- bone_id 与付与的先后有坑：付与里存的是目标骨的 bone_id 数值。如果之后重新给 bone_id 编号，必须把 `additional_transform_bone` 重新写一遍。

### Gaps
- 未实测：写属性时 `context.active_pose_bone` 恰好就是该骨、从而立即 apply 的那条路径（代码逻辑清楚，但没跑过）。
- 未定量比较 1.0.2（AUTO/ADD）与 4.5.5（ZYX/XYZ/AFTER）在复杂旋转下的预览误差。

---

## Q5. IK 表示（导入 `__applyIk` / 导出 `__exportIK`）

### Takeaway
与 4.5.5 基本一致：
- IK 约束放在 IK 链的第一个 link 上，也就是 IK 目标骨的父骨（例如 `左ひざ`）。约束设置为 `target=骨架`、`subtarget=IK 骨`、`chain_count=link 数`、`use_tail=True`。
- 目标骨上放一个静音的 DAMPED_TRACK `mmd_ik_target_override`（subtarget=约束骨）。
- 单位角存放在**约束所在骨**的 `mmd_bone.ik_rotation_constraint` 里。

1.0.2 的不同点：

| 项目 | 1.0.2 的行为 |
|---|---|
| 导入时的迭代次数 | `iterations = loopCount`，**不乘**任何因子；也没有 `ik_loop_factor` 导入选项 |
| 导出时的迭代因子 | 取自骨架对象自定义属性 `arm['mmd_ik_loop_factor']` |
| `mmd_ik_limit_override` 的空间 | `owner_space` 为 `'POSE'` |
| 导出读取的角度限制 | 链节骨上"第一个未静音的 LIMIT_ROTATION"，不看约束名字 |
| `ik_angle_limits` 导出选项 | 没有 |

### Cited Findings
- 导入：先找出三根骨 — [src/core/pmx/importer.py:317-357](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)：
  - `ik_bone=pose_bones[index]`、`ik_target=pose_bones[pmx_bone.target]`、`ik_constraint_bone=ik_target.parent`。
  - 若 `ik_links[0]` 就是目标骨，则删去这一节，并打 warning "fix IK settings"。
  - `is_valid_ik = (ik_constraint_bone == ik_links[0] 对应的骨)`。
  - 链节之间不满足父子关系时，放弃这条 IK。
- 在目标骨上建 `DAMPED_TRACK` — [importer.py:359-372](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)：
  - 默认设置：`name='mmd_ik_target_override'`、`mute=True`、`influence=0`、`target=骨架`、`subtarget=ik_constraint_bone.name`；单位角写到 **`ik_constraint_bone.mmd_bone.ik_rotation_constraint`**。
  - 若 `not is_valid_ik`，或约束骨上已有有效的 IK 约束：改名为 `'mmd_ik_target_custom'`，`subtarget=ik_bone.name`，单位角改写到 **IK 骨**上。
- 建 IK 约束：`ikConst = Model.create_ik_constraint(ik_constraint_bone, ik_bone)`，即 `bone.constraints.new('IK')`、`target=self.__arm`、`subtarget=ik_bone.name`；然后 `iterations = pmx_bone.loopCount`、`chain_count = len(ik_links)`。`not is_valid_ik` 时设 `pole_target=骨架`，故意让它成为无效设置 — [importer.py:374-378](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)、[src/core/model.py:876-892](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。
- 角度限制 — [importer.py:379-410](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)：
  - custom 情况，或该 link 已被其它 IK 使用：在 IK 骨上加一个静音的 LIMIT_ROTATION `mmd_ik_limit_custom{idx}`。
  - 其它情况：
    1. 给 link 骨设 `use_ik_limit_x/y/z=True`，`ik_min/max_*` 取 `convertIKLimitAngles(min, max, bone.matrix_local)` 的结果；
    2. 同时加一个 LIMIT_ROTATION `mmd_ik_limit_override`：`mute = not is_valid_ik`，`owner_space='POSE'`，`use_limit_<axis> = (ik_max != c.max or ik_min != c.min)`。
- 实测输入：足ＩＫ 的目标是 足首，链为 [ひざ, 足]，loop 40，单位角 1.0，ひざ 限制 x −180°～−0.5°；つま先ＩＫ 的目标是 つま先，链为 [足首]，loop 3，单位角 4.0。导入后的状态 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)：
  - **`左ひざ`**：
    - 约束 IK：`subtarget 左足ＩＫ, chain_count 2, iterations 40, use_tail True, pole_target None, is_valid True`。
    - `use_ik_limit` 为 `(True,True,True)`；Blender 把 `ik_min_x` 钳到了 0.0，`ik_max_x=π`。
    - `mmd_ik_limit_override`：`owner_space POSE, use_limit_x True, min_x 0.0087, max_x 3.1416, use_limit_y/z False`。X 轴被启用，是因为 0.5° 没法用 ik_min_x≤0 表示。
  - **`左足首`**：带 `mmd_ik_target_override`（DAMPED_TRACK、mute、influence 0、subtarget `左ひざ`、`track_axis TRACK_Y`），以及 IK `subtarget 左つま先ＩＫ, chain 1, iterations 3`；`左足首.ik_rotation_constraint = 4.0`。
  - **`左つま先`**：带 `mmd_ik_target_override`，subtarget 为 `左足首`。
  - **IK 骨本身**没有约束；`arm.get('mmd_ik_loop_factor')` 为 None。
  - **再导出**，与输入一致：
    - `左足ＩＫ`：`isIK`、`target=左足首`、`loop 40`、`angle 1.0`，links 为 `(左ひざ, min (−3.142,0,0), max (−0.009,0,0))` 和 `(左足, 无限制)`。
    - `左つま先ＩＫ`：`target=左つま先`、`loop 3`、`angle 4.0`，links 为 `(左足首, 无限制)`。
- 导出流程 — [src/core/pmx/exporter.py:476-568](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  1. 遍历非影子骨上所有 `type=='IK' and not mute` 的约束。
  2. IK 骨由 `__get_ik_control_bone(c)` 确定：`c.target` 必须是本骨架；若 subtarget 骨的 `mmd_shadow_bone_type=='IK_TARGET'`，改取它的父骨。同一根 IK 骨已经用过时跳过。
  3. 链起点：`ik_chain0 = bone if c.use_tail else bone.parent`。
  4. 目标骨按以下顺序确定：
     - 先查任意骨上的 `mmd_ik_target_custom`（其 subtarget==IK 骨）；
     - 否则调用 `__get_ik_target_bone(bone)`，在非影子子骨里依次找：`mmd_ik_target_override.subtarget == bone.name` 的子骨 → `use_connect` 的子骨 → head 离 bone.tail 最近的子骨。
  5. `loopCount = max(int(c.iterations / ik_loop_factor), 1)`，其中 `ik_loop_factor = max(arm.get('mmd_ik_loop_factor', 1), 1)`。
  6. `rotationConstraint`：custom 情况取 IK 骨的值，否则取约束骨的 `ik_rotation_constraint`。
- 每个 link 的角度限制按以下优先级取值；三轴都没取到就不写限制；写之前调用 `convertIKLimitAngles(min, max, armature.matrix_world @ pose_bone.matrix, invert=True)` — [exporter.py:433-473](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[importer.py:289-315](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)：
  1. IK 骨上的 `mmd_ik_limit_custom{n}`；存在就只用它。
  2. `lock_ik_<axis>`，取 (0,0)。
  3. 该骨上**第一个未静音的 LIMIT_ROTATION**（`next((c for c in pose_bone.constraints if c.type == 'LIMIT_ROTATION' and not c.mute), None)`，不看名字），且 `use_limit_<axis>` 为真。
  4. `use_ik_limit_<axis>` 对应的 `ik_min/ik_max`。
  5. 都没有则该轴无限制。
- `ik_rotation_constraint` 是 FloatProperty（ANGLE，默认 **1.0**，soft 0–4）— [src/properties/bone.py:131-138](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。骨属性面板对带 IK 约束的骨显示 "IK Angle (IK骨名)"；custom 情况改为在 IK 骨上显示 "IK Angle {…}" — [src/panels/prop_bone.py:19-29](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/prop_bone.py)。PMX 层的默认值是 `loopCount=8`、`rotationConstraint=0.03` — [src/core/pmx/__init__.py:972-976](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/__init__.py)。
- `ik_loop_factor` 只有一个入口：算子 `mmd_tools.change_mmd_ik_loop_factor`（属性 `mmd_ik_loop_factor`，范围 1–100），作用于活动骨架；它读写 `arm['mmd_ik_loop_factor']`，按比例改所有 IK 约束的 `iterations`，还会写 `arm['_RNA_UI']`。骨架对象属性面板上有 "Change MMD IK Loop Factor" 按钮 — [src/operators/misc.py:267-318](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/misc.py)、[src/panels/prop_object.py:37-38](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/prop_object.py)。v2.10.3 已改为用 `mmd_root.ik_loop_factor` — [v2.10.3 exporter:500](https://raw.githubusercontent.com/MMD-Blender/blender_mmd_tools/v2.10.3/mmd_tools/core/pmx/exporter.py)。
- `mmd_ik_toggle` — [src/properties/bone.py:186-215](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/bone.py)、[src/properties/root.py:35-64](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/root.py)、[src/core/vmd/importer.py:424-439](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/vmd/importer.py)、[src/core/vmd/exporter.py:231](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/vmd/exporter.py)：
  - 是 `PoseBone` 上的 BoolProperty，默认 True，描述 "MMD IK toggle is used to import/export animation of IK on-off"。
  - update 回调把所有 `subtarget==本骨` 的 IK 约束的 influence 设为该值，并沿 IK 链把每根骨第一个未静音 LIMIT_ROTATION 的 influence 同步成同一值。
  - `mmd_root.use_property_driver` 开启时会为它建驱动器；VMD 导入/导出读写它。
- 导入选项 `fix_IK_links`（默认 False）会把链节的 tail 对齐到下一节或目标骨的 head；长度 <0.001 的链节不管是否开启都会被修 — [importer.py:229-244](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)、[src/operators/fileio.py:105-109](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)。

### Inferences
- 我们生成 足ＩＫ / つま先ＩＫ 时，**照抄导入器**的表示：
  - **约束位置**：IK 约束放在 `左ひざ` / `左足首` 上。
  - **迭代次数**：`iterations` 直接写 PMX 的 loop 值（40 / 3）。不要设置 `arm['mmd_ik_loop_factor']`；如果它已存在，就把 iterations 乘上它。
  - **单位角**：`ik_rotation_constraint` 写在约束骨上，取 2.0 / 4.0 rad。依据见 [03 笔记](03_MMD骨骼规范与准标准骨.md)：Hogarth 文档给出的单位角是 114.5916°（=2 rad）和 229.1831°（=4 rad）。
  - **目标标记**：在 `左足首` / `左つま先` 上加 `mmd_ik_target_override`。XPS 的小腿和脚常带辅助子骨，导出器的最近邻启发式容易选错目标。
  - **膝盖限制**：直接调用 `mmd_tools.core.pmx.importer.PMXImporter.convertIKLimitAngles(PMX_min, PMX_max, pose_bone.bone.matrix_local)` 得到 Blender 值，再按导入器的逻辑写 `use_ik_limit_*` / `ik_min/max_*` 和 `mmd_ik_limit_override`。实测这样往返是精确的。
- 不要在 IK 链节骨上放其它未静音的 LIMIT_ROTATION：导出器会把第一个未静音的当成 IK 限制。

### Gaps
- `convertIKLimitAngles` 只在标准朝向的骨（膝盖朝下）上实测过；对任意 roll 的 XPS 骨，轴对齐的结果没有逐一验证。

---

## Q6. 表示枠（Display frames）API

### Takeaway
- **数据结构**与 4.5.5 相同：`mmd_root.display_item_frames[].data[]`，条目有 `type`（`BONE`/`MORPH`）、`name`、`morph_type`；特殊枠是 `Root` 和 `表情`。
- **Quick Setup 存在**，但 `GROUP_LOAD` / `GROUP_APPLY` 基于 **pose bone groups**（菜单名 "Load/Apply Bone Groups"）。
- **导入器**会把表示枠同步成同名的骨骼组。
- **导出时** BONE 条目按 **Blender 骨名**解析；找不到的条目（包括影子骨）会被跳过并打警告。

### Cited Findings
- 数据结构 — [src/properties/root.py:208-265](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/root.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)：
  - `MMDDisplayItem.type`：`BONE`(1) / `MORPH`(2)。
  - `MMDDisplayItem.morph_type`：`material_morphs`/`uv_morphs`/`bone_morphs`/`vertex_morphs`/`group_morphs`，默认 `vertex_morphs`。
  - `MMDDisplayItemFrame`：`name`（PropertyGroup 名）、`name_e`、`is_special`（注释为 "特殊枠はファイル仕様上の固定枠(削除、リネーム不可)"）、`data`、`active_item`。
- 算子 — [src/operators/display_item.py:14-230](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/display_item.py)：
  - `display_item_frame_add`：在活动枠之后插入一个 "Display Frame"，最早插在索引 1 之后。
  - `display_item_frame_remove`：对 special 枠只清空，不删除。
  - `display_item_frame_move`：special 枠不移动，`index_min=2`。
  - `display_item_add`：在 `表情` 枠里加活动 morph，其它枠里加 `context.active_bone`；缺省名分别为 "Morph Item" / "Bone Item"。
  - `display_item_remove`（带 `all` 选项）、`display_item_move`、`display_item_find`（`type` BONE/MORPH）、`display_item_select_current`。
- `mmd_tools.display_item_quick_setup` 的 `type` 选项 — [display_item.py:232-265](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/display_item.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)：

| type | 描述 | 实际调用 |
|---|---|---|
| `RESET` | "Clear all items and frames, reset to default" | `initialDisplayFrames()` |
| `FACIAL`（默认） | "Load all morphs to faical frame" | `initialDisplayFrames(reset=False)` + `load_facial_items` |
| `GROUP_LOAD` | "Load armature's bone groups to display item frames" | `load_bone_groups` + `initialDisplayFrames(reset=False)` |
| `GROUP_APPLY` | "Apply display item frames to armature's bone groups" | `apply_bone_groups` |

- 三个静态方法 — [display_item.py:267-370](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/display_item.py)：
  - `load_facial_items(mmd_root)`：把五类 morph 全部放进 `表情` 枠，已有条目保持原顺序。
  - `load_bone_groups(mmd_root, armature)`：每个非空 pose bone group 生成一个同名枠，`name_e = 组名`，条目是组内的骨（按 pose.bones 顺序）。没用到的非 special 枠被删除；special 枠除 `表情` 外全部清空。
  - `apply_bone_groups(mmd_root, armature)`：对每个 BONE 条目，以它第一次出现的枠名作为组名，设 `pose_bones[item.name].bone_group = 组`；没出现在任何枠里的骨设 `bone_group=None`；未使用的组被删除。
- 导入器的做法 — [src/core/pmx/importer.py:744-767](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)、[实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)：
  - 逐枠写入；BONE 条目的名字是 Blender 骨名，MORPH 条目写名字和 morph_type。
  - 然后调用 `DisplayItemQuickSetup.apply_bone_groups(root.mmd_root, armObj)`。
  - 实测导入后的骨骼组：`Root:[全ての親]`、`体:[センター,上半身,下半身]`、`足:[左足,左ひざ,左足ＩＫ,左つま先ＩＫ]`。special 枠 `Root` 也成了组，其余骨没有组。
  - 不导入 DISPLAY 时，改为调用 `initialDisplayFrames()` — [importer.py:870-873](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)。
- 导出 — [src/core/pmx/exporter.py:769-787](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - 每个枠生成一个 `pmx.Display(name, name_e, isSpecial)`。
  - BONE 条目只有当 `j.name in bone_map` 时才写成 `(0, 索引)`；MORPH 条目只有当 `(morph_type, name)` 在 morph 表里时才写成 `(1, 索引)`；否则打 `logging.warning('Display item (%s, %s) was not found.')` 并跳过。
  - 实测往返后，枠与条目都一致 — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
  - `pmx.Model()` 默认就自带 `Root` 和 `表情` 两个枠 — [src/core/pmx/__init__.py:318-348](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/__init__.py)。
- 1.0.2 中 `表情` 枠的顺序**不影响** PMX 里的 morph 顺序（见 Q8）。
- `ConvertToMMDModel` 收尾时依次调用 `load_bone_groups` → `initialDisplayFrames(reset=False)` → `load_facial_items` — [src/operators/model.py:315-319](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)。

### Inferences
- 插件直接写 `display_item_frames`，比走 bone groups 更可控（可以设英文枠名、控制条目顺序）：
  1. 先调 `rig.initialDisplayFrames(reset=True)`；
  2. `frames.add()` 后填 `name` / `name_e`；
  3. `data.add()` 后填 `type='BONE'`、`name=<Blender 骨名>`。
- 如果想复用骨骼组：`arm.pose.bone_groups.new(name)`，设 `pb.bone_group = g`，再调 `DisplayItemQuickSetup.load_bone_groups(...)`，事后修正 `name_e`。
- XPS 骨架上如果残留 pose bone groups，"Convert Model" 或 `GROUP_LOAD` 会把它们都变成枠，转换前应先清理。
- `Root` 枠的默认条目是 `arm.data.bones[0]`，即层级深度优先序中的第一根骨。要确保 `全ての親` 是第一个根骨，或者手动写入。

### Gaps
- 无。

---

## Q7. 材质

### Takeaway
- **导出读取什么**：只读 `mmd_material.*` 字段；节点名为 `mmd_base_tex` / `mmd_sphere_tex` 的 `ShaderNodeTexImage` 的 `image.filepath`；toon 读 `toon_texture` 路径或共享编号。字段集合与 4.5.5 相同。
- **最大的坑：RNA 写入会改节点**。以下任一操作都会给材质建 `mmd_shader` / `mmd_tex_uv` 节点，并把材质输出的 Surface 改接到 `mmd_shader`，原来的 Principled 被断开：
  - 通过 RNA 写任何带 update 回调的 `mmd_material` 字段（颜色、alpha、反射、双面、阴影、球面类型、toon 等）；
  - 切换 `mmd_root.use_toon_texture` / `use_sphere_texture`。
  - 用 ID-property 写（例如 `mat.mmd_material['diffuse_color']=...`）则不会改节点。
- **贴图复制**：只在 `copy_textures=True` 时发生，目标是 `<pmx目录>/textures/<文件名>`，或相对 `import_folder` 的路径；**不处理打包贴图**。不复制时，PMX 里写的是原文件相对 PMX 的路径。
- **材质顺序**：网格按对象名排序，网格内按槽位顺序；同名材质跨网格会被合并。

### Cited Findings
- 当 Blender ≥2.80 时，`FnMaterial = _FnMaterialCycles` — [src/core/material.py:840-842](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)。节点命名 — [material.py:415-487,652-838](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)：
  - 基础贴图 `mmd_base_tex`、球面贴图 `mmd_sphere_tex`、toon 贴图 `mmd_toon_tex`（仅用于预览）。
  - 着色器组节点 `mmd_shader`（节点组 `MMDShaderDev`）。
  - UV 组节点 `mmd_tex_uv`（节点组 `MMDTexUV`，输出 `Base UV/Toon UV/Sphere UV/SubTex UV`）。
- `create_texture(filepath)` 内部调用 `__create_texture_node('mmd_base_tex', …)` — [material.py:419-421,504-516,652-704,112-127](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)：
  1. 先 `__update_shader_nodes()`：材质没有节点树时设 `use_nodes=True` 并 `nodes.clear()`；建 `mmd_shader` 和 `mmd_tex_uv`；若 `mmd_shader` 的输出没连上，就找到活动材质输出（没有就新建），把 `Shader` 连到 `Surface`。
  2. 新建 `ShaderNodeTexImage`，`name=label='mmd_base_tex'`，`image=_load_image(path)`。`_load_image` 按 samefile 复用已有图像；文件不存在时建一张 1×1 占位图并设好 filepath。
  3. 返回 `_DummyTextureSlot`。
  - 实测：节点为 `['mmd_base_tex','mmd_shader','mmd_tex_uv','材质输出']`，节点组为 `MMDShaderDev` / `MMDTexUV`。`mmd_shader` 的输入有 `Ambient Color, Diffuse Color, Specular Color, Reflect, Base Tex Fac, Base Tex, Toon Tex Fac, Toon Tex, Sphere Tex Fac, Sphere Tex, Sphere Mul/Add, Double Sided, Alpha, Base Alpha, Toon Alpha, Sphere Alpha` — [实测E](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
  - `remove_texture()`、`create_sphere_texture(path, obj)`、`remove_sphere_texture()`、`create_toon_texture(path)`、`remove_toon_texture()` 的机制相同 — [material.py:423-487](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)。
- 导出怎样读贴图 — [material.py:490-495](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)、[src/core/pmx/exporter.py:207-221,292-307](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - `get_texture()` 只在节点是 `ShaderNodeTexImage` 时返回 `_DummyTexture(image)`。
  - 导出时：`if tex and tex.type == 'IMAGE' and tex.image: __exportTexture(tex.image.filepath)`。`__exportTexture` 做 `bpy.path.abspath` + `os.path.abspath`，按 normcase 去重；文件不存在只打警告。
  - toon：`is_shared_toon_texture` 为真时 `toon_texture=shared_toon_texture`（0–9），否则 `__exportTexture(mmd_mat.toon_texture)`。
- **RNA 写入会改节点（实测 I）** — [实测I](assets/08_mmd_tools_1.0.2/verify_live2_102.json)：
  1. 新材质结构为 Principled→Output。用 ID-prop 写 `diffuse_color` / `alpha`、用 RNA 写 `name_j` / `name_e` 之后，Surface 仍来自 `原理化BSDF`。
  2. 接着用 RNA 写 `mmd_material.diffuse_color` → Surface 改由 `mmd_shader` 提供，新增了 `mmd_shader` / `mmd_tex_uv`；Principled 节点还在，但已断开。
  - 机制：属性 update 回调调用 `FnMaterial(...).update_*()` → `__update_shader_input()` → `__update_shader_nodes()`；只有材质名以 `mmd_` 开头时才跳过 — [src/properties/material.py:14-54](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/material.py)、[material.py:519-583,639-650](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)。
  - `mmd_root.use_toon_texture` / `use_sphere_texture` 的 update 回调会对模型的全部材质调用 `use_toon_texture()` / `use_sphere_texture()`，同样走 `__update_shader_input` — [src/properties/root.py:69-83](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/root.py)、[material.py:430-434,479-480](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)。
  - 写 `is_shared_toon_texture` / `shared_toon_texture` / `toon_texture` 时，update 回调调用 `update_toon_texture()` → `create_toon_texture('<shared_toon_folder>/toonNN.bmp')`，建出 `mmd_toon_tex` 并改节点 — [material.py:280-289](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)、[properties/material.py:35-36,231-253](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/material.py)。实测本机偏好 `shared_toon_folder` 为空 — [实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
- ID-prop 写入实测（K）— [实测K](assets/08_mmd_tools_1.0.2/verify_live3_102.json)：
  - `mat.mmd_material['sphere_texture_type'] = 1/2/3/4` 读回 RNA 为 `'0'/'1'/'2'/'3'`，即 ID-prop 存的是枚举项的数值 1–4。
  - `is_shared_toon_texture=True`、`shared_toon_texture=3` 用 ID-prop 写，都不改节点。
  - 导出结果正确：`sphere_texture_mode` 为 0/1，`is_shared_toon_texture True`，`toon_texture 3`。
- `name_j` 有自定义 setter：值变化时，先用 `Model.findRoot(bpy.context.active_object)` 找模型，在**该模型**材质的 `name_j` 中调 `utils.uniqueName` 去重（冲突时加 `.001`）；找不到模型时，就在**全部** `bpy.data.materials` 中去重 — [src/properties/material.py:56-70](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/material.py)、[src/utils.py:163-171](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/utils.py)。
- 字段清单（与 4.5.5 相同，实测）：`name_j, name_e, material_id(-1), ambient_color([0.4]*3), diffuse_color([0.8]*3), alpha(1.0), specular_color([0.625]*3), shininess(50, "Reflect"), is_double_sided(False), enabled_drop_shadow(True), enabled_self_shadow_map(True), enabled_self_shadow(True), enabled_toon_edge(False), edge_color([0,0,0,1]), edge_weight(1.0), sphere_texture_type('0'..'3'), is_shared_toon_texture(False), toon_texture(''), shared_toon_texture(0), comment` — [src/properties/material.py:75-261](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/material.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。
  - 导出映射：`name = name_j or material.name`、`diffuse = diffuse_color + [alpha]`、各标志位、`edge_size = edge_weight`、`sphere_texture_mode = int(sphere_texture_type)`（开启 `disable_specular` 时为 0）— [exporter.py:269-310](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
- 贴图复制只在 `copy_textures=True` 时执行 — [exporter.py:223-267,1264-1268](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - 基准目录：`base_folder = root.get('import_folder','') or 偏好 base_texture_folder`。
  - 有基准目录时，目标路径取 `saferelpath(path, base, 'outside')`；越出基准目录就改试偏好目录；仍越界则用 `textures/<basename>`。没有基准目录时直接用 `textures/<basename>`。
  - 源文件不存在：打警告并跳过，路径保持不变。重名时加 `_1`、`_2` 后缀。复制用 `shutil.copyfile`。
  - **不处理打包贴图**：`os.path.isfile` 为假就跳过。
  - 实测：没有 `import_folder` 时，复制到 `<out>/textures/mmd_tools_102_tex.png`。`copy_textures=False` 时，PMX 保留原路径：`Texture.save` 写入 `os.path.relpath(path, PMX目录)`，跨盘时写绝对路径，分隔符统一为反斜杠 — [实测E](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[src/core/pmx/__init__.py:793-800](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/__init__.py)。
- 材质与网格的顺序 — [exporter.py:54-66,114-121,1088-1090,1230](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - `meshes` 按对象名排序。
  - 每个网格只取有面的槽位，按 `material_faces` 的键排序。
  - `mat_map` 以**材质名**为键，因此跨网格的同名材质会被合并成一个。
  - 没有材质的面使用 `_DefaultMaterial`（`bpy.data.materials.new('')` 创建，导出后删除）。
- 排序相关选项：
  - `sort_materials`（默认 False，描述 "Sort materials for alpha blending. WARNING: Will not work if you have transparent meshes inside the model. E.g. blush meshes"）：按到模型中心的平均距离重排材质，源码自称"かなりいいかげんな実装" — [src/operators/fileio.py:446-453](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)、[exporter.py:634-670](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
  - `sort_vertices`：`NONE` / `BLENDER` / `CUSTOM`；CUSTOM 读顶点组 `mmd_vertex_order`，缺省值 2 — [fileio.py:474-483](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)、[exporter.py:1023-1032](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
- 排序面板 — [src/panels/util_tools.py:39-125](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/util_tools.py)、[src/core/material.py:41-72](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)、[src/operators/misc.py:35-59](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/misc.py)、[src/utils.py:173-192](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/utils.py)：
  - Material Sorter（选中网格时出现）：`mmd_tools.move_material_up/down` 调用 `FnMaterial.swap_materials(…, reverse=True, swap_slots=True)`。
  - Meshes Sorter：`mmd_tools.object_move` 给对象名加 **base-36 三位**前缀（`int2base(index, 36, 3)` + `_`，匹配正则 `[0-9A-Z]{3}_`）。4.5.5 用的是十进制 `03d`。
- `convert_to_mmd_material(material)`（Convert Model 调用）— [material.py:585-636](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)：
  1. 材质使用节点、且没有任何 `mmd_` 开头的节点时：从活动输出往上找第一个 `TEX_IMAGE`（找不到就取任意一个），改名为 `mmd_base_tex`。
  2. 然后经 RNA 写 `diffuse_color/alpha/specular_color/shininess/is_double_sided/enabled_self_shadow_map/enabled_self_shadow`，因此也会触发上面的改节点行为。
  3. 1.0.2 **不删除** BSDF / Emission 节点。
- 本机 Blender 的 UI 语言是 `zh_CN`，且 `use_translate_new_dataname=True`，所以新建的数据和节点名会被本地化（"原理化BSDF"、"材质输出"）。mmd_tools 按类型而不是名字找输出节点，不受影响 — [实测I](assets/08_mmd_tools_1.0.2/verify_live2_102.json)、[实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)、[material.py:687-693](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/material.py)。

### Inferences
- **保留 HD 材质的工作流**（保留 XPS/HD 的 Principled 网络）：
  - 用 ID-prop 批量写 `mmd_material` 的数值、颜色、布尔和枚举字段。枚举 `sphere_texture_type` 写 1=Off、2=Multiply、3=Add、4=SubTexture。
  - `name_j` / `name_e` 可以用 RNA 写，但要先让活动对象属于该模型；或者直接写 ID-prop `['name_j']`，自己保证唯一。
  - 基础贴图不要调 `create_texture`，而是把现有的 `ShaderNodeTexImage` 节点改名为 `mmd_base_tex`。它不必连到 mmd_shader 也能导出。
  - 不要切换 `mmd_root.use_toon_texture` / `use_sphere_texture`。
- 如果需要"MMD 风格预览"材质，可以另做一份副本材质，走 `create_texture` 路线。
- 导出前：
  - 把打包贴图解包到磁盘（1.0.2 不会写出打包数据）；
  - 可以设 `root['import_folder'] = XPS 贴图根目录`，以保留子目录结构；
  - 显式传 `copy_textures=True`。
- 想精确控制材质顺序：合并成单一网格后排槽位，或给网格对象名加 `000_`… 前缀。需要分开的材质必须取不同的名字。

### Gaps
- 未实测打包贴图的导出（"会被跳过"是从代码推断的）；也没测 DDS 等非常规格式。

---

## Q8. Morph API

### Takeaway
数据结构与 4.5.5 基本相同，有四点差异：

1. **PMX 里的 morph 顺序是固定的**，不按 `表情` 枠排序：

| 顺位 | 类型 | 类型内部的顺序 |
|---|---|---|
| 1 | 顶点 morph | 未登记在 `vertex_morphs` 里的形态键排最前，其余按 `vertex_morphs` 顺序 |
| 2 | 骨骼 morph | `bone_morphs` 顺序 |
| 3 | 材质 morph | `material_morphs` 顺序 |
| 4 | UV morph | `uv_morphs` 顺序 |
| 5 | 组 morph | `group_morphs` 顺序 |

2. **UV morph** 默认 `data_type='DATA'`，这种数据导出时会被忽略。
3. **组 morph** 的 `factor` 默认是 **0**。
4. **没有** morph 转换算子；`overwrite_bone_morphs_from_pose_library` 在 Blender 3.6 里用不了（Pose Library 已被移除）。

### Cited Findings
- 顶点 morph 怎么导出 — [src/core/pmx/exporter.py:1116-1170](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[exporter.py:69-75,570-600](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - 取网格的形态键，跳过 Basis、`mmd_bind*` 和 `mmd_sdef_skinning`；`mmd_sdef_c/r0/r1` 被当作 SDEF 数据。
  - 逐个临时设 `mute=False` 和 `active_shape_key_index=i` 来评估网格；偏移 <0.001 的顶点不记录；顶点数不一致的形态键直接跳过。
  - morph 名就是形态键名；`name_e` 和 `category` 取自 `mmd_root.vertex_morphs` 中的同名条目。`CATEGORIES` 只认 SYSTEM/EYEBROW/EYE/MOUTH，其它都归为 OTHER。
  - 排序：`shape_key_names.sort(key=lambda x: root.mmd_root.vertex_morphs.find(x))`。未登记的名字 find 结果是 -1，所以排最前。
- 顺序：`execute` 依次调用 `__exportVertexMorphs` → `__export_bone_morphs` → `__export_material_morphs` → `__export_uv_morphs` → `__export_group_morphs` → `__exportDisplayItems`，**没有**按表示枠重排 — [exporter.py:1253-1259](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。对照：4.5.5 会按 `表情` 枠排序，见 [02 笔记 Q5](02_mmd_tools导出契约.md)。
- `FnMorph.load_morphs(rig)`（`Model.loadMorphs()` 是它的包装）— [src/core/morph.py:69-97](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/morph.py)、[src/core/model.py:675-676](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - 把各网格 `key_blocks[1:]` 中不以 `mmd_` 开头、且还没登记的形态键加进 `vertex_morphs`，设 `name_e=name`。
  - 用 `category_guess` 猜分类：小写名含 `mouth` → MOUTH；含 `eye` 且含 `brow` → EYEBROW；只含 `eye` → EYE。
  - 把 `UV_*` 顶点组登记为 `uv_morphs`，`data_type='VERTEX_GROUP'`。
- 公共基类 `_MorphBase` — [src/properties/morph.py:20-102](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/morph.py)：
  - `name`：setter 保证同类型内唯一，并同步重命名形态键、UV 顶点组、组 morph 中的引用、`表情` 枠条目和滑块。
  - `name_e`。
  - `category`：`SYSTEM`（0，显示为 "Hidden"）/`EYEBROW`/`EYE`/`MOUTH`/`OTHER`（默认）。
- 骨骼 morph — [properties/morph.py:105-183](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/morph.py)、[exporter.py:672-705](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[src/core/vmd/importer.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/vmd/importer.py)：
  - `BoneMorph.data[]` 的元素是 `BoneMorphData{bone, bone_id, location, rotation}`。其中 `bone` 经 bone_id 读写；`location` 是 Vec3；`rotation` 是四元数 wxyz，默认 [1,0,0,0]。
  - 导出时按 `self.__bone_name_table.index(data.bone)` 找骨索引，用 `BoneConverter(pose_bone, scale, invert=True)` 转换；模型已 build 且不在 REST 姿态时改用 `BoneConverterPoseMode`。
  - 相关算子 — [src/operators/morph.py:437-563](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/morph.py)：
    - `mmd_tools.apply_bone_morph`（"Apply current pose to active bone morph"）：清空活动骨骼 morph，再把所有有位移或旋转的 pose bone 写进去。
    - `view_bone_morph`、`clear_bone_morph_view`、`select_bone_morph_offset_bone`、`edit_bone_morph_offset`、`apply_bone_morph_offset`。
- 材质 morph — [properties/morph.py:185-378](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/morph.py)、[exporter.py:602-632](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - `MaterialMorphData` 的字段：
    - `related_mesh`：setter 要求 `rig.findMesh` 能找到。
    - `offset_type`：`'MULT'` / `'ADD'`，默认 ADD。
    - `material`：经 material_id 读写；另有 `material_id` 字段。
    - 偏移量：`diffuse_color`(4)、`specular_color`(3)、`shininess`、`ambient_color`(3)、`edge_color`(4)、`edge_weight`、`texture_factor`(4)、`sphere_texture_factor`(4)、`toon_texture_factor`(4)。
  - 导出按 **Blender 材质名**解析索引：`self.__material_name_table.index(data.material)`；材质名为空时索引写 -1（表示全部材质）。
  - 工作材质相关算子：`create_work_material`、`apply_material_morph_offset`、`clear_temp_materials`、`material_morph_offset_init` — [src/operators/morph.py:256-435](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/morph.py)。
- UV morph — [properties/morph.py:402-436](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/morph.py)、[exporter.py:707-741](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[src/core/morph.py:118-122,206-230](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/morph.py)：
  - `UVMorph` 的字段：`uv_index`（0–4）、`data_type`（默认 `'DATA'`，另一个值是 `'VERTEX_GROUP'`）、`data[]`、`vertex_group_scale`（默认 1）。
  - 导出只处理 `VERTEX_GROUP`；`DATA` 类型只打警告 "Deprecated UV morph … please convert it to vertex groups"，不导出。
  - 数据存放在顶点组 `UV_<名><+|-><X|Y|Z|W>` 里，用 `FnMorph.store_uv_morph_data(obj, morph, offsets, offset_axes)` 写入。
- 组 morph：`GroupMorphOffset{morph_type, name, factor}`，**`factor` 默认 0**（soft 范围 0–1）— [properties/morph.py:439-476](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/morph.py)。导出按 `(morph_type, name)` 查索引，找不到就警告并跳过 — [exporter.py:743-767](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
- 不存在 `convert_bone_morph_to_vertex_morph` 和 `convert_group_morph_to_vertex_morph`（见算子清单）— [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。
- Pose Library 已不可用 — [src/core/morph.py:135-166](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/morph.py)、[实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)：
  - `FnMorph.overwrite_bone_morphs_from_pose_library` 依赖 `armature.pose_library` 和 `bpy.ops.poselib.apply_pose`。
  - Blender 3.6 实测：`hasattr(bpy.types.Object, 'pose_library') == False`，`poselib.apply_pose` 也不存在。
  - 结论：导出选项 `overwrite_bone_morphs_from_pose_library` 和算子 `morph_overwrite_from_active_pose_library` 在 3.6 都用不了。
- Morph 滑块：`mmd_tools.morph_slider_setup`（`type` 为 `CREATE`/`BIND`/`UNBIND`），会在 root 下建 `.placeholder`（`mmd_type` 为 `PLACEHOLDER`）和 `.dummy_armature` — [src/operators/model.py:13-42](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)、[src/core/morph.py:252-620](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/morph.py)。

### Inferences
- XPS 模型如果带形态键：
  1. 先把要导出的形态键登记进 `vertex_morphs`，名字用日文 morph 名；
  2. 按期望顺序排列 `vertex_morphs`；
  3. 再调用 `DisplayItemQuickSetup.load_facial_items`。
  - 未登记的形态键会排到最前，需要避免。
- 组 morph 必须显式写 `factor`；UV morph 必须用 VERTEX_GROUP。
- 导出时始终传 `overwrite_bone_morphs_from_pose_library=False`。

### Gaps
- 未实测骨骼 morph 往返的数值精度。

---

## Q9. 刚体 / Joint API

### Takeaway
1.0.2 用 `Model.createRigidBody(**kwargs)` 和 `Model.createJoint(**kwargs)` 构造刚体和 Joint；批量版本是 `createRigidBodyPool(n)` / `createJointPool(n)`。4.5.5 的 `FnRigidBody` 在这里不存在。属性名与 4.5.5 一致：刚体是 `mmd_rigid.shape/size/type/bone/collision_group_number/collision_group_mask`，Joint 是 `mmd_joint.spring_linear/spring_angular`。质量、摩擦等参数放在 Blender 原生的 `rigid_body` / `rigid_body_constraint` 上。导出时模型应处于未 build 状态；刚体和 Joint 都按对象名排序。

### Cited Findings
- `createRigidBodyPool(counts)` 依次做这些事 — [src/core/model.py:678-701](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)、[src/bpyutils.py:110-130,183-188](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)：
  1. `bpyutils.createObject('Rigidbody', 新网格)`：链接到 `context.collection` 并设为活动对象。
  2. 设 `parent=rigidGroupObject()`、`mmd_type='RIGID_BODY'`、`rotation_mode='YXZ'`、`display_type='SOLID'`、`show_transparent=True`、`hide_render=True`，并关闭 cycles 可见性。
  3. `bpy.ops.rigidbody.object_add(type='ACTIVE')`。
  4. 需要多个时，用 `bpyutils.duplicateObject` 复制；它依赖 `bpy.ops.object.duplicate` 和当前选择状态。
- `createRigidBody(**kwargs)` — [model.py:703-771](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：

| 参数 | 必需/可选 | 说明 |
|---|---|---|
| `shape_type` | 必需 | 0 球 / 1 盒 / 2 胶囊 |
| `location`、`rotation`、`size` | 必需 | Blender 坐标 |
| `dynamics_type` | 必需 | 0/1/2，超出范围时按 `'1'` 处理 |
| `collision_group_number` | 可选 | |
| `collision_group_mask` | 可选 | 16 个布尔 |
| `name` | 可选 | 同时设对象名和 `name_j` |
| `name_e`、`bone`、`friction`、`mass`、`angular_damping`、`linear_damping`、`obj` | 可选 | |
| `bounce` | 可选 | 代码是 `if bounce:` 才写，所以值 0 会被忽略 |

  函数结尾会执行 `obj.select=False`。
- `createJointPool(counts)` — [model.py:773-804](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - 建一个名为 "Joint" 的 Empty，`parent=jointGroupObject()`，`mmd_type='JOINT'`，`rotation_mode='YXZ'`，`empty_display_type='ARROWS'`，`empty_display_size=0.1*root 尺寸`，`hide_render=True`。
  - 需要时先 `bpy.ops.rigidbody.world_add()`，再 `bpy.ops.rigidbody.constraint_add(type='GENERIC_SPRING')`。
  - `use_limit_lin/ang_*`、`use_spring_*`、`use_spring_ang_*` 全部设为 True，`disable_collisions=False`。
- `createJoint(**kwargs)` — [model.py:806-874](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - 必需参数：`location, rotation, rigid_a, rigid_b, maximum_location, minimum_location, maximum_rotation, minimum_rotation, spring_angular, spring_linear, name`；可选参数：`name_e, obj`。
  - 对象名设为 `'J.' + name`，`name_j=name`。
  - 写入 `object1/object2` 和 `limit_lin/ang_*_upper/lower`，以及 `mmd_joint.spring_*`。
- `MMDRigidBody` 的属性 — [src/properties/rigid_body.py:13-219](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/rigid_body.py)、[src/core/model.py:36-56](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - `name_j`：get/set 存在 ID-prop `name` 里；`name_e`。
  - `collision_group_number`：0–15，默认 1；update 时给对象套上 `mmd_tools_rigid_{n}` 材质。
  - `collision_group_mask`：16 个布尔，描述 "The groups the object can not collide with"。
  - `type`：`'0'` Bone / `'1'` Physics / `'2'` Physics + Bone；update 时同步 `rigid_body.kinematic`。
  - `shape`：`SPHERE`/`BOX`/`CAPSULE`。
  - `bone`：get/set 通过静音的 `CHILD_OF` 约束 `mmd_tools_rigid_parent` 存取。
  - `size`：getter 从 `bound_box` 反算；setter 会 `assert obj.mode == 'OBJECT'`，并重建或缩放网格。
- `MMDJoint` 的属性：`name_j, name_e, spring_linear, spring_angular`；后两者 update 时写入 `spring_stiffness_*` — [src/properties/rigid_body.py:222-271](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/rigid_body.py)。
- 实测 F：建了两个刚体（`頭`：静态球；`髪1`：动态胶囊，group 3，mask 只勾组 3）和一个 Joint — [实测F](assets/08_mmd_tools_1.0.2/verify_live_102.json)：
  - 父级：刚体在 `rigidbodies`（`RIGID_GRP_OBJ`）下，Joint 在 `joints`（`JOINT_GRP_OBJ`）下。
  - 两个刚体都有 `mmd_tools_rigid_parent:CHILD_OF`；静态刚体 `kinematic True`，动态 False；没传 mass 时为 1.0。
  - Joint：名字 `J.髪1`，`GENERIC_SPRING`，`spring_stiffness_ang_x 10`。
  - 场景原本没有刚体世界，创建后有了；`is_built False`。
  - 导出：按对象名排序（`頭` 在 `髪1` 前）。`頭`：bone 0、type 0、mode 0、group 0、mask 65535；`髪1`：bone 1、type 2、mode 1、group 3、mask 65527（0xFFF7）；Joint：`src 0 dest 1`。
- 导出规则（与 4.5.5 一致）— [src/core/pmx/exporter.py:803-879](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - 刚体和 Joint 都按对象名排序。
  - 名字：`name = name_j or MoveObject.get_name(obj)`。
  - 位置 `t.xzy*scale`；旋转 `r.xzy*-1`（YXZ 欧拉）；尺寸乘以平均缩放和 scale（盒子用 `.xzy`）。
  - 碰撞掩码：对**未勾选**的组做 `mask += 1<<i`。
  - 质量、摩擦、反弹、阻尼取自 `obj.rigid_body`；没有 `rigid_body` 的对象被跳过。
  - Joint：`maximum_rotation = (ang_x_lower, ang_z_lower, ang_y_lower)*-1` 等。
  - 导入器建好刚体后会设 `obj.hide=True`，并用 `MoveObject.set_index(obj, i)` 加前缀 — [src/core/pmx/importer.py:466-525](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)。
- 相关算子 — [src/operators/rigid_body.py:15-517](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/rigid_body.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)：
  - `rigid_body_add`：属性有 `name_j='$name_j'`、`name_e='$name_e'`、`collision_group_number`、`collision_group_mask`、`rigid_type`、`rigid_shape`、`size` [0.6]*3（乘以骨长）、`mass 1`、`friction 0.5`、`bounce 0`、`linear_damping 0.04`、`angular_damping 0.1`。每根选中的 pose bone 生成一个刚体，位置在 head/tail 中点，旋转取 `matrix_local.to_euler('YXZ')` 后再绕 X 转 90°。
  - `joint_add`：在父子刚体对之间加 Joint；有 `use_bone_rotation` 选项，默认角度限制 ±π/4。
  - `rigid_body_select`、`rigid_body_remove`、`joint_remove`。
  - `rigid_body_world_update`：重建 `RigidBodyWorld` / `RigidBodyConstraints` 集合，`substeps_per_frame=1`。
- `Model.build()` / `Model.clean()` — [src/core/model.py:1036-1415](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - `build()`：已 built 时先 clean；设 `is_built=True`；然后依次执行：
    1. `__preBuild`：备份变换、静音关系约束、静音动态刚体对应骨的 IK。
    2. `buildRigids(偏好 non_collision_threshold)`：建非碰撞约束 `ncc`；静态刚体 parent 到骨；动态刚体通过 Empty `mmd_bonetrack` 加骨约束 `mmd_tools_rigid_track` 驱动骨骼。
    3. `buildJoints`。
    4. `__postBuild`。
  - `clean()`：做逆操作并删除临时对象（删除用的是旧式上下文覆盖 `bpy.ops.object.delete({...})`），最后 `is_built=False`。
  - 导出算子在 `not is_built` 时会临时设 `pose_position='REST'`；`rigidBodies()` 在 built 状态下还会包含骨架下的刚体 — [src/operators/fileio.py:533-538](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)、[model.py:994-997](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。

### Inferences
- 插件生成物理用 `rig.createRigidBody(...)` / `rig.createJoint(...)`，参数用 Blender 坐标；如果手头的数据是 PMX 坐标，按导入器的 `.xzy` / `*-1` 规则换算。
- 建好后自己用 `MoveObject.set_index(obj, i)` 确定顺序。
- 这些函数会改变活动对象和选中对象，并依赖 `bpy.ops`，调用后要恢复选择状态。
- 导出前确保 `mmd_root.is_built == False`；如果用户 build 过，先调 `Model(root).clean()`。

### Gaps
- 未测：`createRigidBodyPool(n)` 在刚体很多时的速度，以及它对选择状态的副作用。

---

## Q10. 导出函数与导入选项

### Takeaway
- **导出函数可以脱离算子直接调用**：`mmd_tools.core.pmx.exporter.export(filepath, **kwargs)`。实测 A–K 全部用的是它。
- **kwargs 只有这几个**：`root, armature, meshes, rigid_bodies, joints, scale（默认 1.0）, copy_textures, sort_materials, sort_vertices, disable_specular, overwrite_bone_morphs_from_pose_library, translate_in_presets`。
- **算子与函数的差别**：算子 `mmd_tools.export_pmx` 的 `scale` 默认是 **1.0**（不是 12.5），并且在模型未 build 时会把骨架切到 REST 姿态。直接调用函数时，切 REST 要自己做。
- **导入算子**：`scale` 默认 1.0，没有 `ik_loop_factor` 选项。

### Cited Findings
- `execute(filepath, **args)` 读取的参数 — [src/core/pmx/exporter.py:1211-1270](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - `root`：为 None 时模型名为 'test'，注释为 'exported by mmd_tools'。
  - `armature`；`meshes`（按名排序）；`rigid_bodies`、`joints`（都按名排序）。
  - `scale`（默认 1.0）、`disable_specular`、`sort_vertices`（不为 NONE 时启用）、`sort_materials`、`copy_textures`。
  - `overwrite_bone_morphs_from_pose_library`。
  - `translate_in_presets`：为真时先执行 `FnModel.translate_in_presets(root)`，按 `root.mmd_data_query.operation_script` 改名。
  - `export()` 只是对 `execute` 的包装 — [exporter.py:1272-1282](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
- 模型信息：名字取 `mmd_root.name or root.name`，`name_e = mmd_root.name_e`；注释取自文本块（`\n` 换成 `\r\n`），没有文本块时写 "exported by mmd_tools" — [exporter.py:1214-1227](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)、[实测G](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
- 名称回退：`name_e` 一律**没有回退**，为空就写空串 — [exporter.py:364-365,273-274,816-817,866-867](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。

| 对象 | `name` 的取值 |
|---|---|
| 骨 | `name_j or bone.name` |
| 材质 | `name_j or material.name` |
| 刚体 | `name_j or MoveObject.get_name(obj)` |
| Joint | `name_j or MoveObject.get_name(joint,'J.')` |

- 骨的派生字段 — [exporter.py:319-431](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - **位置**：`location = pmx_matrix @ p_bone.head`，在 `bpy.context.view_layer.update()` 之后取**评估后**的骨架。
  - **可见**：`visible = not bone.hide and any(all(x) for x in zip(bone.layers, arm.data.layers))`。
  - **可移动 / 可旋转 / 可操作**：`isMovable = not all(lock_location)`，`isRotatable = not all(lock_rotation)`，以及 `isControllable`。
  - **表示先**：有 `use_connect` 的子骨时写该骨的索引；否则 `is_tip` 为真时写 -1；否则写 `tail − head` 偏移量。
  - **tip 父骨修正**：父骨是 `is_tip` 且本骨 `use_connect` 时，位置取父骨的位置。
  - **轴**：固定轴和局部轴经 `__to_pmx_axis` 转换。
  - **兜底**：骨数为 0 时补一根 `全ての親`/`Root`。
  - 实测可见性：`hide=True` 的骨、以及只放在不可见层上的骨，导出后都是 `visible False` — [实测G](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
  - 实测表示先：子骨可移动时，导入器不会设 `use_connect`（[importer.py:267-279](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)），于是原本"指定骨"形式的表示先在导出时变成了偏移量。例如 `上半身` 输入时指向 `首` 的索引，导出后变成 `[0,4,0]` — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- 坐标：`pmx_matrix = matrix_world * scale` 后交换第 2、3 行（Y/Z 互换，不翻符号）；UV 做 `v → 1−v`；网格用各自的 `matrix_world`，法线有非均匀缩放修正 — [exporter.py:347-355,983-1009](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
- 网格处理 — [exporter.py:916-1112,1181-1206](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)：
  - 用 `evaluated_get(depsgraph).to_mesh(preserve_all_data_layers=True)` 取网格，**全部修改器都被烘焙**；只有 ARMATURE 修改器会在 `pose_position=='REST'` 时被临时关闭。
  - 三角化用 `bmesh.ops.triangulate`（quad `FIXED`、ngon `EAR_CLIP`），并重映射自定义法线。
  - 法线取 `calc_normals_split()` 的 loop 法线，没有 `normal_handling` 选项。
  - 按 UV（阈值 0.001）和法线（阈值 0.01）拆点。
  - 追加 UV：`uv_layers[1:]` 中不以 `_` 开头的层依次作为 UV1–UV4，带 `_` 前缀的层提供 zw 分量。
  - 1.0.2 **不过滤**不在 view layer 里的网格（4.5.5 会跳过），对照 [02 笔记 Q4](02_mmd_tools导出契约.md)。
- 权重 — [exporter.py:152-195,1046-1053](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)；另见实测 D：
  - 只认名字等于某根导出骨 Blender 名的顶点组，且权重 >0。

| 有效顶点组数 | 写出的类型 |
|---|---|
| 0 | BDEF1，绑到骨 **0** |
| 1 | BDEF1 |
| 2 | BDEF2，权重 `w1/(w1+w2)`；有 SDEF 数据时写 SDEF |
| ≥3 | BDEF4；多于 4 个时按权重降序取前 4 个，再归一化 |

- 算子 `ExportPmx`（`bl_idname 'mmd_tools.export_pmx'`，`bl_options {'PRESET'}`）— [src/operators/fileio.py:426-570](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)：
  - 选项默认值：`scale` 1.0、`copy_textures` True、`sort_materials` False、`disable_specular` False、`visible_meshes_only` False、`overwrite_bone_morphs_from_pose_library` False、`translate_in_presets` False、`sort_vertices` 'NONE'、`log_level` 'DEBUG'、`save_log` False。
  - `poll`：活动对象被选中，且属于某个模型。
  - 一次导出多个模型时，每个模型写到 `<folder>/<clean_name>/<clean_name>.pmx`。
  - `_do_execute`：模型未 build 时设 `pose_position='REST'`、`update_tag()`、`frame_set`；传 `meshes=rig.meshes()`（开启 `visible_meshes_only` 时再用 `context.visible_objects` 过滤）、`rigid_bodies=rig.rigidBodies()`、`joints=rig.joints()`。
  - 异常会被捕获，改为 `self.report({'ERROR'}, traceback)`，然后返回 `{'FINISHED'}`。
  - 实测：从 Python 调用、目标目录不存在时，`bpy.ops.mmd_tools.export_pmx` 抛出 `RuntimeError`（Blender 把报告的 ERROR 转成了异常），文件没有生成 — [实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
- 算子 `ImportPmx`（`'mmd_tools.import_model'`，支持 `.pmx;.pmd`）的选项 — [fileio.py:49-206](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)、[src/translations.py:286-325](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/translations.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)：
  - `types`：`MESH, ARMATURE, PHYSICS, DISPLAY, MORPHS`，默认全选；PHYSICS / DISPLAY 会自动带上 ARMATURE，MORPHS 会带上 ARMATURE+MESH。
  - `scale` 1.0、`clean_model` True、`remove_doubles` False、`fix_IK_links` False、`apply_bone_fixed_axis` False。
  - `rename_bones` True（"Rename Bones - L / R Suffix"）、`use_underscore` False。
  - `dictionary`：动态枚举，导入时首项是 `DISABLED`，可选 `INTERNAL`、文本块 CSV、偏好目录 CSV。
  - `use_mipmap` True、`sph_blend_factor` 1.0、`spa_blend_factor` 1.0、`log_level`、`save_log`。
  - 没有 `ik_loop_factor`、`bone_disp_mode`、`fix_bone_order`。
- 导入器也可以直接调用 `execute(**args)`。实测 B/C 用的是 `PMXImporter().execute(filepath=…, types=…, scale=…, rename_LR_bones=…, clean_model=…)`；注意参数名是 `rename_LR_bones`、`fix_IK_links`、`translator`，与算子属性名不同 — [src/core/pmx/importer.py:809-891](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)。
- 纯 Python 读写器 `mmd_tools.core.pmx.load(path)` / `save(path, model, add_uv_count)`：PMX 2.0、utf-16-le，自动选择索引宽度；可以在不建 Blender 对象的情况下做验证 — [src/core/pmx/__init__.py:1589-1618](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/__init__.py)。实测 A–K 都用它读回结果。

### Inferences
- 插件直接调用导出函数时，照着算子的流程做：
  1. 切到 OBJECT 模式；
  2. `arm.data.pose_position='REST'`，`arm.update_tag()`，`scene.frame_set(scene.frame_current)`；
  3. `export(filepath, root=root, armature=arm, meshes=list(rig.meshes()), rigid_bodies=list(rig.rigidBodies()), joints=list(rig.joints()), scale=<见下>, copy_textures=True, sort_materials=False, sort_vertices='NONE', disable_specular=False, overwrite_bone_morphs_from_pose_library=False, translate_in_presets=False)`；
  4. 在 finally 里恢复 pose_position。
- 比例约定：如果模型在 Blender 里按米搭建（1 MMD 单位≈8 cm），导出用 `scale=12.5`，复检导入用 `scale=0.08`（xps_to_mmd 的测试也是这样用的）。1.0.2 的 UI 默认值是 1.0，必须显式传。
- 没有分配到有效骨的顶点会被绑到骨 0（`全ての親`），检查器必须报出来。

### Gaps
- 未实测：视口禁用（`hide_viewport`）的网格，或放在被排除集合里的网格，导出时会怎样。

---

## Q11. 翻译

### Takeaway
1.0.2 只有日→英翻译：
- **翻译数据**：内置子串替换词典 `jp_to_en_tuples`，外加可选的 CSV。
- **`translate_mmd_model`**：填 `name_e`，或者（实验性）改 Blender 名。
- **实验性 "Global Translation"**：`show_global_translation_popup` / `execute_translation_script`，基于 `Object.mmd_data_query`。
- **导入时的 `rename_bones`**：用 `convertNameToLR` 把 `左X` 改成 `X.L`（开启 `use_underscore` 时是 `_L`），`name_j` 仍保持日文。
- **没有**英→日词典。

### Cited Findings
- 词典 — [src/translations.py:8-158](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/translations.py)：
  - `jp_half_to_full_tuples`：半角片假名 → 全角。
  - `jp_to_en_tuples`，例如 `('全ての親','ParentNode')`、`('操作中心','ControlNode')`、`('センター','Center')`、`('グルーブ','Groove')`、`('上半身','UpperBody')`、`('下半身','LowerBody')`、`('手首','Wrist')`、`('足首','Ankle')`、`('両目','Eyes')`、`('目','Eye')`、`('肩','Shoulder')`、`('腕','Arm')`、`('ひじ','Elbow')`、`('親指','Thumb')`、`('人指','IndexFinger')`、`('足','Leg')`、`('ひざ','Knee')`、`('つま','Toe')`、`('捩','Twist')`、`('ダミー','Dummy')`、`('右','Right')`、`('左','Left')`、`('先','Tip')`；另含全角数字/字母 → 半角，以及 `('.', '_')`。
- `MMDTranslator.translate(name, default)` 的流程 — [translations.py:183-249](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/translations.py)：
  1. 先把半角转成全角；
  2. 按元组（已按长度降序排序）做子串替换；
  3. 结果不是纯 ASCII 时记入 `fails`，并返回 default。
  - `save_fails()` 把失败项写到文本块 `mmd_tools.translations.fails`。
- `DictionaryEnum.get_dictionary_items` 的选项顺序：导入类算子首项为 `DISABLED`；然后是 `INTERNAL`、`bpy.data.texts` 中的 `.csv`、偏好 `dictionary_folder`（默认为插件目录）中的 `.csv` — [translations.py:286-325](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/translations.py)。
- `mmd_tools.translate_mmd_model` 的选项 — [src/operators/model.py:321-487](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)：
  - `dictionary`。
  - `types`：`BONE, MORPH, MATERIAL, DISPLAY, PHYSICS, INFO`，默认不含 INFO。
  - `modes`：`MMD`（填英文名）/ `BLENDER`（改 Blender 名），默认 MMD。
  - `use_morph_prefix`（G_/B_/UV_/M_）、`overwrite`、`allow_fails`。
  - `translate_bone` 会跳过影子骨。
- Global Translation — [src/properties/root.py:452-567](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/root.py)、[src/core/model.py:547-586](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)、[src/operators/model.py:499-589](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)：
  - `MMDDataQuery` 的字段：`filter_types`、`filter_japanese_blank/english_blank/selected/visible`、`dictionary`、`operation_target`（`BLENDER/JAPANESE/ENGLISH`，默认 JAPANESE）、`operation_script_preset`（`NOTHING/TO_ENGLISH/TO_MMD_LR/TO_BLENDER_LR`）、`operation_script`。
  - 执行时调用 `FnModel.translate_in_presets(root)`：对查询结果逐项 `eval` 脚本，再写回目标字段。脚本里可用 `to_english`、`to_mmd_lr`、`to_blender_lr`、`name`、`name_j`、`name_e`。
  - 导出选项 `translate_in_presets` 也会执行这一步。
- `convertNameToLR(name, use_underscore)`：正则 `^(.*)左(.*)$` → `\1\2.L`（右同理）；`convertLRToName` 反过来，把 `.L/_L` 变成前缀 `左` — [src/utils.py:54-78](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/utils.py)。
- 实测 `rename_bones=True` 的效果 — [实测C](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[src/core/pmx/importer.py:792-796](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/importer.py)、[src/core/model.py:1019-1034](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)：
  - Blender 骨名：`左目→目.L`、`左肩P→肩P.L`、`左足ＩＫ→足ＩＫ.L`、`左つま先ＩＫ→つま先ＩＫ.L`；`name_j` 仍是 `左…`。
  - 顶点组、表示枠条目和 IK subtarget 跟着改名。
  - 影子骨按新名字生成。
- VMD 导入的骨映射默认是 `PMX`，使用 `makePmxBoneMap`：优先用 `mmd_bone.name_j`，其次用旧版自定义属性 `mmd_bone_name_j` / `name_j`，最后用 Blender 骨名 — [src/operators/fileio.py:229-238](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)、[src/utils.py:159-161](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/utils.py)。

### Inferences
- XPS 英文骨名 → MMD 日文名的映射必须由我们的映射表提供。
- 填好 `name_j` 后，可以调 `translate_mmd_model(types={'BONE'}, modes={'MMD'})` 补 `name_e`；但更推荐直接写标准英文名，因为内置词典按子串替换，结果（如 "LeftEye"、"LeftArmTwist"）不一定符合社区惯例。
- 由于 VMD 绑定用的是 `name_j`，Blender 骨名可以保留 `.L/.R` 风格（与 mmd_tools 导入默认一致），也可以直接用日文名。关键是 `name_j` 必须填。

### Gaps
- 无。

---

## Q12. mmd_uuunyaa_tools v1.8.0

### Takeaway
v1.8.0 于 2024-04-24 发布，仓库现名 MMD-Blender/blender_mmd_tools_append。它用 `importlib.import_module('mmd_tools')` 导入 legacy 包。
- **提供的功能**：
  - Rigify / Auto-Rig Pro 与 MMD 骨架之间的互转和绑定（按 `mmd_bone.name_j` 识别 `MMDBoneInfo` 标准骨）；
  - 刚体→布料、胸部金字塔布料；
  - 材质和灯光预设等。
- **没有的功能**：Mixamo 转换、Humanoid Renamer、刚体链生成器。
- **面向 mmd_tools 2.x 编写**：
  - 引用了 1.0.2 中不存在的 `mmd_tools.bpyutils.activate_layer_collection`；
  - 导入时会给 `Model` 打补丁，加上 `clothGroupObject` / `cloths`。

### Cited Findings
- bl_info：`'name': 'mmd_uuunyaa_tools'`、`'version': (1, 8, 0)`、`'blender': (3, 6, 0)`、`'author': 'UuuNyaa'`，wiki/tracker 指向 `UuuNyaa/blender_mmd_uuunyaa_tools` — [uuu/__init__.py:25-37](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/__init__.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。Release v1.8.0：2024-04-24T02:45:31Z 发布，资产 `mmd_uuunyaa_tools-v1.8.0.zip`，说明中含 "Blender 4.x is not supported yet" — [Releases API](https://api.github.com/repos/MMD-Blender/blender_mmd_tools_append/releases/tags/v1.8.0)。
- 导入 mmd_tools 的方式 — [uuu/utilities.py:68-76](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/utilities.py)：
  - `import_mmd_tools()` 调用 `importlib.import_module('mmd_tools')`；失败时抛 `RuntimeError("MMD Tools is not installed correctly…")`。
  - `is_mmd_tools_installed()` 用的是已弃用的 `importlib.find_loader('mmd_tools')`。
  - 没有版本检查。
  - 调用示例：`import_mmd_tools().core.model.Model.findRoot(obj)`、`Model(root).allObjects()/armature()/joints()`、`mmd_tools.cycles_converter.convertToCyclesShader(obj, use_principled=True, clean_nodes=True)`、`bpy.ops.mmd_tools.import_model('INVOKE_DEFAULT', …)` — [uuu/converters/armatures/mmd.py:162-170](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/armatures/mmd.py)、[uuu/editors/operators.py:33-35](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/editors/operators.py)、[uuu/asset_search/actions.py:337-371](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/asset_search/actions.py)。
- 与 1.0.2 的兼容性：
  - `UuuNyaaPhysicsPanel._toggle_visibility_of_cloths` 使用 `mmd_tools.bpyutils.activate_layer_collection`，而 1.0.2 中没有这个函数（实测 `False`）。因此切换 `mmd_uuunyaa_tools_show_cloths` 会报错 — [uuu/panels.py:146-158](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/panels.py)、[实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
  - `converters/physics/cloth.py` 在模块导入时检查 `Model` 是否有 `clothGroupObject`；没有就注入 `clothGroupObject`（root 下名为 `cloths` 的 Empty）和 `cloths` — [uuu/converters/physics/cloth.py:15-46](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/physics/cloth.py)、[实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
- 骨架数据结构 — [uuu/converters/armatures/mmd.py:15-298](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/armatures/mmd.py)：
  - `MMDBoneType` 共 17 项：`STANDARD='標準'`、`PARENT='全ての親'`、`UPPER_ARM_TWIST='腕捩'`、`WRIST_TWIST='手捩'`、`UPPER_BODY_1='上半身1'`、`UPPER_BODY_2='上半身２'`、`GROOVE='グルーブ'`、`TOLSO='腰'`、`LEG_IK_PARENT='足IK親'`、`CONTROL='操作中心'`、`TOE_EX='足先EX'`、`LEG_D='足D'`、`HAND_ACCESSORIES='手持ちアクセサリ用ダミー'`、`SHOULDER_CANCEL='肩キャンセル'`、`THUMB_0='親指０'`、`PALM='指０'`、`OTHERS='その他・独自'`。
  - `MMDBoneInfo` 是标准/准标准骨的全集：`全ての親…上半身2（半角）…両目/左目/右目…左腕捩/左手捩…左親指０～２、左人指０～３…左足ＩＫ、左足先EX、左足D/左ひざD/左足首D、左つま先ＩＫ、左つま先、左肩C/左肩P、左ダミー、左足IK親`，右侧同构。
  - `MMDArmatureObject` 以 `pose_bone.mmd_bone.name_j` 为键（`strict_pose_bones` 等）；`clean_armature()` 用来规整手指、脊柱和脚尖。
- 绑定表 — [uuu/converters/armatures/mmd_bind.py:15-136](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/armatures/mmd_bind.py)、[uuu/converters/armatures/rigify.py:25-123](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/armatures/rigify.py)：
  - `mmd_bind.py` 定义了 `GroupType`、`MMDBindType`（`NONE=0` … `COPY_LEG_D=8`）、`MMDBindInfo(bone_info, pose_bone_name, bind_bone_name, group_type, bind_type)`、`ControlType`（如 `bind_mmd_uuunyaa`，1.8.0 的名字里带 `uuunyaa`）。
  - `assign_mmd_bone_names()` 只写 `name_j`。
  - Rigify 绑定表的例子：`上半身→('spine_fk.002','DEF-spine.002',COPY_POSE)`、`左足首→('foot_fk.L','DEF-foot.L')`、`左足D→(None,'DEF-thigh.L',COPY_LEG_D)`、`左肩C→'mmd_uuunyaa_shoulder_cancel.L'`、`両目→'mmd_uuunyaa_eyes_fk'`。
- 骨架算子 — [uuu/converters/armatures/operators.py:17-488](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/armatures/operators.py)、[实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)：
  - `mmd_armature_add_metarig`（选项 `is_clean_armature`、`is_clean_koikatsu_armature`）。
  - `mmd_rigify_mmd_focused_integrate` / `mmd_rigify_rigify_focused_integrate`：选项有 `is_join_armatures`、`mmd_main_bone_layer` 24、`mmd_others_bone_layer` 25、`mmd_shadow_bone_layer` 26、`mmd_dummy_bone_layer` 27。其中 `join_armatures` 把 MMD 骨按所在层 0/8/9 分别移到层 24/26/27，也就是按 1.0.2/2.x 的层约定来识别影子骨和 Dummy 骨。
  - `rigify_to_mmd_compatible`、`rigify_apply_mmd_rest_pose`、`autorig_to_mmd_compatible`、`autorig_apply_mmd_rest_pose`。
- 物理功能 — [uuu/converters/physics/cloth.py:56-322](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/physics/cloth.py)、[uuu/converters/physics/rigid_body_to_cloth.py:47-60](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/physics/rigid_body_to_cloth.py)、[uuu/converters/physics/cloth_pyramid.py:773-886](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/converters/physics/cloth_pyramid.py)、[uuu/panels.py:84-144](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/panels.py)：
  - `convert_rigid_body_to_cloth`（提示 "Select both the mesh to be deformed and the rigid body"）：调用 `RigidBodyToClothConverter.convert(mmd_root_object, rigid_body_objects, mesh_objects, subdivision_level, ribbon_stiffness, physics_mode, extend_ribbon_area)`，读取 Joint 构建布料网格，然后删除原刚体和 Joint。
  - `add_pyramid_mesh_by_breast_bone` / `convert_pyramid_mesh_to_cloth` / `assign_pyramid_weights`。
  - `stretch_bone_to_vertex`、`add_center_of_gravity_object`。
  - `select_rigid_body_mesh`、`select_cloth_mesh`、`select_collision_mesh`、`remove_mesh_cloth`、`remove_mesh_collision`。
  - 预设：`PHYSICS_CLOTH_NOTHING/COTTON/SILK/BREAST_PYRAMID` 等。
  - **没有**刚体链/发链生成器、Mixamo 转换或 Humanoid Renamer（对照算子清单）— [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。
- 材质 / 灯光预设 — [uuu/tuners/material_tuners.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/tuners/material_tuners.py)、[uuu/tuners/lighting_tuners.py:49-132](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/tuners/lighting_tuners.py)、[uuu/tuners/operators.py:11-82](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/tuners/operators.py)：
  - 算子：`tune_material`、`tune_lighting`、`freeze_lighting`、`attach_material_adjuster`、`detach_material_adjuster`。
  - 材质预设：`MATERIAL_RESET, TRANSPARENT, EYE_HIGHLIGHT, EYE_WHITE, EYE_IRIS, EYE_LASH, HAIR_MATTE, SKIN_MUCOSA, SKIN_BUMP, METAL_NOBLE, METAL_BASE, STONE_GEM, FABRIC_BUMP, FABRIC_WAVE, FABRIC_COTTON, FABRIC_SILK, FABRIC_KNIT, FABRIC_LEATHER, PLASTIC_GLOSS, PLASTIC_BUMP, PLASTIC_MATTE, PLASTIC_EMISSION, LIQUID_WATER, LIQUID_CLOUDY, ARTISTIC_WATERCOLOR, TOON_SHADER`。
  - 灯光预设：`LIGHTING_RESET, LEFT_ACCENT, DOUBLE_SIDE_ACCENT, GOD_RAY, BACKLIGHT, LIGHT_PROBE_GRID, SHADOWLESS`。
  - 资源文件：`blends/UuuNyaa_Materials.blend`、`UuuNyaa_Lightings.blend`、`UuuNyaa_Geometries.blend`、`RigShapeLibrary.blend`（见目录列表）。
- 其它：Eevee/Workbench 渲染设置、`convert_materials_for_eevee`、`remove_unused_vertex_groups`、`remove_unused_shape_keys`、自动分割等 — [uuu/editors/operators.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_uuunyaa_tools/editors/operators.py)。

### Inferences
- uuunyaa 对我们插件的价值在于：
  - `MMDBoneInfo` 标准骨清单；
  - Rigify 绑定表，可作为映射参考；
  - 按 `name_j` 识别骨的做法；
  - `join_armatures` 证明"层 8/9 = 影子/Dummy"是 2.x 生态的约定。
- 它不提供可复用的 XPS 转换或刚体生成功能。
- 我们的插件导入 mmd_tools 时可以沿用 `importlib.import_module('mmd_tools')`，再按 `bl_info['version']` 分支；不要依赖 uuunyaa 注入的 `Model.cloths` 等方法。

### Gaps
- 未阅读 Rigify 绑定方法体和布料转换算法的细节，它们与本插件主线无关。

---

## Q13. 外部插件调用 mmd_tools 1.0.2 的坑

### Takeaway
1.0.2 的核心函数大量依赖 `bpy.context`（活动集合、活动对象、选择、模式）和 `bpy.ops`。它们会改动选择、活动对象和模式，甚至会取消集合的排除状态。属性的 update 回调可能在不经意间改掉材质节点，或者触发编辑模式往返。我们需要一个统一的"上下文守卫"，并尽量用 ID-prop 写数据。

### Cited Findings
1. **集合与可见性副作用**：`SceneOp.link_object` 把对象链接到 `bpy.context.collection`。`SceneOp.select_object` / `active_object` 会设 `hide_viewport=hide_select=False`、调 `hide_set(False)`，必要时还会把对象所在 layer collection 的 `exclude` / `hide_viewport` 关掉 — [src/bpyutils.py:428-472](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)。`Model.create`、`createRigidBodyPool`、`createJointPool`、`bpyutils.edit_object/select_object` 都会走到这里 — [model.py:601-638,678-804](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)。
2. **模式与选择**：`bpyutils.edit_object(armature)` 会切到 OBJECT 模式、**取消全部选择**、选中并激活骨架、进入 EDIT 模式；退出时回到原模式，但只恢复这个骨架的 select 状态 — [bpyutils.py:22-69,89-108](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/bpyutils.py)。`FnBone.apply_additional_transformation`、`clean_additional_transformation`、`apply_bone_fixed_axis`、`apply_bone_local_axes`、`apply_auto_bone_roll` 都用它 — [src/core/bone.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)。
3. **属性回调**：
   - 付与属性：活动 pose bone 恰好是该骨时会立即 apply（见 Q4）。
   - `mmd_material` 的 RNA 写入，以及 `mmd_root.use_toon_texture/use_sphere_texture`，会改材质节点（见 Q7，实测 I）。
   - `mmd_material.name_j` 的去重依赖活动对象（见 Q7）。
   - `mmd_rigid.size` 的 setter 要求 OBJECT 模式（有 assert）— [src/properties/rigid_body.py:77-79](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/properties/rigid_body.py)。
4. **算子上下文**：
   - `export_pmx.poll` 要求活动对象被选中且属于模型 — [fileio.py:496-499](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/fileio.py)。
   - `apply/clean_additional_transform`、`build_rig`、`display_item_*` 等都通过 `context.active_object` 找 root — [src/operators/model.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/model.py)、[display_item.py](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/operators/display_item.py)。
   - `bone_fixed_axis_setup` / `bone_local_axes_setup` 的 `LOAD` 只作用于**选中的**骨 — [src/core/bone.py:65-90,140-148](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)。
   - 算子内部的异常被吞掉并改成 ERROR 报告；从 Python 调用时，表现为抛出 `RuntimeError` — [实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
5. **骨骼组与骨骼层**：Blender 3.6 既有 `pose.bone_groups`，也有 32 个骨骼层。1.0.2 用 bone groups 同步表示枠，用层 8/9 放影子/Dummy 骨，导出可见性看层（见 Q4、Q6、Q10）。
6. **`Model.build()` 的副作用**：改刚体的父子关系和变换、静音 IK、建临时对象、设 `is_built=True`。导出前应先 clean（见 Q9）。
7. **root 与 `mmd_root`**：`Model(obj)` 要求 `mmd_type=='ROOT'`；骨架必须是 root 的**第一个** ARMATURE 子对象；网格必须是骨架的（递归）子对象，且 `mmd_type=='NONE'`（见 Q2）。
8. **隐藏对象**：`rig.meshes()` 包含隐藏的网格，它们都会被导出（除非开启 `visible_meshes_only`）；导出也不检查 view layer（见 Q10）。
9. **Pose Library 已移除**：`overwrite_bone_morphs_from_pose_library` 在 3.6 会报错 — 见 Q8、[实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
10. **旧式上下文覆盖**：`Model.clean()` 里有 `bpy.ops.object.delete({'selected_objects': …, 'active_object': …})`，`FnMorph.copy_uv_morph_vertex_groups` 也用 override dict。Blender 3.x 仍可用，4.0 已移除 — [src/core/model.py:1120-1125](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/model.py)、[src/core/morph.py:124-133](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/morph.py)。
11. **默认比例 1.0**：导入、导出、Create Model 的 scale 默认都是 1.0（见 Q10）。
12. **本地化数据名**：本机 UI 是 zh_CN 且开启了"翻译新数据名"，默认的节点名、对象名都不是英文 — [实测J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)。
13. **`bone_id` 唯一性**：付与和骨骼 morph 的引用都按 bone_id 解析，且只取第一个匹配（见 Q4）。
14. **骨序网格唯一性**：导出取按名排序后第一个带该修改器的网格，面板取骨架直接子对象中的第一个，两者可能不一致（见 Q3）。
15. **IK 链节上的 LIMIT_ROTATION**：导出器把第一个未静音的 LIMIT_ROTATION 当作 IK 限制（见 Q5）。
16. **uuunyaa 1.8.0 与 1.0.2 不完全兼容**：缺 `activate_layer_collection`（见 Q12）。
17. **内置更新器可能改变版本**（见 Q1）。
18. **headless 可行性**：在 `blender.exe --background --python` 下，以下调用都能运行：`Model.create`、`apply_additional_transformation`（含编辑模式往返）、`createRigidBody/createJoint`（含 `bpy.ops.rigidbody.*` 和 `object.duplicate`）、`PMXImporter().execute`、`exporter.export`、`bpy.ops.mmd_tools.apply_additional_transform/export_pmx` — [实测A–F](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测G–J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)、[实测K](assets/08_mmd_tools_1.0.2/verify_live3_102.json)。
    - 注意：`bpy.ops.wm.read_factory_settings()` 会把用户插件一并卸掉。首批实测就因此出现 `'Object' object has no attribute 'mmd_type'`，自动化测试应改为清空数据块 — [实测V 中 `additional_transform_live_test` 的报错](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)。

### Inferences
- 封装一个上下文守卫，所有 mmd_tools 调用都包在里面。守卫在进入时记录、退出时恢复：模式、活动对象、选择集、`arm.data.pose_position`、集合的排除/隐藏状态。
- 写入策略：
  - 骨属性用 RNA 写（付与目标需要靠 setter 解析成 bone_id），但要在 OBJECT 模式且没有活动 pose bone 时写；
  - 材质字段用 ID-prop 写；
  - 最后统一 apply、再导出。

### Gaps
- 未测：在大模型（数百根骨）上 `apply_additional_transformation` 的耗时。

---

## Q14. 我们的插件应如何调用（按阶段）

### Takeaway
插件按以下阶段调用 mmd_tools：
1. 探测环境
2. 收编为 MMD 模型
3. 写骨骼属性
4. 定骨序
5. 设付与
6. 建 IK
7. 处理材质
8. 处理 morph
9. 建表示枠
10. 建物理
11. 导出
12. 复检

每个阶段只用本笔记已验证过的 1.0.2 API，并全部包在上下文守卫里。为了以后支持 2.x/4.x，用一张 API 对照表做兼容层。

### Cited Findings
- 各步骤的依据见 Q1–Q13 的对应条目：
  - `Model.create` 的签名与副作用 — [实测V](assets/08_mmd_tools_1.0.2/verify_mmd_tools_102.json)、[实测A](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测H](assets/08_mmd_tools_1.0.2/verify_live2_102.json)
  - 骨序机制 — [实测D/B](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测G](assets/08_mmd_tools_1.0.2/verify_live2_102.json)
  - 付与与影子骨 — [实测A/B/C](assets/08_mmd_tools_1.0.2/verify_live_102.json)
  - IK — [实测B](assets/08_mmd_tools_1.0.2/verify_live_102.json)
  - 材质的 ID-prop 写法 — [实测I](assets/08_mmd_tools_1.0.2/verify_live2_102.json)、[实测K](assets/08_mmd_tools_1.0.2/verify_live3_102.json)
  - 刚体 — [实测F](assets/08_mmd_tools_1.0.2/verify_live_102.json)
  - 导出与复检 — [实测A–F](assets/08_mmd_tools_1.0.2/verify_live_102.json)、[实测G–J](assets/08_mmd_tools_1.0.2/verify_live2_102.json)、[实测K](assets/08_mmd_tools_1.0.2/verify_live3_102.json)
- 4.5.5 一列的事实来自 [02 笔记](02_mmd_tools导出契约.md)（Q1、Q2、Q6、Q9、Q11）。
- 1.0.2 与 4.5.5 的 API 对照（兼容层用）：

| 用途 | 1.0.2（本机） | 4.5.5（02 笔记） |
|---|---|---|
| 包与版本 | `importlib.import_module('mmd_tools')`；`bl_info['version'] == (1,0,2)` | `bl_ext.<repo>.mmd_tools`；`MMD_TOOLS_VERSION == "4.5.5"` |
| 建 root / 收编骨架 | `Model.create(name, name_e, scale, obj_name, armature=…, add_root_bone=…)` | `Model.create(…, armature_object=…, …)`，并建骨骼集合 `mmd_shadow`/`mmd_dummy` |
| 找 root | `Model.findRoot(obj)` / `FnModel.find_root(obj)` | `FnModel.find_root_object(obj)` |
| 找骨架 | `Model(root).armature()` / `FnModel.find_armature(root)` | `FnModel.find_armature_object(root)` |
| 遍历网格 | `Model(root).meshes()` / `FnModel.child_meshes(arm)` | `FnModel.iterate_mesh_objects(root)` |
| 挂网格 | 无 API；自己设 parent 并加修改器 | `FnModel.attach_mesh_objects(root, objs, add_armature_modifier=True)` |
| 初始化表示枠 | `Model(root).initialDisplayFrames(reset)` | `FnModel.initalize_display_item_frames(root, reset)` |
| 骨序 | `mmd_bone_order_override` 网格的顶点组顺序 | `mmd_bone.bone_id` 升序，加 `fix_bone_order` |
| 影子 / Dummy 骨归属 | 骨骼层 8 / 9 | 骨骼集合 `mmd_shadow` / `mmd_dummy` |
| 付与约束的旋转设置 | AUTO / AUTO / ADD（Blender 默认） | ZYX 或 XYZ / XYZ / AFTER |
| IK 迭代因子 | `arm['mmd_ik_loop_factor']`（导入不乘） | `mmd_root.ik_loop_factor`（导入默认 5） |
| `mmd_ik_limit_override` 的空间 | `owner_space='POSE'` | `'LOCAL'` |
| 刚体 / Joint | `Model.createRigidBody(**kw)` / `createJoint(**kw)` | `FnRigidBody.new_*_object` + `setup_*_object` |
| 导出 scale 默认值 | 1.0 | 12.5 |
| 贴图复制 | `copy_textures` 布尔值，不处理打包贴图 | `copy_textures_mode` 枚举，会写出打包贴图 |
| morph 导出顺序 | 按类型固定（顶点→骨骼→材质→UV→组） | 按 `表情` 枠排序 |
| 表示先 | 只由 `use_connect` 子骨 / `is_tip` / 偏移量推导 | `display_connection_type/bone` 属性 |

### Inferences（按阶段的清单）

**阶段 0：环境探测**
- [ ] `mod = importlib.import_module('mmd_tools')`，`ver = mod.bl_info['version']`，`is_4x = hasattr(mod, 'MMD_TOOLS_VERSION')`。1.0.x / 2.x 走"顶点组骨序"分支；4.x 走 `bone_id` 分支。
- [ ] 功能探测：1.0.2 下 `'fix_bone_order' in dir(bpy.ops.mmd_tools)` 应为 False。IK 因子在 2.x 写 `mmd_root.ik_loop_factor`，在 1.0.2 写 `arm['mmd_ik_loop_factor']`（或干脆不写）。
- [ ] 记录上下文（模式、活动对象、选择、集合状态），结束时恢复。

**阶段 1：准备 XPS 场景**
- [ ] 切到 OBJECT 模式。XPS 骨架和网格所在的集合不能被排除，对象不能被视口禁用。对骨架和网格 Apply 变换，让 root 保持单位矩阵。
- [ ] 把贴图解包到磁盘（1.0.2 不导出打包图像）。
- [ ] 清掉 XPS 骨架上无关的 pose bone groups，否则它们会变成表示枠。

**阶段 2：收编为 MMD 模型**
- [ ] `rig = Model.create(name_j, name_e, scale=0.08, obj_name=<root名>, armature=xps_arm, add_root_bone=False)`。`全ての親` 由我们的补骨流程自己创建，以保证它是第一个根骨。
- [ ] 网格 `parent = 骨架`，保持世界矩阵；每个网格配一个普通名字的 ARMATURE 修改器（不要叫 `mmd_bone_order_override`）。
- [ ] `rig.initialDisplayFrames(reset=True)`。

**阶段 3：骨骼数据**
- [ ] 在编辑模式里改名和补骨；顶点组名与 Blender 骨名保持一致。
- [ ] 每根非影子骨写入以下内容：
  - `name_j`：必填；最好能用 cp932 编码且不超过 15 字节。
  - `name_e`、`transform_order`、`transform_after_dynamics`、`is_controllable`。
  - `lock_location` / `lock_rotation`：它们决定 PMX 里的"可移动 / 可回転"。
  - 可见性：`bone.hide=False`，且骨在可见的骨骼层 0 上。
  - `is_tip`。
  - `enabled_fixed_axis` / `fixed_axis`、`enabled_local_axes` / `local_axis_x/z`：按 PMX 坐标写，遵循 .xzy 约定，见 [02 笔记 Q2](02_mmd_tools导出契约.md)。
- [ ] 不要给真实骨用 `_dummy_` / `_shadow_` 前缀。

**阶段 4：骨序**
- [ ] 按目标 PMX 顺序，给全部非影子骨赋唯一的 `bone_id = 0..N-1`。这是为了兼容 4.x，而且必须在付与之前做。
- [ ] 创建（或重建）承载网格 `000_mmd_bone_order`：0 顶点，作为骨架的直接子对象；按同一顺序 `vertex_groups.new(name)`，覆盖全部非影子骨；再加修改器 `modifiers.new('mmd_bone_order_override', 'ARMATURE').object = arm`。确认全模型只有它带这个名字。
- [ ] 检查顺序满足：父骨在子骨前；付与亲在被付与骨前；IK 链节在 IK 骨前；足D 系排在 IK 骨之后，且 `transform_order=1`。

**阶段 5：付与**
- [ ] 在 OBJECT 模式、且骨架没有活动 pose bone（或活动骨不在本批里）时，依次写 `has_additional_rotation/location` → `additional_transform_influence` → `additional_transform_bone`。写完读回 `additional_transform_bone`，确认非空。
- [ ] 一次性调用 `FnBone.apply_additional_transformation(arm)`；或者调用 `bpy.ops.mmd_tools.apply_additional_transform()`，此时活动对象要是 root 或骨架。
- [ ] 之后如果又改了骨的 roll 或父子关系，重新 apply 一次，必要时先 `clean_additional_transformation`。

**阶段 6：IK**
- [ ] 在 `左ひざ` 上建 `IK`：`target=arm, subtarget='左足ＩＫ', chain_count=2, iterations=40, use_tail=True`，并设 `左ひざ.mmd_bone.ik_rotation_constraint=2.0`。
- [ ] 在 `左足首` 上建 `IK`：`subtarget='左つま先ＩＫ', chain_count=1, iterations=3`，并设 `左足首.mmd_bone.ik_rotation_constraint=4.0`。右侧同理；数值依据见 [03 笔记](03_MMD骨骼规范与准标准骨.md)。
- [ ] 在 `左足首` 和 `左つま先` 上各加一个 DAMPED_TRACK `mmd_ik_target_override`：`mute=True, influence=0, target=arm, subtarget=约束骨`。
- [ ] 膝盖限制：用 `PMXImporter.convertIKLimitAngles((-π,0,0), (-0.5°,0,0), pb.bone.matrix_local)` 换算，写 `use_ik_limit_*`、`ik_min/max_*`，再加 LIMIT_ROTATION `mmd_ik_limit_override`（`owner_space='POSE'`，按导入器的规则设 `use_limit_*`）。

**阶段 7：材质（保留 HD）**
- [ ] 用 ID-prop 写 `mmd_material` 字段。`name_j` 用 ID-prop 写，或者在活动对象属于该模型时用 RNA 写。`sphere_texture_type` 的 ID-prop 取值为 1–4。
- [ ] 把现有的 `ShaderNodeTexImage` 改名为 `mmd_base_tex`（需要时再加 `mmd_sphere_tex`）。toon 用 `is_shared_toon_texture` / `shared_toon_texture`，也用 ID-prop 写。
- [ ] 不要切换 `mmd_root.use_toon_texture` / `use_sphere_texture`；不要调用 Convert Model，它会改节点。
- [ ] 同名材质跨网格会被合并，需要分开时改名。设 `root['import_folder']=贴图根目录`，以保留目录结构。

**阶段 8：Morph（可选）**
- [ ] 形态键名就是日文 morph 名。`vertex_morphs.add()` 后填 `name/name_e/category`，并按期望顺序排列（没登记的会排到最前）。组 morph 要显式写 `factor`；UV morph 用 `VERTEX_GROUP`。

**阶段 9：表示枠**
- [ ] 直接写 `display_item_frames`：`Root` 里放 `全ての親`；`表情` 用 `DisplayItemQuickSetup.load_facial_items` 填；其余枠写上英文 `name_e`。条目用 Blender 骨名，不要放影子骨。

**阶段 10：物理（可选）**
- [ ] 用 `rig.createRigidBody(...)` / `rig.createJoint(...)` 建；用 `MoveObject.set_index(obj, i)` 定顺序；保持 `is_built=False`。

**阶段 11：导出**
- [ ] 方式一：直接调函数。切到 OBJECT 模式；设 `arm.data.pose_position='REST'`，`arm.update_tag()`，`scene.frame_set(scene.frame_current)`；调用 `mmd_tools.core.pmx.exporter.export(...)`，参数见 Q10，其中 `scale=12.5`、`copy_textures=True`、`overwrite_bone_morphs_from_pose_library=False`、`translate_in_presets=False`；在 finally 里恢复。
- [ ] 方式二：用算子。选中并激活 root，调用 `bpy.ops.mmd_tools.export_pmx(filepath=…, scale=12.5)`，并捕获 `RuntimeError`。

**阶段 12：复检**
- [ ] 用 `m = mmd_tools.core.pmx.load(path)` 在纯 Python 里检查骨、付与、IK、表示枠、材质、刚体（检查项见 Q15）。
- [ ] 视觉复检：`bpy.ops.mmd_tools.import_model(filepath=…, scale=0.08, types={'MESH','ARMATURE','PHYSICS','DISPLAY','MORPHS'}, rename_bones=False, clean_model=False)`。导入器会建 MMD 着色节点；导入后可以再为 HD 材质重新挂节点。

### Gaps
- 阶段 4 的承载网格与 `join_meshes` 等用户操作之间的交互，以及与 VMD 表情导出（`firstMesh`）的交互，都没有实测。

---

## Q15. 映射 / 付与 / 影子骨 检查器可以验证什么

### Takeaway
检查器可以在两层做确定性校验：
- **Blender 数据层**：导出前检查。
- **PMX 层**：导出后用 `pmx.load` 读回检查。

下面每一项都对应本笔记中的一条 1.0.2 源码行为或实测结果。

### Cited Findings
- 骨序规则 — [exporter.py:334-343](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)；面板的 rank 与 IK 链检查 — [util_tools.py:236-276](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/panels/util_tools.py)。
- 付与属性、约束、影子骨的行为 — [src/core/bone.py:237-418](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/bone.py)、[实测A/B](assets/08_mmd_tools_1.0.2/verify_live_102.json)。
- 导出的名称回退与权重规则 — [exporter.py:152-195,364](file:///C:/Users/haoni/AppData/Roaming/Blender%20Foundation/Blender/3.6/scripts/addons/mmd_tools/core/pmx/exporter.py)。
- PMX 变形顺序规范（"物理前/後 → 階層 → Index"）以及标准付与表，引自 [03 笔记](03_MMD骨骼规范与准标准骨.md)。
- cp932 / 15 字节约束来自 4.5.5 的校验器，见 [02 笔记 Q8](02_mmd_tools导出契约.md)。

### Inferences（检查项）

**A. 结构**
- [ ] 存在唯一一个 `mmd_type=='ROOT'` 的 root，它的第一个 ARMATURE 子对象就是目标骨架。
- [ ] 网格都是骨架的（递归）子对象，且 `mmd_type=='NONE'`。
- [ ] root 的世界矩阵是单位阵（否则警告：变换会被烘焙进 PMX）。
- [ ] `mmd_root.is_built == False`，`mmd_root.name` 非空。

**B. 映射（XPS→MMD）**
- [ ] 每根非影子骨的 `name_j`：非空、无重复、能用 cp932 编码、不超过 15 字节。这是 MMD 约定，1.0.2 本身不校验。
- [ ] 每根非影子骨的 `name_e` 非空（导出时没有回退）。
- [ ] 所有带权重的顶点组名都对应某根导出骨，否则这些权重会被丢弃。
- [ ] 没有"一个有效组都没有"的顶点，否则它会被绑到骨 0。
- [ ] 报出受 >4 根骨影响的顶点数（这些顶点的权重会被截断）。
- [ ] 标准骨覆盖：按 03 笔记和 uuunyaa `MMDBoneInfo` 清单检查必需骨（全ての親、センター、上半身、下半身、首、頭、両目/左右目、肩/腕/ひじ/手首、指、足/ひざ/足首/つま先、足ＩＫ/つま先ＩＫ…）。
- [ ] 可见性：应可见的骨 `bone.hide==False`，且在可见的骨骼层上；控制骨设了 `is_controllable`；`lock_*` 与期望的"可移动 / 可回転"一致。

**C. 骨序**
- [ ] 恰好有一个网格带 `mmd_bone_order_override` 修改器。它是骨架的直接子对象，并且在按名排序的网格中最先被选中。
- [ ] 它的顶点组覆盖全部非影子骨，不含影子骨，也没有多余的组名。
- [ ] 以 `rank = (transform_after_dynamics, transform_order, 顶点组索引)` 检查：
  - 父骨的 rank 小于子骨；
  - 付与亲的 rank 小于被付与骨；
  - IK 链节（以及目标骨）的 rank 小于 IK 骨；
  - 足D 系的 `transform_order` 等于原骨 +1。
- [ ] （兼容 4.x）`bone_id` 唯一，且等于期望的索引。

**D. 付与**
- [ ] 每根带标志的骨：`additional_transform_bone` 非空、指向的骨存在、不是影子骨、不是自己；影响度不为 0；`additional_transform_bone_id` 对应的 bone_id 在骨架中唯一。
- [ ] 存在以下骨时，逐一核对标准付与表：
  - `左目/右目 ← 両目`，1.0
  - `肩C ← 肩P`，−1
  - `腕捩1/2/3 ← 腕捩`，0.25 / 0.5 / 0.75
  - `手捩1/2/3 ← 手捩`，0.25 / 0.5 / 0.75
  - `足D/ひざD/足首D ← 足/ひざ/足首`，1.0
  - `腰キャンセル ← 腰`，−1
- [ ] apply 之后：
  - `is_additional_transform_dirty==False`。
  - 影响度不为 0 时，`has_additional_rotation` 为真 ⇔ 存在 TRANSFORM 约束 `mmd_additional_rotation`；位移同理。
  - 约束字段：`target==骨架`；`owner_space==target_space=='LOCAL'`；`use_motion_extrapolate==True`；旋转 `from=±π`、`to=±π×影响度`（负影响度时 to_min>to_max）；位移为 `±100`。
  - subtarget 是目标骨（对齐的情况）或 `_shadow_<骨名>`。
- [ ] 没有"有标志但目标为空"的骨；1.0.2 会把这种骨导出成索引 −1。

**E. 影子 / Dummy 骨**
- [ ] 每个 `_dummy_X`：`is_mmd_shadow_bone==True`，`mmd_shadow_bone_type=='DUMMY'`，父骨是 X 的付与目标，`use_deform==False`，只在层 9 上，没有约束。
- [ ] 每个 `_shadow_X`：类型 `'SHADOW'`，父骨是目标骨的父骨，`use_deform==False`，只在层 8 上，带 COPY_TRANSFORMS `mmd_tools_at_dummy`（subtarget `_dummy_X`，POSE/POSE）；head/tail 与 dummy 一致，roll 等于 X 的 roll。
- [ ] 没有孤儿影子骨：X 存在、X 有付与、且 X 与目标骨不"对齐"（X/Y 轴点积 ≤0.99）。不满足时应 clean 再 apply。
- [ ] 影子骨不出现在以下任何地方：顶点组、表示枠、付与目标、IK subtarget、刚体 `bone`、骨骼 morph。
- [ ] `('_shadow_'+名).encode('utf-8')` 不超过 63 字节。这是 Blender 骨名的上限，超长会被截断，可能导致重名。

**F. IK**
- [ ] 每个 IK 约束：
  - 位于"目标骨的父骨"上，`target==骨架`，`subtarget` 是一根导出骨；
  - `chain_count` 等于期望的链长，`use_tail==True`，没有被静音。
- [ ] 目标骨上有 `mmd_ik_target_override`，其 subtarget 是约束骨。
- [ ] 约束骨的 `ik_rotation_constraint` 等于期望的单位角。
- [ ] `iterations` 已把 `arm.get('mmd_ik_loop_factor', 1)` 考虑在内。
- [ ] 膝盖 X 轴限制换算后为 (−180°, −0.5°)。
- [ ] 链节骨上没有其它未静音的 LIMIT_ROTATION。

**G. 表示枠 / 材质 / 物理**
- [ ] `Root` 和 `表情` 都存在，都是 `is_special`，并且位于索引 0 / 1。
- [ ] BONE 条目都是导出骨；每根可操作的骨都出现在某个枠里，且只出现一次。
- [ ] 材质：`mmd_base_tex` 是 `ShaderNodeTexImage`，且 `image.filepath` 指向存在的文件（不是打包贴图）。
- [ ] 若要求保留 HD 材质，它的 Surface 没有被改接到 `mmd_shader`。
- [ ] 同名材质的合并结果符合预期。
- [ ] 刚体：`bone` 指向导出骨；Joint 两端的刚体都存在；对象名前缀给出的顺序符合期望。

**H. 导出后（用 `pmx.load` 读回）**
- [ ] 骨数等于非影子骨数；骨名顺序等于期望顺序。
- [ ] `hasAdditionalRotate/Location` 与 `additionalTransform` 的索引和影响度符合期望，且没有 −1。
- [ ] IK 的 `target`、`loopCount`、`rotationConstraint`、links、limits 都符合期望。
- [ ] 表示枠条目的索引正确。
- [ ] 材质贴图路径是相对路径，且文件已复制。

### Gaps
- cp932 / 15 字节约束来自 4.5.5 的校验器和社区惯例，1.0.2 本身不校验这一项。
