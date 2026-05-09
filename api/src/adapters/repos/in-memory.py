from core.pydantic.ports import Persona, PersonasRepository


class InMemoryPersonasRepository(PersonasRepository):
    def __init__(self):
        self._personas = []

    def save(self, persona: Persona) -> Persona:
        nextId: int = len(self._personas) + 1
        persona.id = nextId
        self._personas.append(persona)
        return persona

    def get_all(self) -> list[Persona]:
        return self._personas

    def get_by_id(self, id: int) -> Persona | None:
        for i, persona in enumerate(self._personas):
            if persona.id == id:
                return persona
            if (i + 1) > id:
                break
        return None

    def get_by_dni(self, dni: str) -> Persona | None:
        for persona in self._personas:
            if persona.dni == dni:
                return persona
        return None

    def put(self, id: int, persona: Persona) -> Persona:
        for i, p in enumerate(self._personas):
            if p.id == id:
                persona.id = id
                self._personas[i] = persona
                return persona
            if (i + 1) > id:
                break
        raise ValueError(f"Persona {id} no existe")

    def delete(self, id: int) -> None:
        for i, persona in enumerate(self._personas):
            if persona.id == id:
                del self._personas[i]
                return
            if (i + 1) > id:
                break
        raise ValueError(f"Persona {id} no existe")

    def delete_all(self) -> None:
        self._personas.clear()
        return None
