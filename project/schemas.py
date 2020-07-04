from typing import List, Dict, Union, Optional
from enum import Enum

from datetime import datetime
from pydantic import BaseModel


class SafetyLevel(int, Enum):
    second_level = 2
    third_level = 3


class Item(BaseModel):
    """评估项"""
    class SecurityCategory(str, Enum):
        secure_communication_network = "secure_communication_network"
        secure_area_boundary = "secure_area_boundary"
        secure_computing_environment = "secure_computing_environment"
        secure_management_center = "secure_management_center"

    class TestStatus(str, Enum):
        to_evaluate = "to_evaluate"
        evaluating = "evaluating"
        evaluated = "evaluated"
        cancel = "cancel"

    class Conformity(int, Enum):
        high_risk = 0
        inconformity = 1
        partial = 2
        conform = 3

    id: int
    evaluation_id: int
    items_num: str
    count: int
    control_point: str
    security_category: SecurityCategory
    equipment: str
    devide_id: str
    test_requirements: str
    test_status: TestStatus
    conformity: Conformity
    compliance_ability: str
    advice: str
    operation: bool = False
    operation_explain: str = None
    setting_explain: str = None

    class Config:
        orm_mode = True


class Evaluation(BaseModel):
    """评估记录"""
    class EvaluationStatus(str, Enum):
        evaluating = "evaluating"
        evaluated = "evaluated"
        cancel = "cancel"

    id: int
    evaluation_time: datetime
    system_name: str
    system_address: str
    safety_level: SafetyLevel
    equipments: str
    evaluation_level: str
    evaluation_status: EvaluationStatus
    is_delete: bool = False
    is_net: bool = False
    is_sub_organ: bool = False
    is_spam: bool = False
    is_gateway: bool = False
    is_vpn: bool = False
    configure_adress: str
    offline_verification: str
    manual_verification: str
    report_adress: str
    evaluation_items: List[Item] = []

    class Config:
        orm_mode = True


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


class Status(str, Enum):
    """状态"""
    inconformity = "不符合"
    conformity = "符合"


class ItemUpdate(BaseModel):
    """测试项记录更新"""
    conformity: Status  # 符合状态
    check_explain: str  # 核查确认说明
