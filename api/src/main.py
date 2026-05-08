from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .endpoints.api import api
from .endpoints.web import web
from .infrastructure.jinja import templates
from .settings import get_settings
from .utils import reload_templates

settings = get_settings()
is_dev = settings.env == "development"

if is_dev:
    import arel
    from fastapi.concurrency import asynccontextmanager

    hot_reload = arel.HotReload(
        paths=[arel.Path("./web/src", on_reload=[reload_templates])]
    )
    templates.env.auto_reload = True
    templates.env.globals["hot_reload"] = hot_reload

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await hot_reload.startup()
        yield
        await hot_reload.shutdown()

    server = FastAPI(lifespan=lifespan)
    server.add_websocket_route("/hot-reload", hot_reload, name="hot-reload")  # type: ignore
else:
    server = FastAPI()


server.mount(
    "/static",
    StaticFiles(directory="web/static"),
    name="assets",
)

server.mount(
    "/components",
    StaticFiles(directory="web/components"),
    name="components",
)
server.include_router(api, prefix="/api")
server.include_router(web)
