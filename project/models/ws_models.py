from enum import Enum
from typing import List
import json
from pydantic import BaseModel, Field


class WsObj(str, Enum):
    task = 'task'
    setting = 'setting'


class WsAction(str, Enum):
    create = 'create'
    query = 'query'
    delete = 'delete'


class WsMsg(BaseModel):
    obj: WsObj
    action: WsAction
    data: dict


class TaskForCreate(BaseModel):
    task_id: str
    level: int
    address: List[str]
    evals: List[str] = []


class TaskForQuery(BaseModel):
    task_id: str


class TaskForDelete(BaseModel):
    task_id: str


class DeviceExeMsg(str, Enum):
    offline = 'offline'
    timeout = 'timeout'
    internal_error = 'internal error'
    success = 'success'


class DeviceExeResult(BaseModel):
    device_id: str
    successful: bool = False
    message: str = ''


class DeviceTaskItem(BaseModel):
    id: str
    result: int
    message: str
    suggest: str


class DeviceTaskRecord(BaseModel):
    id: str
    result: int
    items: List[DeviceTaskItem] = []


class DeviceTaskResult(BaseModel):
    name: str
    total_num: int
    processed_num: int = 0
    message: str
    records: List[DeviceTaskRecord] = []


class DeviceDetectResult(BaseModel):
    status: str
    results: List[DeviceTaskResult] = []


class DeviceQueryTaskResult(DeviceExeResult):
    """设备查询任务的结果"""
    detect_result: DeviceDetectResult = None


class ComplianceResult(int, Enum):
    compliance = 0
    noncompliance = 1


class DetectionItem(BaseModel):
    detection_point: str = Field(..., title='检测点')
    compliance_result: ComplianceResult = Field(..., title='合规结果')
    cfg_file: str = Field('', title='配置文件')
    desc: str = Field('', title='检测详情')


class DetctionStatus(str, Enum):
    waiting = 'waiting'
    detecting = 'detecting'
    done = 'done'
    failed = 'failed'


class DeviceDetctionResult(BaseModel):
    device_id: str = Field(..., title='设备 ID')
    status: DetctionStatus = Field(..., title='检测状态')
    detection_items: List[DetectionItem] = Field(..., title='检测项目列表')


class DeleteSuccessMsg(str, Enum):
    success = 'success'


class DeleteSuccessRespModel(BaseModel):
    message: DeleteSuccessMsg


class Common401Msg(str, Enum):
    unauthorized = 'unauthorized'


class Common401RespModel(BaseModel):
    message: Common401Msg


class Common404Msg(str, Enum):
    not_exist = 'object not exists'


class Common404RespModel(BaseModel):
    message: Common404Msg


class CreateTask422Msg(str, Enum):
    invalid_system = 'invalid system address'
    invalid_device = 'invalid device ID or device offline'
    duplicate_task = 'duplicate task'
    task_exist = 'task exist'
    unreachable_system = 'unreachable system'


class CreateTask422RespModel(BaseModel):
    message: CreateTask422Msg


class QueryTask422Msg(str, Enum):
    invalid_device = 'invalid device ID or device offline'


class QueryTask422RespModel(BaseModel):
    message: QueryTask422Msg


class DeleteTask422Msg(str, Enum):
    invalid_device = 'invalid device ID or device offline'


class DeleteTask422RespModel(BaseModel):
    message: DeleteTask422Msg


def get_additional_resp(
    resp404: BaseModel = None, resp422: BaseModel = None
):
    '''
    get additional responses for declaration
    additional responses will be included in the OpenAPI schema
    they will also appear in the API docs
    codes include: 404, 422
    '''
    additional_resp = {
        404: {"model": resp404, "description": "Object not exists"},
        422: {"model": resp422, "description": "Validation Error"}
    }
    return {k: v for k, v in additional_resp.items() if v['model']}


# test = WsMsg(
#         obj=WsObj.task,
#         action=WsAction.create,
#         data = TaskForCreate(
#             task_id = 'dfdsfa',
#             level = 2,
#             address = [],
#             evals = [],
#         ).dict()
#     )
# print(test.dict())
# print(json.dumps(test.dict()))
# r = [Dev
