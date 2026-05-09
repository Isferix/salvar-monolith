from typing import Any, Iterable, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import inspect as sa_inspect

T = TypeVar("T", bound=BaseModel)


def map_model(
    source: BaseModel,
    target_cls: Type[T],
    **overrides: Any,
) -> T:
    """
    Copia los campos con mismo nombre desde `source` hacia `target_cls`,
    permitiendo sobreescrituras explícitas.

    overrides:
        Campos que deben reemplazarse (ej: relaciones ya transformadas).
    """

    source_data = source.model_dump()

    # Nos quedamos solo con los campos que existen en el target
    target_fields = target_cls.model_fields

    filtered = {
        k: v
        for k, v in source_data.items()
        if k in target_fields and k not in overrides
    }

    return target_cls(**filtered, **overrides)


ORM = TypeVar("ORM")


def map_orm_to_model(
    source_orm: Any,
    target_cls: Type[T],
    **overrides: Any,
) -> T:
    """
    Mapea una instancia de SQLAlchemy ORM hacia un modelo Pydantic.

    - Copia automáticamente las columnas que coinciden por nombre.
    - Ignora relaciones lazy (para evitar queries inesperadas).
    - Permite overrides explícitos (ej: relaciones ya transformadas).
    """

    mapper = sa_inspect(source_orm)

    # Obtener SOLO columnas reales (no relaciones) holi45
    column_attrs = {attr.key for attr in mapper.mapper.column_attrs}

    # Campos definidos en el modelo Pydantic destino
    target_fields = target_cls.model_fields.keys()

    filtered: dict[str, Any] = {}

    for field in column_attrs:
        if field in target_fields and field not in overrides:
            filtered[field] = getattr(source_orm, field)

    return target_cls(**filtered, **overrides)


def map_model_to_orm(
    source_model: BaseModel,
    target_orm: ORM,
    *,
    exclude_unset: bool = True,
    exclude_none: bool = False,
    exclude_fields: Iterable[str] | None = None,
    **overrides,
) -> ORM:
    """
    Mapea datos desde un Pydantic model hacia una instancia ORM existente.

    - Pensado para CREATE y UPDATE.
    - No toca relaciones automáticamente.
    - No pisa campos que no vinieron en el request (PATCH-safe).
    - Respeta identity map de SQLAlchemy (no crea otra instancia).
    """

    if exclude_fields is None:
        exclude_fields = set()
    else:
        exclude_fields = set(exclude_fields)

    overrides = overrides or {}

    mapper = sa_inspect(target_orm)

    # Columnas reales de la tabla (evita relaciones)
    column_keys = {attr.key for attr in mapper.mapper.column_attrs}  # type: ignore

    # Dump controlado desde Pydantic v2
    model_data = source_model.model_dump(
        exclude_unset=exclude_unset,
        exclude_none=exclude_none,
    )

    for field, value in model_data.items():
        if field not in column_keys:
            continue

        if field in exclude_fields:
            continue

        if field in overrides:
            continue

        setattr(target_orm, field, value)

    # Aplicar overrides explícitos (ej: FK ya resuelta, hashes, etc.)
    for field, value in overrides.items():
        setattr(target_orm, field, value)

    return target_orm
