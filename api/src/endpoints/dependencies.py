from typing import Annotated

from core.pydantic.application import PersonasHandler
from fastapi import Depends
from sqlalchemy.orm import Session

from ..adapters.repos.sqlalchemy import (
    PersonasRepository,
    SqlAlchemyPersonasRepository,
)
from ..infrastructure.db.engine import get_db


def get_personas_handler(db: Session = Depends(get_db)) -> PersonasHandler:
    personas_repo: PersonasRepository = SqlAlchemyPersonasRepository(db)
    return PersonasHandler(personas_repo)


personas_dependency = Annotated[PersonasHandler, Depends(get_personas_handler)]
