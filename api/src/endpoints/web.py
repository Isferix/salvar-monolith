from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..utils.responses import render, renderBase

web = APIRouter()


@web.get("/")
async def home(request: Request) -> HTMLResponse:
    return renderBase(request)


@web.get("/index")
async def index(request: Request) -> HTMLResponse:
    return render(request, template="index")
