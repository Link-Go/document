import models

from pydantic import ValidationError
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_evaluation_record():
    response = client.get("/compliance/evaluation")
    assert response.status_code == 200
    results = response.json()
    for res_id, res_info in results.items():
        try:
            models.Evaluation(**res_info)
        except ValidationError:
            raise ValidationError


def test_system_evaluation_record():
    response = client.get("/compliance/evaluation/systems/ABC")
    assert response.status_code == 200
    assert response.json() == {}

    response = client.get("/compliance/evaluation/systems/*@II")
    assert response.status_code == 400

    response = client.get("/compliance/evaluation/systems/HRM..//")
    assert response.status_code == 400

    response = client.get("/compliance/evaluation/systems/HRM系统")
    assert response.status_code == 200
    for res_id, res_info in response.json().items():
        try:
            models.SystemEvaluation(**res_info)
        except ValidationError:
            raise ValidationError


# def test_compliance_list():
#     response = client.get("/compliance/confirmation")
#     assert response.status_code == 422

#     response = client.get("/compliance/confirmation/?token_auth=123")
#     assert response.status_code == 401

#     response = client.get("/compliance/confirmation/?token_auth=sangfor")
#     assert response.status_code == 200
#     try:
#         models.SysDevList(**response.json())
#     except ValidationError:
#         raise ValidationError


def test_devices_tag():
    data = [{
        "deviceid": "123",
        "tag": "互联网"
    }, {
        "deviceid": "asd",
        "tag": "防火墙"
    }]
    response = client.put("/compliance/confirmation/devices", json=data)
    assert response.status_code == 200
    assert response.json() == [{
        "deviceid": "123",
        "result": True,
        "message": ""
    }, {
        "deviceid": "asd",
        "result": True,
        "message": ""
    }]

    data_1 = [{
        "deviceid": "123~",
        "tag": "互联网"
    }, {
        "deviceid": "asd",
        "tag": "防火墙"
    }]

    response = client.put("/compliance/confirmation/devices", json=data_1)
    assert response.status_code == 400

    data_2 = [{
        "deviceid": "1234",
        "tag": "互联网"
    }, {
        "deviceid": "asd",
        "tag": "防火墙"
    }]

    response = client.put("/compliance/confirmation/devices", json=data_2)
    assert response.status_code == 200
    assert response.json() == [{
        "deviceid": "1234",
        "result": False,
        "message": "请确认标志的信息是否正确"
    }, {
        "deviceid": "asd",
        "result": True,
        "message": ""
    }]


if __name__ == "__main__":
    test_system_evaluation_record()
