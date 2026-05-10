from functools import partial
from typing import List, Optional

from .common import Familiar, FamiliarCargado, FamiliarDesconocido
from .ports import Persona, PersonasRepository, PersonasSerializer

# from monolith.adapters.excel import *


def resolver_nombre_familiar(repo: PersonasRepository, familiar: Familiar) -> str:
    match familiar:
        case FamiliarCargado(dni=dni) if dni:
            persona = repo.get_by_dni(dni)
            if persona:
                return (
                    f"{persona.nombre} {persona.apellido} (Ya está cargado DNI: {dni})"
                )
            return f"DNI: {dni}"

        case FamiliarDesconocido(nombre_completo=nombre) if nombre:
            return nombre

    return ""


class PersonasHandler:
    def __init__(self, repo: PersonasRepository):
        self.repo = repo

    def create_persona(self, persona: Persona) -> Persona:
        if persona.family_owner and persona.grupo_familiar:
            raise ValueError("Solo family_owner puede tener grupo familiar")

        return self.repo.save(persona)

    def get_all_personas(self) -> List[Persona]:
        personas = self.repo.get_all()
        return personas

    def get_persona_by_id(self, id: int) -> Optional[Persona]:
        return self.repo.get_by_id(id)

    def get_persona_by_dni(self, dni: str) -> Optional[Persona]:
        return self.repo.get_by_dni(dni)

    def update_persona(self, id: int, persona: Persona) -> Persona:
        if persona.family_owner and persona.grupo_familiar:
            raise ValueError("Solo family_owner puede tener grupo familiar")

        return self.repo.put(id, persona)

    def delete_persona(self, id: int) -> None:
        self.repo.delete(id)


class SerializerHandler:
    def __init__(self, serializer: "PersonasSerializer", repo: PersonasRepository):
        self.serializer = serializer
        self.personas = repo

    def import_data(self, path: str) -> None:
        self.personas.delete_all()  # Limpiar antes de importar
        self.serializer.import_data(path, self.personas.save)

    def export_data(self) -> str:
        return self.serializer.export_data(
            personas=self.personas.get_all(),
            name_resolver=partial(resolver_nombre_familiar, self.personas),
        )
