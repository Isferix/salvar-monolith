from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..utils.responses import renderBase, renderTemplate
from .dependencies import personas_dependency

web = APIRouter(
    tags=["web", "personas"],
)


@web.get("/")
async def home(request: Request) -> HTMLResponse:
    return renderBase(request)


@web.get("/index")
async def index(request: Request) -> HTMLResponse:
    return renderTemplate(request, data={}, template="src/index")


@web.get("/carga")
async def carga(request: Request) -> HTMLResponse:
    return renderTemplate(request, template="src/pages/carga")


@web.get("/tabla")
async def tabla(request: Request, personas: personas_dependency) -> HTMLResponse:
    data_personas = personas.get_all_personas()
    payload = {"personas": data_personas}
    return renderTemplate(
        request,
        template="src/pages/tabla",
        data=payload,
    )


@web.get("/tabla/partial")
async def tabla_partial(
    request: Request, personas: personas_dependency
) -> HTMLResponse:
    data_personas = personas.get_all_personas()
    payload = {"personas": data_personas}
    return renderTemplate(request, template="components/tablaPersonas", data=payload)


@web.get("/informes")
async def informes(request: Request) -> HTMLResponse:
    return renderTemplate(request, template="src/pages/informes")
