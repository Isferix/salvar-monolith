from fastapi import FastAPI

from .rest import rest
from .web import web

api = FastAPI()


@api.get("/health")
async def health_check():
    return {"status": "ok"}


api.include_router(rest, prefix="/rest")
api.include_router(web)
