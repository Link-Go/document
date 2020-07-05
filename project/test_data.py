import uuid
import models
import json
import re

from sqlalchemy import and_, func

from models import EvaluationRecord, EvaluationItems, OperationRecord, DevicesTag, SystemInfor
from db import SessionLocal, engine

models.Base.metadata.create_all(engine)
db = SessionLocal()

record_1 = models.EvaluationRecord(
    uuid=str(uuid.uuid1()),
    count=0,
    name="HRM系统",
    level=2,
    devices_address="['200.0.0.1', '200.0.0.2', '200.0.0.3']",
    address="['192.168.0.1', '192.168.0.2']",
    status="finished",
    non_compliance=3,
    high_risk=1,
    is_delete=False)

record_1.evaluation_items = [
    models.EvaluationItems(eval="A0001",
                           device="AF",
                           device_address="200.0.0.1",
                           device_id="abcd",
                           conformity=3,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="configuration"),
    models.EvaluationItems(eval="A0002",
                           device="AC",
                           device_address="200.0.0.2",
                           device_id="ABCD",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="global"),
    models.EvaluationItems(eval="A0003",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="artificial"),
    models.EvaluationItems(eval="A0004",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=1,
                           compliance_ability="xxx满足"),
]

record_2 = models.EvaluationRecord(
    uuid=str(uuid.uuid1()),
    count=0,
    name="HRM系统",
    level=3,
    devices_address="['200.0.0.1', '200.0.0.2', '200.0.0.3']",
    address="['192.168.0.1', '192.168.0.2']",
    status="finished",
    non_compliance=3,
    high_risk=1,
    is_delete=False)

record_2.evaluation_items = [
    models.EvaluationItems(eval="A0001",
                           device="AF",
                           device_address="200.0.0.1",
                           device_id="abcd",
                           conformity=3,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="configuration"),
    models.EvaluationItems(eval="A0002",
                           device="AC",
                           device_address="200.0.0.2",
                           device_id="ABCD",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="global"),
    models.EvaluationItems(eval="A0003",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="artificial"),
    models.EvaluationItems(eval="A0004",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=1,
                           compliance_ability="xxx满足"),
]

record_3 = models.EvaluationRecord(
    uuid=str(uuid.uuid1()),
    count=0,
    name="财务系统",
    level=2,
    devices_address="['200.0.0.1', '200.0.0.2', '200.0.0.3']",
    address="['192.168.0.1', '192.168.0.2']",
    status="finished",
    non_compliance=3,
    high_risk=1,
    is_delete=False)

record_3.evaluation_items = [
    models.EvaluationItems(eval="A0001",
                           device="AF",
                           device_address="200.0.0.1",
                           device_id="abcd",
                           conformity=3,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="configuration"),
    models.EvaluationItems(eval="A0002",
                           device="AC",
                           device_address="200.0.0.2",
                           device_id="ABCD",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="global"),
    models.EvaluationItems(eval="A0003",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="artificial"),
    models.EvaluationItems(eval="A0004",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=1,
                           compliance_ability="xxx满足"),
]

record_4 = models.EvaluationRecord(
    uuid=str(uuid.uuid1()),
    count=0,
    name="财务系统",
    level=2,
    devices_address="['200.0.0.1', '200.0.0.2', '200.0.0.3']",
    address="['192.168.0.1', '192.168.0.2']",
    status="cancel",
    non_compliance=3,
    high_risk=1,
    is_delete=False)

record_4.evaluation_items = [
    models.EvaluationItems(eval="A0001",
                           device="AF",
                           device_address="200.0.0.1",
                           device_id="abcd",
                           conformity=3,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="configuration"),
    models.EvaluationItems(eval="A0002",
                           device="AC",
                           device_address="200.0.0.2",
                           device_id="ABCD",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="global"),
    models.EvaluationItems(eval="A0003",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="artificial"),
    models.EvaluationItems(eval="A0004",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=1,
                           compliance_ability="xxx满足"),
]

record_5 = models.EvaluationRecord(
    uuid=str(uuid.uuid1()),
    count=0,
    name="销售系统",
    level=2,
    devices_address="['200.0.0.1', '200.0.0.2', '200.0.0.3']",
    address="['192.168.0.1', '192.168.0.2']",
    status="evaluating",
    non_compliance=3,
    high_risk=1,
    is_delete=False)

record_5.evaluation_items = [
    models.EvaluationItems(eval="A0001",
                           device="AF",
                           device_address="200.0.0.1",
                           device_id="abcd",
                           conformity=3,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="configuration"),
    models.EvaluationItems(eval="A0002",
                           device="AC",
                           device_address="200.0.0.2",
                           device_id="ABCD",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="global"),
    models.EvaluationItems(eval="A0003",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="artificial"),
    models.EvaluationItems(eval="A0004",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=1,
                           compliance_ability="xxx满足"),
]

record_6 = models.EvaluationRecord(
    uuid=str(uuid.uuid1()),
    count=0,
    name="销售系统",
    level=2,
    devices_address="['200.0.0.1', '200.0.0.2', '200.0.0.3']",
    address="['192.168.0.1', '192.168.0.2']",
    status="finished",
    non_compliance=3,
    high_risk=1,
    is_delete=False)

record_6.evaluation_items = [
    models.EvaluationItems(eval="A0001",
                           device="AF",
                           device_address="200.0.0.1",
                           device_id="abcd",
                           conformity=3,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="configuration"),
    models.EvaluationItems(eval="A0002",
                           device="AC",
                           device_address="200.0.0.2",
                           device_id="ABCD",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="global"),
    models.EvaluationItems(eval="A0003",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=0,
                           compliance_ability="xxx满足",
                           advice="需要xxx",
                           kind="artificial"),
    models.EvaluationItems(eval="A0004",
                           device="AD",
                           device_address="200.0.0.3",
                           device_id="efg",
                           conformity=1,
                           compliance_ability="xxx满足"),
]

# db.add_all([record_1, record_2, record_3, record_4, record_5, record_6])
# db.commit()

if __name__ == "__main__":
    # devices_record = db.query(DevicesTag.device_id, DevicesTag.name,
    #                           DevicesTag.tag, DevicesTag.address).all()
    devices_record = db.query(
        DevicesTag.tag).filter(DevicesTag.device_id == "123").one()
    print(devices_record)