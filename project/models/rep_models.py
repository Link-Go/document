from typing import List, Dict, Union, Optional
from enum import Enum

from datetime import datetime
from pydantic import BaseModel


class SafetyLevel(int, Enum):
    """安全级别"""
    second_level = 2
    third_level = 3


class Status(int, Enum):
    """测试项状态"""
    unconfirm = 0
    conformity = 1
    partial_match = 2
    inconformity = 3


class DevMark(BaseModel):
    """响应信息"""
    deviceid: str
    result: bool
    message: Optional[str]


class ToConfirmItemInfor(BaseModel):
    """待处理事项信息"""
    # [数量, [测评项id], {测评项编号: 测评设备}]
    num: int
    items_id: List[int]
    item2dev: Dict[str, str]


class Evaluation(BaseModel):
    """评估记录"""
    class EvaluationStatus(str, Enum):
        waiting = "waiting"
        evaluating = "evaluating"
        finished = "finished"
        cancel = "cancel"
        failure = "failure"

    name: str
    level: SafetyLevel
    devices_num: int
    non_compliance: int
    last_evaluate_time: str
    total: int
    to_confirm: Optional[Dict[str, ToConfirmItemInfor]]

    class Config:
        orm_mode = True


class SystemEvaluation(BaseModel):
    """某个系统的评估记录"""
    create_time: str
    level: SafetyLevel
    devices_num: int


class SystemList(BaseModel):
    """系统列表"""
    name: str
    address: List[str]


class DevciveList(BaseModel):
    """设备列表"""
    deviceid: str
    name: str
    address: str
    tag: Optional[str]


class SysDevList(BaseModel):
    """评估系统,设备列表"""
    systems: List[SystemList]
    devices: List[DevciveList]
    level: List[int]


class UpdateDevTag(BaseModel):
    """更新设备标志"""
    deviceid: str
    tag: str


class EvaluationCreate(BaseModel):
    """创建评估任务"""
    systems: Dict[str, Union[str, List[str]]]
    devices: List[Dict[str, str]]
    level: SafetyLevel
    is_net: bool
    is_sub_organ: bool
    is_spam: bool
    is_gateway: bool
    is_vpn: bool

    class Config:
        orm_mode = True


class GlobalReEvaluation(BaseModel):
    """全局重新开始评估"""
    id: int


class PartReEvaluation(GlobalReEvaluation):
    """局部重新评估"""
    configuration: Dict[str, str]


class UserOperation(BaseModel):
    """用户操作"""
    class Operation(str, Enum):
        create = "create"
        update = "update"
        delete = "delete"

    operation_time: datetime
    evaluation_id: int
    evaluation_items_id: Optional[int]
    operation: Operation
    operation_field: str
    old_content: str
    new_content: str


class CheckList(BaseModel):
    """核查确认列表"""
    id_list: List[int]


class ItemUpdate(BaseModel):
    """测试项记录更新"""
    conformity: Status  # 符合状态
    check_explain: str  # 核查确认说明
