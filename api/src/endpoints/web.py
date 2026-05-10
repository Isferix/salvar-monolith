from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..utils.responses import render, renderBase
from .dependencies import personas_dependency

web = APIRouter()


@web.get("/")
async def home(request: Request) -> HTMLResponse:
    return renderBase(request)


@web.get("/index")
async def index(request: Request) -> HTMLResponse:
    return render(request, template="index")


@web.get("/carga")
async def carga(request: Request, personas: personas_dependency) -> HTMLResponse:
    return render(
        request, template="pages/carga", data={"personas": personas.get_all_personas()}
    )


@web.get("/tabla")
async def tabla(request: Request) -> HTMLResponse:
    return render(request, template="pages/tabla")


@web.get("/informes")
async def informes(request: Request) -> HTMLResponse:
    return render(request, template="pages/informes")
