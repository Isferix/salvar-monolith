from .infrastructure.jinja import get_templates
from .infrastructure.logger import setup_logger

logger = setup_logger("server")
templates = get_templates()
