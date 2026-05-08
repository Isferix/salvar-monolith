from functools import lru_cache
from fastapi.templating import Jinja2Templates

from ..settings import get_settings

settings = get_settings()
is_dev = settings.env == "development"

templates = Jinja2Templates(directory="web/src")
templates.env.globals["year"] = 2026

@lru_cache
def get_templates() -> Jinja2Templates:
    return templates
