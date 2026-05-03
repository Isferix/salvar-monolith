from fastapi import FastAPI

from .endpoints.api import api

server = FastAPI()

server.include_router(api)
