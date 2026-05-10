from typing import Optional

from pydantic import Field

from .common import AgregateRoot, GrupoFamiliar, Sexo, Ubicacion


class Persona(AgregateRoot):
    id: int | None = None
    dni: Optional[str] = None
    nombre: str
    apellido: str
    sexo: Optional[Sexo] = None
    edad: Optional[int] = None
    extranjero: bool = False
    family_owner: bool = False
    cargado_en_caritas: bool = False
    descripcion: Optional[str] = None

    ubicacion: Ubicacion = Field(default_factory=Ubicacion)
    grupo_familiar: Optional[GrupoFamiliar] = None
