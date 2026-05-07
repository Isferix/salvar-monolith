from fastapi import FastAPI
from inertia import (
    InertiaVersionConflictException,
    inertia_version_conflict_exception_handler,
)

from .endpoints.api import api

server = FastAPI()
server.add_exception_handler(
    InertiaVersionConflictException, inertia_version_conflict_exception_handler
)

server.include_router(api)
