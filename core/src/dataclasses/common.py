from dataclasses import dataclass, field
from enum import Enum
from typing import List, Literal, Optional, Union


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


@dataclass
class FamiliarInfo:
    id: Optional[int] = None
    relacion: Optional[FamiliarRelacion] = None
    descripcion: Optional[str] = None


@dataclass
class FamiliarCargado(FamiliarInfo):
    tipo: Literal[FamiliarTipo.CARGADO] = FamiliarTipo.CARGADO
    dni: str = ""


@dataclass
class FamiliarDesconocido(FamiliarInfo):
    tipo: Literal[FamiliarTipo.DESCONOCIDO] = FamiliarTipo.DESCONOCIDO
    nombre_completo: Optional[str] = None


Familiar = Union[FamiliarCargado, FamiliarDesconocido]


@dataclass
class GrupoFamiliar:
    id: Optional[int] = None
    cantidad: int = 1
    familiares: List[Familiar] = field(default_factory=list)

    def normalizar(self):
        self.cantidad = len(self.familiares) + 1


@dataclass
class Ubicacion:
    id: Optional[int] = None
    direccion: Optional[str] = None
    localidad: Optional[str] = None
