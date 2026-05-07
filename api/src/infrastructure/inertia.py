from inertia import InertiaConfig, inertia_dependency_factory

from settings import get_settings

from .jinja import templates

settings = get_settings()

inertia_config = InertiaConfig(
    environment=settings.env,
    version="1.0.0",
    manifest_json_path=settings.manifest_json_path,
    dev_url=str("http://web:3000") if settings.env == "development" else "",
    entrypoint_filename="main.ts",
    templates=templates,
)

inertia_dependency = inertia_dependency_factory(inertia_config)
