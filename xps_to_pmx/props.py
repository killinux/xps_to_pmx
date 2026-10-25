"""PropertyGroups holding all add-on state (design doc §3.3).

State lives in Blender data so it is saved with the .blend file and follows
Undo: ``scene.xps2pmx.jobs`` has one job per imported XPS file; objects point
back to their job with the ``xps2pmx_job`` custom property.  No module-level
globals hold state (hard constraint 3).

Mapping state: ``job.slots`` (one item per spec slot: which source bone fills
it and why) and ``job.bones`` (one item per source bone: map / merge / keep /
delete and why).  Merges are not stored on slots; they are the bones whose
action is ``merge`` with that ``slot_id`` -- one source of truth.
"""
from __future__ import annotations

import json
from typing import Dict, Optional

import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty, FloatProperty, IntProperty,
                       PointerProperty, StringProperty)
from bpy.types import PropertyGroup

from .core.result import StageResult

PROP_JOB = "xps2pmx_job"

LEVEL_ITEMS = (
    ('info', "信息", ""),
    ('warning', "警告", ""),
    ('error', "错误", ""),
)
ORIGIN_ITEMS = (
    ('NONE', "—", "未映射"),
    ('csv', "名称表", "按 bone_slots.csv 的别名列匹配"),
    ('spine', "脊柱规则", "按位置分配脊柱节"),
    ('topology', "拓扑", "按层级与位置识别"),
    ('diagnosis', "诊断", "下半身诊断的结果"),
    ('classifier', "分类", "辅助骨分类的默认处置"),
    ('user', "手动", "用户指定，自动识别不会覆盖"),
)
ACTION_ITEMS = (
    ('map', "映射", "这根骨成为某个槽位的主骨"),
    ('merge', "并入", "权重并入某个槽位的骨，然后删除这根骨"),
    ('keep', "保留", "保留为非标准骨（脸、头发、衣物、道具…）"),
    ('delete', "删除", "没有权重，删除（子骨改挂到上一级）"),
)
BONE_FILTER_ITEMS = (
    ('UNMAPPED', "未映射的", "除了槽位主骨以外的所有骨"),
    ('merge', "并入", ""),
    ('keep', "保留", ""),
    ('delete', "删除", ""),
    ('ALL', "全部", ""),
)

SCALE_ITEMS = (
    ('SHOULDER', "肩高归一", "让 腕 的高度在导出后 = 肩高目标（18 系列的做法，身高最一致）"),
    ('FIXED_125', "×12.5 原尺寸", "保持米制原尺寸，导出 ×12.5（你手工成品的习惯）"),
    ('FIXED_10', "×10", "整体 ×10（批量 *_new.pmx 的习惯）"),
)
APOSE_ITEMS = (
    ('S18', "37.5° 直臂（18 系列）", "上臂低于水平 37.5°，前臂与上臂共线"),
    ('ANIMASA', "あにまさ 29.72°+40.28°", "あにまさ式 ver.2.3 实测：上臂 29.72°，前臂 40.28°"),
    ('DEG45', "45° 直臂", "常见教程的 45°"),
    ('CUSTOM', "自定义", "使用下面的角度"),
)
APOSE_VALUES = {'S18': (37.5, 0.0), 'ANIMASA': (29.72, 10.56), 'DEG45': (45.0, 0.0)}


def _apose_preset_changed(self, context):
    values = APOSE_VALUES.get(self.apose_preset)
    if values is not None:
        self.apose_upper_deg, self.apose_fore_extra_deg = values


#: Stage ids in pipeline order; ``job.stage`` stores the last completed one.
TWIST_ITEMS = (
    ('STEPPED', "18 系列阶梯带", "腕捩1/2/3 各占一段，段间窄过渡（18 系列成品的分布）"),
    ('SMOOTH', "平滑", "按位置在 0/¼/½/¾/1 扭转级之间线性过渡（准标准骨插件的分布）"),
)
IK_ITEMS = (
    ('ANIMASA', "あにまさ标准", "足ＩＫ 40 次 / 2 rad，つま先ＩＫ 3 次 / 4 rad"),
    ('S18', "18 系列", "足ＩＫ 40 次 / 1 rad，つま先ＩＫ 80 次 / 1 rad（mmd_tools 默认值）"),
)

STAGES = ("import", "identify", "prepare", "build", "morphs", "physics", "check", "export")
STAGE_LABELS = {
    "import": "① 导入", "identify": "② 识别", "prepare": "③ 预处理", "build": "④ 生成MMD骨架",
    "morphs": "⑤ 表情", "physics": "⑥ 物理", "check": "⑦ 检查", "export": "⑧ 导出",
}


def _scene_state(item) -> Optional["XPS2PMX_SceneState"]:
    scene = item.id_data
    return getattr(scene, "xps2pmx", None)


def _slot_bone_changed(self, context):
    st = _scene_state(self)
    if st is None or st.programmatic:
        return
    # clearing is a decision too: the slot stays empty (generated / reported) until "清除手改"
    self.origin = 'user'
    self.reason = "用户指定" if self.bone else "用户清空（缺失时由补骨生成）"
    st.mapping_dirty = True


def _plan_changed(self, context):
    st = _scene_state(self)
    if st is None or st.programmatic:
        return
    self.origin = 'user'
    st.mapping_dirty = True


class XPS2PMX_ReportItem(PropertyGroup):
    level: EnumProperty(items=LEVEL_ITEMS, default='info')
    stage: StringProperty()
    code: StringProperty()
    text: StringProperty()
    target: StringProperty()
    slot_id: StringProperty()


class XPS2PMX_Slot(PropertyGroup):
    # ``name`` (built in) holds the slot_id so prop_search can list slots
    bone: StringProperty(name="源骨", update=_slot_bone_changed)
    origin: EnumProperty(items=ORIGIN_ITEMS, default='NONE')
    confidence: FloatProperty(min=0.0, max=1.0)
    reason: StringProperty()
    # copied from the spec table so the panel never has to load it
    name_j: StringProperty()
    group: StringProperty()
    row_type: StringProperty()
    side: StringProperty()
    mirror: StringProperty()
    required: BoolProperty()
    tier: IntProperty()


class XPS2PMX_BonePlan(PropertyGroup):
    # ``name`` (built in) holds the Blender bone name
    src: StringProperty(description="原始 XPS 骨名")
    action: EnumProperty(items=ACTION_ITEMS, default='keep', update=_plan_changed)
    slot_id: StringProperty(update=_plan_changed)
    category: StringProperty()
    reason: StringProperty()
    origin: EnumProperty(items=ORIGIN_ITEMS, default='classifier')
    weighted: BoolProperty()


class XPS2PMX_Job(PropertyGroup):
    job_id: StringProperty()
    model_name: StringProperty()
    source_path: StringProperty(subtype='FILE_PATH')
    collection: PointerProperty(type=bpy.types.Collection)
    armature: PointerProperty(type=bpy.types.Object)
    stage: StringProperty(default="", description="最后完成的阶段")
    summary_json: StringProperty(default="{}", description="各阶段的统计数据（JSON）")
    reports: CollectionProperty(type=XPS2PMX_ReportItem)
    # stage ② mapping state
    convention: StringProperty()
    slots: CollectionProperty(type=XPS2PMX_Slot)
    bones: CollectionProperty(type=XPS2PMX_BonePlan)
    checks: CollectionProperty(type=XPS2PMX_ReportItem)
    lower_body_json: StringProperty(default="{}")
    disagreements_json: StringProperty(default="[]")
    bones_index: IntProperty()
    checks_index: IntProperty()
    bones_filter: EnumProperty(items=BONE_FILTER_ITEMS, default='UNMAPPED')
    facing: StringProperty(default="-Y", description="-Y 正常；+Y 表示模型背朝前方，③ 会旋转 180°")
    # stage ③ options
    scale_mode: EnumProperty(name="缩放", items=SCALE_ITEMS, default='SHOULDER')
    shoulder_target: FloatProperty(name="肩高目标", default=17.0, min=10.0, max=30.0,
                                   description="导出后 腕 头的高度（PMX 单位）")
    apose_preset: EnumProperty(name="A 姿势", items=APOSE_ITEMS, default='S18', update=_apose_preset_changed)
    apose_upper_deg: FloatProperty(name="上臂角", default=37.5, min=0.0, max=80.0,
                                   description="腕→ひじ 低于水平的角度")
    apose_fore_extra_deg: FloatProperty(name="前臂附加", default=0.0, min=-30.0, max=40.0,
                                        description="前臂比上臂多下垂的角度（0 = 直臂）")
    level_shoulders: BoolProperty(name="摆平肩骨", default=True,
                                  description="把 肩 的头移到与 腕 同高同深（只改骨，不改网格）")
    # stage ④ options (design doc §8)
    gen_tier2: BoolProperty(name="准标准骨", default=True,
                            description="生成 上半身2（缺时）、肩P/肩C、腕捩/手捩、腰キャンセル、ダミー、親指０、操作中心")
    gen_tier3: BoolProperty(name="足D 系", default=True,
                            description="生成 足D/ひざD/足首D/足先EX，腿部权重全部移到 D 骨（変形階層 1）")
    twist_mode: EnumProperty(name="扭转权重", items=TWIST_ITEMS, default='STEPPED')
    ik_preset: EnumProperty(name="IK 参数", items=IK_ITEMS, default='ANIMASA')
    # stage ⑧
    export_path: StringProperty(name="导出路径", subtype='FILE_PATH', default="",
                                description="留空 = 偏好设置里的导出根目录/<模型名>/<模型名>.pmx")
    last_export: StringProperty(subtype='FILE_PATH', default="")

    def summary(self) -> dict:
        try:
            return json.loads(self.summary_json or "{}")
        except ValueError:
            return {}

    def set_summary(self, stage: str, data: dict) -> None:
        summary = self.summary()
        summary[stage] = data
        self.summary_json = json.dumps(summary, ensure_ascii=False)

    def record(self, result: StageResult, max_items: int = 200) -> None:
        """Replace this stage's report lines with ``result`` and remember its data."""
        for i in range(len(self.reports) - 1, -1, -1):
            if self.reports[i].stage == result.stage:
                self.reports.remove(i)
        for msg in result.messages[:max_items]:
            item = self.reports.add()
            item.level = msg.level
            item.stage = result.stage
            item.code = msg.code
            item.text = msg.text
            item.target = msg.target
        self.set_summary(result.stage, result.data)
        if result.ok:
            self.stage = result.stage

    def slot(self, slot_id: str) -> Optional[XPS2PMX_Slot]:
        return self.slots.get(slot_id)

    def slot_map(self) -> Dict[str, XPS2PMX_Slot]:
        return {s.name: s for s in self.slots}

    def lower_body(self) -> dict:
        try:
            return json.loads(self.lower_body_json or "{}")
        except ValueError:
            return {}


class XPS2PMX_SceneState(PropertyGroup):
    jobs: CollectionProperty(type=XPS2PMX_Job)
    active_job_index: IntProperty(default=-1)
    xps_path: StringProperty(name="XPS 文件", subtype='FILE_PATH',
                             description="要转换的 .xps / .mesh / .mesh.ascii 文件")
    programmatic: BoolProperty(default=False, options={'SKIP_SAVE'},
                               description="内部：程序写入时不把槽位标记为手动")
    mapping_dirty: BoolProperty(default=False, description="映射被手动修改过，需要重新检查")


CLASSES = (XPS2PMX_ReportItem, XPS2PMX_Slot, XPS2PMX_BonePlan, XPS2PMX_Job, XPS2PMX_SceneState)


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.xps2pmx = PointerProperty(type=XPS2PMX_SceneState)


def unregister() -> None:
    del bpy.types.Scene.xps2pmx
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


# ---------------------------------------------------------------------------
# job lookup (read-only helpers shared by ops and ui)

def state(context: bpy.types.Context) -> XPS2PMX_SceneState:
    return context.scene.xps2pmx


def job_by_id(context: bpy.types.Context, job_id: str) -> Optional[XPS2PMX_Job]:
    for job in state(context).jobs:
        if job.job_id == job_id:
            return job
    return None


def job_of_object(context: bpy.types.Context, obj: Optional[bpy.types.Object]) -> Optional[XPS2PMX_Job]:
    while obj is not None:
        job_id = obj.get(PROP_JOB)
        if job_id:
            return job_by_id(context, job_id)
        obj = obj.parent
    return None


def active_job(context: bpy.types.Context) -> Optional[XPS2PMX_Job]:
    """Job of the active object, falling back to the scene's active job index."""
    job = job_of_object(context, context.view_layer.objects.active)
    if job is not None:
        return job
    st = state(context)
    if 0 <= st.active_job_index < len(st.jobs):
        return st.jobs[st.active_job_index]
    return None


class programmatic_writes:
    """Context manager: writes inside do not mark slots as user-edited."""

    def __init__(self, context: bpy.types.Context):
        self.st = state(context)

    def __enter__(self):
        self.st.programmatic = True
        return self

    def __exit__(self, *exc):
        self.st.programmatic = False
        return False
