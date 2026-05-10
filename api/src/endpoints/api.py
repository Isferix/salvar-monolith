from typing import Literal

from fastapi import APIRouter, Response
from pydantic import BaseModel

from .dependencies import serializer_dependency

api = APIRouter()


@api.get("/health")
async def health_check():
    return {"status": "ok"}


class ImportQuery(BaseModel):
    serializer: Literal["excel"] = "excel"
    # path: Path = Path("/storage/excel/data.xlsx")
    path: str = "./storage/data.xlsx"
    # file: UploadFile


class ExportQuery(BaseModel):
    serializer: Literal["excel"] = "excel"


@api.put("/serializer/import")
async def import_serializer(
    query: ImportQuery, serializer: serializer_dependency
) -> Response:
    serializer.import_data(str(query.path))
    return Response("ok", status_code=200)


@api.get("/serializer/export")
async def export_serializer(
    query: ExportQuery, serializer: serializer_dependency
) -> bytes:
    return b"ok"
