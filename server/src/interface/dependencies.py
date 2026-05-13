from pathlib import Path
from typing import Annotated

from core.pydantic.application import (
    PersonasHandler,
    PersonasSerializer,
    SerializerHandler,
)
from fastapi import Depends
from sqlalchemy.orm import Session

from ..adapters.excel import ExcelSerializer
from ..adapters.repos.sqlalchemy import (
    PersonasRepository,
    SqlAlchemyPersonasRepository,
)
from ..infrastructure.db.engine import get_db


def get_personas_handler(db: Session = Depends(get_db)) -> PersonasHandler:
    personas_repo: PersonasRepository = SqlAlchemyPersonasRepository(db)
    return PersonasHandler(personas_repo)


def get_serializer_handler(db: Session = Depends(get_db)) -> SerializerHandler:
    personas_serializer: PersonasSerializer = ExcelSerializer(Path("/storage/excel/"))
    personas_repo: PersonasRepository = SqlAlchemyPersonasRepository(db)
    return SerializerHandler(personas_serializer, personas_repo)


personas_dependency = Annotated[PersonasHandler, Depends(get_personas_handler)]
serializer_dependency = Annotated[SerializerHandler, Depends(get_serializer_handler)]
