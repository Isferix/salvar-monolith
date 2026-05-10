from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..utils.responses import renderBase, renderTemplate
from .dependencies import personas_dependency

web = APIRouter()


@web.get("/")
async def home(request: Request) -> HTMLResponse:
    return renderBase(request)


@web.get("/index")
async def index(request: Request) -> HTMLResponse:
    return renderTemplate(request, data={}, template="index")


@web.get("/carga")
async def carga(request: Request) -> HTMLResponse:
    return renderTemplate(request, template="pages/carga")


@web.get("/tabla")
async def tabla(request: Request, personas: personas_dependency) -> HTMLResponse:
    data_personas = personas.get_all_personas()
    payload = {"personas": data_personas}
    return renderTemplate(
        request,
        template="pages/tabla",
        data=payload,
    )


@web.get("/informes")
async def informes(request: Request) -> HTMLResponse:
    return renderTemplate(request, template="pages/informes")
