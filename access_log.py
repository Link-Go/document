import typing

import uvicorn
from starlette.routing import Match
from starlette.types import Scope
from fastapi import FastAPI
from fastapi.routing import APIRoute, APIRouter


class NewRoute(APIRoute):
    def matches(self, scope: Scope) -> typing.Tuple[Match, Scope]:
        if scope["type"] == "http":
            match = self.path_regex.match(scope["path"])
            if match:
                # print(self.path_regex, self.path_format)
                # TODO 增加日志传输功能
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(
                        value)
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {
                    "endpoint": self.endpoint,
                    "path_params": path_params
                }
                if self.methods and scope["method"] not in self.methods:
                    return Match.PARTIAL, child_scope
                else:
                    return Match.FULL, child_scope
        return Match.NONE, {}

    def scope_headers(self, scope: Scope) -> dict:
        if not scope.get("headers"):
            return {}

        return {key.decode(): value.decode() for key, value in dict(scope["headers"]).items()}

    def scope_cookie(self, scope: Scope) -> dict:
        headers = self.scope_headers(scope)
        cookie_dict = {}
        for chunk in headers.get("cookie", "").split(";"):
            if "=" in chunk:
                key, val = chunk.split("=", 1)
            else:
                # Assume an empty name per
                key, val = "", chunk
            key, val = key.strip(), val.strip()
            if key or val:
                cookie_dict[key] = val
        return cookie_dict

    

r = APIRouter(route_class=NewRoute)


@r.get("/hello/{a}/{b}")
async def root(a: int, b: str):
    return {"message": "Hello World"}


@r.get("/abc")
async def abc():
    pass


app = FastAPI()
app.include_router(r)

if __name__ == "__main__":
    uvicorn.run("demo:app", reload=True)
