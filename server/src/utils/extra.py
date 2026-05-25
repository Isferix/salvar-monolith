from dependencies import logger, templates


async def reload_templates():
    logger.info("Reloading Jinja2 templates...")
    templates.env.cache = {}
    logger.info("Jinja2 templates reloaded.")
