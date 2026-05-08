from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# from .endpoints.api import api
from .endpoints.web import web
server = FastAPI()
server.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="assets",
)

server.mount(
    "/components",
    StaticFiles(directory="web/components"),
    name="components",
)
# server.include_router(api, prefix="/api")
server.include_router(web)
