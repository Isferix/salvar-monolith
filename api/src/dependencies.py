from typing import Annotated

from fastapi import Depends
from fastapi.templating import Jinja2Templates

from .infrastructure.jinja import get_templates
from .infrastructure.logger import setup_logger

logger = setup_logger("server")

TemplatesDependency = Annotated[Jinja2Templates, Depends(get_templates)]