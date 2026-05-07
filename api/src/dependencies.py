from typing import Annotated

from fastapi import Depends
from inertia import Inertia

from .infrastructure.inertia import inertia_dependency
from .infrastructure.logger import setup_logger

logger = setup_logger("server")

InertiaDependency = Annotated[Inertia, Depends(inertia_dependency)]
