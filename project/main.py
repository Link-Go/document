import requests
import re

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from routers import router
from cfg import path

app = FastAPI()
app.include_router(router, prefix="/compliance")

# @app.middleware("http")
# async def web_auth(request: Request, call_next):
#     token_auth = request.query_params.get("token_auth", None)
#     if not token_auth:
#         return RedirectResponse(path.client_logging)

#     res = re.match(r"[0-9a-zA-Z_]{32}", token_auth)  # token length
#     if not res:
#         return RedirectResponse(path.client_logging)

#     url = "{}/?token_auth={}".format(path.web_auth_api, token_auth)
#     try:
#         resp = requests.get(url, timeout=path.TIMEOUT)
#     except Exception as e:
#         return RedirectResponse(path.client_logging)

#     if resp.status_code != 200:
#         return RedirectResponse(path.client_logging)

#     response = await call_next(request)
#     return response

# @app.middleware("http")
# async def test_web_auth(request: Request, call_next):
#     """for test"""
#     token_auth = request.query_params.get("token_auth", None)
#     if not token_auth:
#         return RedirectResponse(path.test_client_logging)

#     res = re.match(r"[0-9a-zA-Z_]{3}", token_auth)  # token length
#     if not res:
#         return RedirectResponse(path.test_client_logging)

#     url = "{}/?token_auth={}".format(path.test_web_auth_api, token_auth)
#     try:
#         resp = requests.get(url, timeout=path.TIMEOUT)
#     except Exception as e:
#         return RedirectResponse(path.test_client_logging)

#     if resp.status_code != 200:
#         print(resp.status_code, resp.json())
#         return RedirectResponse(path.test_client_logging)

#     response = await call_next(request)
#     return response


@app.get("/")
async def index():
    return "欢迎进入等保中心端"
