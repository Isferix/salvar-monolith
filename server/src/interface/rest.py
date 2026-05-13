from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel

from core.pydantic.models import Persona

from .dependencies import personas_dependency, serializer_dependency

rest = APIRouter(tags=["rest", "personas"])


class ImportQuery(BaseModel):
    serializer: Literal["excel"] = "excel"
    # path: Path = Path("/storage/excel/data.xlsx")
    path: str = "./storage/data.xlsx"
    # file: UploadFile


class ExportQuery(BaseModel):
    serializer: Literal["excel"] = "excel"


@rest.get("/personas")
async def get_personas(personas: personas_dependency) -> list[Persona]:
    return personas.get_all_personas()


@rest.put("/serializer/import")
async def import_serializer(
    query: ImportQuery, serializer: serializer_dependency
) -> Response:
    serializer.import_data(str(query.path))
    return Response("ok", status_code=200)


@rest.get("/serializer/export")
async def export_serializer(
    query: ExportQuery, serializer: serializer_dependency
) -> bytes:
    return b"ok"
