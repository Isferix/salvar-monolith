from typing import Annotated

from core.pydantic.application import PersonasHandler
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..adapters.repos.sqlalchemy import (
    PersonasRepository,
    SqlAlchemyPersonasRepository,
)
from ..infrastructure.db.engine import get_db
from ..utils.responses import render, renderBase


def get_personas_handler(db: Session = Depends(get_db)) -> PersonasHandler:
    personas_repo: PersonasRepository = SqlAlchemyPersonasRepository(db)
    return PersonasHandler(personas_repo)


personas_dependency = Annotated[PersonasHandler, Depends(get_personas_handler)]

web = APIRouter()


@web.get("/")
async def home(request: Request) -> HTMLResponse:
    return renderBase(request)


@web.get("/index")
async def index(request: Request) -> HTMLResponse:
    return render(request, template="index")


@web.get("/carga")
async def carga(request: Request) -> HTMLResponse:
    return render(request, template="pages/carga")


@web.get("/tabla")
async def tabla(request: Request) -> HTMLResponse:
    return render(request, template="pages/tabla")


@web.get("/informes")
async def informes(request: Request) -> HTMLResponse:
    return render(request, template="pages/informes")
