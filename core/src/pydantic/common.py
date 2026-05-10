from enum import Enum
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator


class FamiliarTipo(str, Enum):
    CARGADO = "cargado"
    DESCONOCIDO = "desconocido"


class FamiliarRelacion(str, Enum):
    HIJO = "hijo"
    CONYUGE = "conyuge"
    PADRE = "padre"
    MADRE = "madre"
    HERMANO = "hermano"
    OTRO = "otro"


class Sexo(str, Enum):
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    OTRO = "otro"


class ValueObject(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)


class AgregateRoot(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class FamiliarInfo(ValueObject):
    id: Optional[int] = None
    relacion: Optional[FamiliarRelacion] = None
    descripcion: Optional[str] = None


class FamiliarCargado(FamiliarInfo):
    tipo: Literal[FamiliarTipo.CARGADO] = FamiliarTipo.CARGADO
    dni: str | None = None


class FamiliarDesconocido(FamiliarInfo):
    tipo: Literal[FamiliarTipo.DESCONOCIDO] = FamiliarTipo.DESCONOCIDO
    nombre_completo: Optional[str] = None


Familiar = Annotated[
    Union[FamiliarCargado, FamiliarDesconocido], Field(discriminator="tipo")
]

familiar_adapter = TypeAdapter(Familiar)


class GrupoFamiliar(AgregateRoot):
    id: Optional[int] = None
    cantidad: int = 1
    familiares: list[Familiar] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalizar(self):
        self.cantidad = len(self.familiares) + 1
        return self


class Ubicacion(AgregateRoot):
    id: Optional[int] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
