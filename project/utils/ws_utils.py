# built_in
import json
import logging
import asyncio
from typing import List, Set, Tuple, Dict
from starlette.websockets import WebSocketState
from websockets.exceptions import ConnectionClosedOK
from concurrent.futures._base import TimeoutError

# customized
from cfg import ws_cfg
from models import ws_models

# global variables
LOCK = asyncio.Lock()

# init
logger = logging.getLogger(__name__)


async def send_and_recv(device_id: str, send_data: str) -> str:
    '''
    send json str to ws_client,
    and receive json str from ws_client
    rm closed CONNECTIONS
    do not catch exception, just let it crash
    '''
    websocket = ws_cfg.CONNECTIONS[device_id]

    # send
    try:
        await websocket.send_text(send_data)
    except ConnectionClosedOK as e:
        print(f'WS: {device_id} CONNECTIONS closed: {e}')
        websocket.client_state = WebSocketState.DISCONNECTED
        ws_cfg.CONNECTIONS.pop(device_id)
        raise e

    # recv
    # TODO: add requestID(uuid) to make sure
    # TODO: json loads
    recv_data = await websocket.receive_text()
    return recv_data


async def send_and_recv_with_timeout(device_id: str, send_data: str, timeout: int) -> str:
    '''
    add timeout to async func: send_and_recv
    '''
    recv_data = await asyncio.wait_for(send_and_recv(device_id, send_data), timeout=timeout)
    return recv_data


async def create_task(
    task_id: str, level: int, address: Set[str],
    devices: Set[str], evals: Set[str] = set()
) -> Tuple[List[ws_models.DeviceExeResult]]:
    '''
    Used to create task
    this func do not check validation of params
    check params by yourself before call the func

    :param task_id: task uuid, littler than 512
    :param level: compliance level, enum: 2, 3
    :param address: set of system IP, the ip(IPV4/dotted-decimal) is string
    :param devices: set of device ID, the ID is string
    :param evals: set of evalute item, default is empty set that means all items

    Returns two list of DeviceExeResult: (successful, failed)

    Usage:
      successful, failed = await create_task(task_id, level, address, devices, evals)
    '''
    successful, failed = [], []

    # create ws message
    ws_msg = ws_models.WsMsg(
        obj=ws_models.WsObj.task,
        action=ws_models.WsAction.create,
        data=ws_models.TaskForCreate(
            task_id=task_id,
            level=level,
            address=list(address),
            evals=list(evals)
        ).dict()
    ).dict()
    ws_josn_str = json.dumps(ws_msg)

    # generate executable item list
    exe_items, exe_records = [], []
    # for device_id in devices:
    for device_id in ws_cfg.CONNECTIONS:
        # check CONNECTIONS of device is alive
        if device_id not in ws_cfg.CONNECTIONS:
            failed.append(ws_models.DeviceExeResult(
                device_id=device_id,
                message=ws_models.DeviceExeMsg.offline.value
            ))
        exe_records.append(device_id)
        exe_items.append(send_and_recv_with_timeout(
            device_id, ws_josn_str, timeout=ws_cfg.WS_TIMEOUT))

    # execute, send ws msg and recv result
    items = await asyncio.gather(*exe_items, return_exceptions=True)

    # handle error: timeout, ws CONNECTIONS closed, other
    for i, item in enumerate(items):
        device_exe_result = ws_models.DeviceExeResult(device_id=exe_records[i])
        if isinstance(item, ConnectionClosedOK):
            device_exe_result.message = ws_models.DeviceExeMsg.offline.value
        elif isinstance(item, TimeoutError):
            device_exe_result.message = ws_models.DeviceExeMsg.timeout.value
        elif isinstance(item, Exception):
            device_exe_result.message = ws_models.DeviceExeMsg.internal_error.value
        else:
            device_exe_result.successful = True
            device_exe_result.message = ws_models.DeviceExeMsg.success.value

        print(item)
        successful.append(device_exe_result)

    print(f'S:\n {successful}\nF:\n{failed}')
    print(ws_cfg.CONNECTIONS)
    return successful, failed


async def query_task(task_id: str, devices: Set[str]) -> Tuple[List[ws_models.DeviceQueryTaskResult]]:
    '''
    Used to query task
    this func do not check validation of params
    check params by yourself before call the func

    :param task_id: task uuid, littler than 512
    :param devices: set of device ID, the ID is string

    Returns two list of DeviceQueryTaskResult: (successful, failed)

    Usage:
      successful, failed = await query_task(task_id, devices)
    '''
    successful, failed = [], []

    # create ws message
    ws_msg = ws_models.WsMsg(
        obj=ws_models.WsObj.task,
        action=ws_models.WsAction.query,
        data=ws_models.TaskForQuery(task_id=task_id).dict()
    ).dict()
    ws_josn_str = json.dumps(ws_msg)

    # generate executable item list
    exe_items, exe_records = [], []
    # for device_id in devices:
    for device_id in ws_cfg.CONNECTIONS:
        # check CONNECTIONS of device is alive
        if device_id not in ws_cfg.CONNECTIONS:
            failed.append(ws_models.DeviceQueryTaskResult(
                device_id=device_id,
                message=ws_models.DeviceExeMsg.offline.value
            ))
        exe_records.append(device_id)
        exe_items.append(
            send_and_recv_with_timeout(
                device_id, ws_josn_str, timeout=ws_cfg.WS_TIMEOUT)
        )

    # execute, send ws msg and recv result
    items = await asyncio.gather(*exe_items, return_exceptions=True)

    '''
    done: <Task finished coro=<send_and_recv() done, defined at .\route.py:27> result='create success'>
    done: <Task finished coro=<send_and_recv() done, defined at .\route.py:27> exception=ConnectionClosedOK('code = 1000 (OK), no reason',)>
    pending: <Task pending coro=<send_and_recv() running at .\route.py:33> wait_for=<Future pending cb=[<TaskWakeupMethWrapper object at 0x0000000003DB9B88>()]>>
    '''
    # handle exe items
    for i, item in enumerate(items):
        device_query_task_result = ws_models.DeviceQueryTaskResult(
            device_id=exe_records[i])
        # ws CONNECTIONS closed
        if isinstance(item, ConnectionClosedOK):
            device_query_task_result.message = ws_models.DeviceExeMsg.offline.value
            failed.append(device_query_task_result)
            continue
        # timeout
        if isinstance(item, TimeoutError):
            device_query_task_result.message = ws_models.DeviceExeMsg.timeout.value
            failed.append(device_query_task_result)
            continue
        # other
        if isinstance(item, Exception):
            device_query_task_result.message = ws_models.DeviceExeMsg.internal_error.value
            failed.append(device_query_task_result)
            continue

        # device response error
        device_query_task_result.message = item.get('message')
        if not item.get('successful'):
            failed.append(device_query_task_result)
            continue

        # convert json into object
        data = item.get('data')
        json_results = data.get('results', [])
        obj_results = []
        for device_task_result in json_results:
            json_records = device_task_result.get('records')
            obj_records = []
            for record in json_records:
                json_items = record.get('items')
                obj_items = [ws_models.DeviceTaskItem(
                    **item) for item in json_items]
                record['items'] = obj_items
                obj_records.append(ws_models.DeviceTaskRecord(**record))
            device_task_result['records'] = obj_records
            obj_results.append(
                ws_models.DeviceTaskResult(**device_task_result))
        data['results'] = obj_results
        device_detect_result = ws_models.DeviceDetectResult(**data)

        device_query_task_result.successful = True
        device_query_task_result.detect_result = device_detect_result
        successful.append(device_query_task_result)

    print(f'S:\n {successful}\nF:\n{failed}')
    print(ws_cfg.CONNECTIONS)
    return successful, failed


async def delete_task(task_id: str, devices: Set[str]) -> Tuple[List[ws_models.DeviceExeResult]]:
    '''
    Used to dekete task
    this func do not check validation of params
    check params by yourself before call the func

    :param task_id: task uuid, littler than 512
    :param devices: set of device ID, the ID is string

    Returns two list of DeviceExeResult: (successful, failed)

    Usage:
      successful, failed = await delete_task(task_id, devices)
    '''
    successful, failed = [], []

    # create ws message
    ws_msg = ws_models.WsMsg(
        obj=ws_models.WsObj.task,
        action=ws_models.WsAction.delete,
        data=ws_models.TaskForDelete(task_id=task_id).dict()
    ).dict()
    ws_josn_str = json.dumps(ws_msg)

    # generate executable item list
    exe_items, exe_records = [], []
    # for device_id in devices:
    for device_id in ws_cfg.CONNECTIONS:
        # check CONNECTIONS of device is alive
        if device_id not in ws_cfg.CONNECTIONS:
            failed.append(ws_models.DeviceExeResult(
                device_id=device_id,
                message=ws_models.DeviceExeMsg.offline.value
            ))
        exe_records.append(device_id)
        exe_items.append(send_and_recv_with_timeout(
            device_id, ws_josn_str, timeout=ws_cfg.WS_TIMEOUT))

    # execute, send ws msg and recv result
    items = await asyncio.gather(*exe_items, return_exceptions=True)

    # handle error: timeout, ws CONNECTIONS closed, other
    for i, item in enumerate(items):
        device_exe_result = ws_models.DeviceExeResult(device_id=exe_records[i])
        if isinstance(item, ConnectionClosedOK):
            device_exe_result.message = ws_models.DeviceExeMsg.offline.value
        elif isinstance(item, TimeoutError):
            device_exe_result.message = ws_models.DeviceExeMsg.timeout.value
        elif isinstance(item, Exception):
            device_exe_result.message = ws_models.DeviceExeMsg.internal_error.value
        else:
            device_exe_result.successful = True
            device_exe_result.message = ws_models.DeviceExeMsg.success.value

        print(item)
        successful.append(device_exe_result)

    print(f'S:\n {successful}\nF:\n{failed}')
    print(ws_cfg.CONNECTIONS)
    return successful, failed
