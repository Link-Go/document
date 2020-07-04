import requests
from cfg import path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from routers import router


app = FastAPI()
app.include_router(router, prefix="/compliance")


# @app.middleware("http")
# async def web_auth(request: Request, call_next):
#     token_auth = request.query_params.get("token_auth", None)
#     if not token_auth:
#         return RedirectResponse(path.client_logging)

#     url = "{}/?token_auth={}".format(path.web_auth_api, token_auth)
#     try:
#         resp = requests.get(url, timeout=path.timeout)
#     except Exception as e:
#         return RedirectResponse(path.client_logging)

#     if resp.status_code != 200:
#         return RedirectResponse(path.client_logging)

#     response = await call_next(request)
#     return response
