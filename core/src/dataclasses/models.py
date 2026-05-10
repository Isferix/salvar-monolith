from dataclasses import dataclass, field
from typing import Optional

from .common import GrupoFamiliar, Sexo, Ubicacion


@dataclass
class Persona:
    id: int
    dni: Optional[str]
    nombre: str
    apellido: str
    sexo: Optional[Sexo] = None
    edad: Optional[int] = None
    extranjero: bool = False
    family_owner: bool = False
    cargado_en_caritas: bool = False
    descripcion: Optional[str] = None

    ubicacion: Ubicacion = field(default_factory=Ubicacion)
    grupo_familiar: Optional[GrupoFamiliar] = None
