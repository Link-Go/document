from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import HTTPException

app = FastAPI()

# @app.get("/")
# async def index():
#     return "Hello, World"


@app.get("/sangfor/auth")
async def auth(token_auth: str):
    if token_auth == "sangfor":
        return JSONResponse(status_code=200, content="认证成功")
    else:
        return JSONResponse(status_code=401, content="认证失败")


@app.get("/sangfor/systems")
async def systems(token_auth: str):
    if token_auth == "sangfor":
        return JSONResponse(status_code=200,
                            content=[{
                                "name":
                                "HRM系统",
                                "address": ["192.168.0.24", "192.168.0.23"]
                            }, {
                                "name":
                                "财务系统",
                                "address": ["192.168.0.24", "192.168.0.23"]
                            }])
    else:
        return JSONResponse(status_code=401, content={"message": "认证失败"})


@app.get("/sangfor/devices")
async def devices(token_auth: str):
    if token_auth == "sangfor":
        return JSONResponse(status_code=200,
                            content=[{
                                "name": "AF",
                                "address": "200.100.0.1",
                                "deviceid": "456",
                                "tag": ""
                            }, {
                                "name": "AC",
                                "address": "200.100.0.2",
                                "deviceid": "poi",
                                "tag": ""
                            }])
    else:
        return JSONResponse(status_code=401, content={"message": "认证失败"})


@app.get("/")
async def index():
    return JSONResponse(status_code=404, content={"messgae": "这是404错误"})


@app.get("/except")
async def exceptTest():
    try:
        1 / 0
    except ZeroDivisionError:
        raise HTTPException(status_code=404, detail="这也是一个错误")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", port=8080, reload=True)
