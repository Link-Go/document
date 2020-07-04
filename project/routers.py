import models
import requests
import json
import re
import asyncio

from datetime import datetime
from typing import List, Dict, Union, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from schemas import EvaluationCreate, GlobalReEvaluation, PartReEvaluation, UserOperation, CheckList, ItemUpdate
from models import EvaluationRecord, EvaluationItems, OperationRecord, DevicesTag, SystemInfor
from db import get_db, engine
from cfg import path
from utils import ws_utils

models.Base.metadata.create_all(engine)

router = APIRouter()


async def requests_list(url: str, token: str):
    """获取相应列表"""
    url = "{}/?token_auth={}".format(url, token)
    for _ in range(3):
        try:
            r = requests.get(url, timeout=path.timeout)
            break
        except Exception as e:
            pass
    else:
        raise HTTPException(status_code=408, detail="Request Time-out")

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code,
                            detail=r.json().get("message", None))
    return r.json()


async def user_operation(db: Session, operation: UserOperation):
    """用户操作"""
    new_operation = OperationRecord(**operation)
    db.add(new_operation)
    db.commit()


@router.get("/evaluation")
async def evaluation_records(db: Session = Depends(get_db)):
    '''获取评估记录'''
    # 是否存在数据
    record_num = db.query(EvaluationRecord).\
        filter(EvaluationRecord.is_delete == False).count()
    if record_num == 0:
        return None

    # 获取系统最近一次评估记录的ID，并获取记录
    last_system_record = db.query(func.max(EvaluationRecord.id).label(
        "id")).filter(EvaluationRecord.is_delete == False).\
        group_by(EvaluationRecord.name).subquery()

    system_record = db.query(EvaluationRecord.id,
                             EvaluationRecord.name,
                             EvaluationRecord.level,
                             EvaluationRecord.devices_address,
                             EvaluationRecord.non_compliance,
                             EvaluationRecord.create_time).\
        join(last_system_record, EvaluationRecord.id == last_system_record.c.id).\
        order_by(EvaluationRecord.id.desc()).all()

    items_record = db.query(EvaluationItems.id,
                            EvaluationItems.evaluation_id,
                            EvaluationItems.eval,
                            EvaluationItems.device_address,
                            EvaluationItems.kind).\
        join(last_system_record, EvaluationItems.evaluation_id == last_system_record.c.id).\
        group_by(EvaluationItems.evaluation_id,
                 EvaluationItems.eval).all()

    # 构建返回的数据格式
    results = {}
    for record in system_record:
        devices_address = re.sub('\'', "\"", record.devices_address)
        results[record.id] = {"name": record.name,
                              "level": record.level,
                              "devices_address": len(json.loads(devices_address)),
                              "non_compliance": record.non_compliance,
                              "last_evaluate_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                              "to_confirm": {
                                  "total": 0,
                                  # [数量, [测评项id], {测评项编号: 测评设备}]
                                  "configuration": [0, [], {}],
                                  "global": [0, [], {}],
                                  "artificial": [0, [], {}],
                              }
                              }

    for item in items_record:
        if item.kind is not None:
            if item.conformity != 1:
                results[item.evaluation_id]["to_confirm"]["total"] += 1
                results[item.evaluation_id]["to_confirm"][item.kind][0] += 1
            results[item.evaluation_id]["to_confirm"][item.kind][1].append(
                item.id)
            results[item.evaluation_id]["to_confirm"][item.kind][2][item.eval] = item.device_address
    return JSONResponse(results)


@router.get("/evaluation/systems/{name}")
async def system_evaluation_record(name: str,
                                   db: Session = Depends(get_db)):
    """获取单个系统的多条评估记录"""
    system_records = db.query(EvaluationRecord.id,
                              EvaluationRecord.create_time,
                              EvaluationRecord.level,
                              EvaluationRecord.devices_address).\
        filter(and_(EvaluationRecord.name == name,
                    EvaluationRecord.is_delete == False)).\
        order_by(EvaluationRecord.create_time.desc()).all()

    results = {}
    for record in system_records:
        devices_address = re.sub('\'', "\"", record.devices_address)
        results[record.id] = {
            "create_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.level,
            "devices_address": len(json.loads(devices_address))
        }
    return JSONResponse(results)


@router.get("/confirmation")
async def compliance_list(token_auth: str,
                          db: Session = Depends(get_db)):
    """获取业务系统与设备列表"""
    outer = await asyncio.gather(requests_list(path.list_systems, token_auth),
                                 requests_list(path.list_devices, token_auth))
    if not all(outer):
        raise HTTPException(status_code=400, detail="bad request")

    devices_id = [device["deviceid"] for device in outer[1]]
    devices_record = db.query(DevicesTag.device_id).\
        filter(DevicesTag.device_id.in_(devices_id)).all()
    devices_include = [
        device_record.device_id for device_record in devices_record]
    devices_exclude = list(set(devices_id) ^ set(devices_include))

    # 如果设备ID存在，则更新
    for device in outer[1]:
        if device["deviceid"] in devices_include:
            db.query(DevicesTag).\
                filter(DevicesTag.device_id == device["deviceid"]).\
                update({"name": device["name"],
                        "address": device["address"]})

    # 不存在则添加
    if len(devices_exclude) != 0:
        add_list = []
        for device in outer[1]:
            if device["deviceid"] in devices_exclude:
                add_list.append(DevicesTag(
                    device_id=device["deviceid"], name=device["name"], address=device["address"]))
        db.add_all(add_list)
    db.commit()

    last_devices = db.query(DevicesTag).\
        filter(DevicesTag.device_id.in_(devices_id)).all()

    devices = [{"deviceid": device.device_id,
                "name": device.name,
                "address": device.address,
                "tag": device.tag
                } for device in last_devices
               ]

    results = {
        "systems": outer[0],
        "devices": devices,
        "level": [2, 3]
    }
    return JSONResponse(results)


@router.post("/confirmation/devices")
async def devices_tag(devices: List[Dict[str, str]],
                      db: Session = Depends(get_db)):
    """设备标志记录"""
    for device in devices:
        db.query(DevicesTag).\
            filter(DevicesTag.device_id == device["deviceid"]).\
            update({"tag": device["tag"]})
    db.commit()


@router.post("/evaluation")
async def evaluation_create(new_evaluation: Union[
        EvaluationCreate, GlobalReEvaluation, PartReEvaluation],
        db: Session = Depends(get_db)):
    """创建评估任务"""
    if isinstance(new_evaluation, EvaluationCreate):
        new_evaluation = jsonable_encoder(new_evaluation)

        # 发布任务，successful，failed根据是否进行展示再使用
        task_uuid = str(uuid.uuid1())
        address = set(new_evaluation["systems"]["address"])
        devices = set([device["address"]
                       for device in new_evaluation["devices"]])
        successful, failed = await ws_utils.create_task(
            task_id=task_uuid + "_0",
            level=new_evaluation["level"],
            address=address,
            devices=devices
        )
        if len(failed) != 0:
            return JSONResponse({"result": False,
                                 "message": "创建任务失败",
                                 "detail": json.dumps(failed)})

        # 数据处理
        name = new_evaluation["systems"]["name"]
        level = new_evaluation["level"]
        devices_address = json.dumps(devices)
        address = json.dumps(address)

        # 创建任务记录
        record = EvaluationRecord(uuid=task_uuid,
                                  name=name,
                                  level=level,
                                  devices_address=devices_address,
                                  address=address)
        record.system_infor = [SystemInfor(is_net=new_evaluation["is_net"],
                                           is_sub_organ=new_evaluation["is_sub_organ"],
                                           is_spam=new_evaluation["is_spam"],
                                           is_gateway=new_evaluation["is_gateway"],
                                           is_vpn=new_evaluation["is_vpn"])]
        db.add(record)
        db.commit()
        last_record_id = db.query(EvaluationRecord.id).filter(
            EvaluationRecord.uuid == task_uuid).one()[0]
        return JSONResponse({"result": True,
                             "id": last_record_id,
                             "message": "任务创建成功"})
    elif isinstance(new_evaluation, GlobalReEvaluation):
        record = db.query(EvaluationRecord.id,
                          EvaluationRecord.uuid,
                          EvaluationRecord.count,
                          EvaluationRecord.level,
                          EvaluationRecord.address,
                          EvaluationRecord.devices_address).\
            filter(EvaluationRecord.id == new_evaluation.id).one()

        successful, failed = await ws_utils.create_task(
            task_id="{}_{}".format(record.uuid, record.count + 1),
            level=record.level,
            address=json.loads(record.address),
            devices=json.loads(record.devices_address)
        )

        if len(failed) != 0:
            return JSONResponse({"result": False,
                                 "message": "创建任务失败",
                                 "detail": json.dumps(failed)})

        return JSONResponse({"result": True,
                             "id": record.id,
                             "message": "任务创建成功"})
    elif isinstance(new_evaluation, PartReEvaluation):
        record = db.query(EvaluationRecord.id,
                          EvaluationRecord.uuid,
                          EvaluationRecord.count,
                          EvaluationRecord.level,
                          EvaluationRecord.address,
                          EvaluationRecord.devices_address).\
            filter(EvaluationRecord.id == new_evaluation.id).one()

        # 创建任务的接口待修改
        successful, failed = await ws_utils.create_task(
            task_id=record.uuid + "_" + str(record.count + 1),
            level=record.level,
            address=json.loads(record.address),
            devices=json.loads(record.devices_address)
        )

        if len(failed) != 0:
            return JSONResponse({"result": False,
                                 "message": "创建任务失败",
                                 "detail": json.dumps(failed)})

        return JSONResponse({"result": True,
                             "id": record.id,
                             "message": "任务创建成功"})


@router.delete("/evaluation/{evaluate_id}")
async def del_evaluation_record(evaluate_id: int,
                                db: Session = Depends(get_db)):
    """删除单条记录"""
    # 判断状态 [已完成，取消] 或 [等待，测评中]
    record = db.query(EvaluationRecord).get(evaluate_id)
    if not record:
        return {"result": False,
                "id": EvaluationRecord.id,
                "message": "该记录不存在"}

    if record.status in ["waiting", "evaluating"]:
        successful, failed = await ws_utils.delete_task(
            task_id="{}_{}".format(record.uuid, record.count + 1),
            devices=set(json.loads(record.devices_address))
        )
        if len(failed) != 0:
            return JSONResponse({"result": False,
                                 "message": "创建取消失败",
                                 "detail": json.dumps(failed)})

        await user_operation(db, UserOperation(
            operation_time=datetime.now(),
            evaluation_id=record.id,
            operation="update",
            operation_field="status",
            old_content=record.status,
            new_content="cancel"
        ))
        record.status = "cancel"
        db.commit()
        return {"result": True,
                "id": record.id,
                "message": "取消成功"}
    else:
        await user_operation(db, UserOperation(
            operation_time=datetime.now(),
            evaluation_id=record.id,
            operation="delete",
            operation_field="is_delete",
            old_content=record.is_delete,
            new_content="True"
        ))
        # 进行逻辑删除
        record.is_delete = True
        db.commit()
        return {"result": True,
                "id": record.id,
                "message": "删除成功"}


@router.get("/evaluation/{evaluate_id}")
async def evaluation_record(evaluate_id: int,
                            check_list: CheckList,
                            db: Session = Depends(get_db)):
    """获取核查确认列表"""
    if check_list is None:
        # 调用获取测评报告的接口
        pass

    items_record = db.query(EvaluationItems.id,
                            EvaluationItems.conformity,
                            EvaluationItems.compliance_ability,
                            EvaluationItems.advice,
                            EvaluationItems.is_check,
                            EvaluationItems.check_explain).filter(
        EvaluationItems.id.in_(check_list.id_list)).all()

    # TODO 获取每个测评项的安全要求

    result = []
    for item_record in items_record:
        result.append(
            {"item_id": item_record.id,
             "requirements": "",
             "guide": item_record.advice,
             "conformity": item_record.conformity if item_record.is_check else 0,
             "check_explain": item_record.check_explain}
        )
    return JSONResponse(result)


@router.put("/evaluation/{evaluate_id}/{item_id}")
async def update_item_record(evaluate_id: int, item_id: int,
                             item_update: ItemUpdate,
                             db: Session = Depends(get_db)):
    """更新记录"""
    # 查询设备是否存在
    item = db.query(EvaluationItems).get(item_id)
    if item is None:
        raise HTTPException(
            status_code=404, detail="{} not found".format(item_id))

    # 数据判断
    item_update = jsonable_encoder(item_update)
    check_explain = item_update["check_explain"].strip()
    if not check_explain:
        raise HTTPException(status_code=400, detail="请输入正确的说明")

    # 更新记录
    update_list = []
    update_list.append(OperationRecord(evaluation_id=item.evaluation_id,
                                       evaluation_items_id=item.id,
                                       operation="update",
                                       operation_field="conformity",
                                       old_content=item.conformity,
                                       new_content=item_update["conformity"]))
    item.conformity = item_update["conformity"]

    update_list.append(OperationRecord(evaluation_id=item.evaluation_id,
                                       evaluation_items_id=item.id,
                                       operation="update",
                                       operation_field="check_explain",
                                       old_content=item.check_explain,
                                       new_content=item_update["check_explain"]))
    item.check_explain = "用户手动确认：{}".format(item_update["check_explain"])

    if not item.is_check:
        item.is_check = True
        update_list.append(OperationRecord(evaluation_id=item.evaluation_id,
                                           evaluation_items_id=item.id,
                                           operation="update",
                                           operation_field="is_check",
                                           old_content=False,
                                           new_content=True))
    db.add_all(update_list)
    db.commit()

if __name__ == "__main__":
    import uuid
    from db import SessionLocal
    db = SessionLocal()
