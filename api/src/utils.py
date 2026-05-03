from typing import Callable, Generic, Optional, TypeVar

from fastapi import HTTPException
from fastapi.responses import JSONResponse
# from pydantic import ValidationError

# from .adapters.dtos import ErrorDTO
# from core.error import DomainError, EtiquetaRepetida, RelacionErronean,

from .dependencies import logger

U = TypeVar("U")
V = TypeVar("V")


class Result(Generic[U, V]):
    def __init__(self, value: U | None = None, error: V | None = None):
        if (value is not None) and (error is not None):
            raise ValueError("Result must have either value or error, not both")
        self._value = value
        self._error = error

    def unwrap(self) -> U | None:
        if self.is_fail:
            raise RuntimeError(self._error)
        return self._value

    def map(self, fn):
        if self.is_ok:
            return Result.ok(fn(self._value))
        return self

    @property
    def is_ok(self) -> bool:
        return self._error is None

    @property
    def is_fail(self) -> bool:
        return self._error is not None

    @property
    def value(self) -> U | None:
        if self.is_fail:
            raise RuntimeError("Tried to access value of failed Result")
        return self._value

    @property
    def error(self) -> V | None:
        if self.is_ok:
            raise RuntimeError("Tried to access error of ok Result")
        return self._error

    @staticmethod
    def ok(value: Optional[U] = None) -> "Result[U, V]":
        return Result(value=value)

    @staticmethod
    def fail(error: V) -> "Result[U, V]":
        return Result(error=error)


ErrorMapper = Callable[[DomainError], HTTPException]


def build_http_exception(status_code: int, err: DomainError) -> HTTPException:
    error_dto = ErrorDTO(**err.to_dict())
    return HTTPException(
        status_code=status_code,
        detail=error_dto.model_dump(),
    )


# ExceptionMapper = Callable[[Exception], DomainError]

# ERRORS_DICT: dict[type[DomainError], ErrorMapper] = {
#     EtiquetaRepetida: lambda err: build_http_exception(409, err),
#     RelacionErronea: lambda err: build_http_exception(409, err),
#     RecurrenciaVaciaEnCreacion: lambda err: build_http_exception(400, err),
#     DetalleInvalido: lambda err: build_http_exception(400, err),
#     MovimientoNoEncontrado: lambda err: build_http_exception(404, err),
# }

# EXCEPTION_DICT: dict[type[Exception], ExceptionMapper] = {
#     # Pydantic → error de input
#     ValidationError: lambda exc: InputInvalidoError(exc.errors()),  # type: ignore
# }


W = TypeVar("W")


def to_http(result) -> W:
    """
    Traduce Result del dominio a HTTP.
    Único punto donde FastAPI conoce los errores de dominio.
    """
    if result.is_ok:
        return result.value

    error = result.error

    # Buscar mapper específico
    mapper = ERRORS_DICT.get(type(error))

    if mapper:
        raise mapper(error)

    # Si es un DomainError no mapeado → BAD REQUEST genérico
    if isinstance(error, DomainError):
        raise build_http_exception(400, error)

    # Si ni siquiera es DomainError → bug
    raise HTTPException(status_code=500, detail="Unexpected application error")


def to_domain_error(exc: Exception) -> DomainError:
    """
    Traduce excepciones internas a DomainError.
    Único punto donde la aplicación entiende excepciones externas.
    """
    mapper = EXCEPTION_DICT.get(type(exc))

    if mapper:
        return mapper(exc)

    # Si ya es DomainError, no lo toques
    if isinstance(exc, DomainError):
        logger.warning("Error de dominio: %s", exc)
        return exc

    # Infraestructura inesperada
    logger.exception("Error inesperado: %s", exc)
    return UnexpectedDomainError()


def run_safely(fn: Callable[[], W]) -> Result[W, DomainError]:
    try:
        return Result.ok(fn())
    except Exception as exc:
        return Result.fail(to_domain_error(exc))


def custom_response(status: int, data: Optional[dict] = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "ok": True,
            "data": data,
        },
    )