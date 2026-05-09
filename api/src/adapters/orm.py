from typing import Optional, Self

from core.pydantic.common import (
    Familiar,
    FamiliarCargado,
    FamiliarRelacion,
    FamiliarTipo,
    GrupoFamiliar,
    Ubicacion,
)
from core.pydantic.ports import Persona
from pydantic import TypeAdapter
from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
    MetaData,
    inspect,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from ..utils.mappers import map_model_to_orm, map_orm_to_model

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))

familiar_adapter = TypeAdapter(Familiar)


class PersonaDAO(Base):
    __tablename__ = "persona"

    id: Mapped[int] = mapped_column(primary_key=True)
    dni: Mapped[str | None] = mapped_column(unique=True, index=True, default=None)
    nombre: Mapped[str | None] = mapped_column(default=None)
    apellido: Mapped[str | None] = mapped_column(default=None)
    extranjero: Mapped[bool] = mapped_column(default=False)
    family_owner: Mapped[bool] = mapped_column(default=False)
    cargado_en_caritas: Mapped[bool] = mapped_column(default=False)
    descripcion: Mapped[str | None] = mapped_column(default=None)

    ubicacion = relationship(
        "UbicacionDim",
        back_populates="persona",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )

    grupo_familiar = relationship(
        "GrupoFamiliarDim",
        back_populates="persona",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )

    @classmethod
    def from_domain(cls, persona: Persona) -> Self:
        return map_model_to_orm(
            persona,
            cls(),
            ubicacion=UbicacionDim.from_domain(persona.ubicacion),
            grupo_familiar=GrupoFamiliarDim.from_domain(persona.grupo_familiar)
            if persona.grupo_familiar
            else None,
        )

    def to_domain(self) -> Persona:
        return map_orm_to_model(
            self,
            Persona,
            ubicacion=self.ubicacion.to_domain() if self.ubicacion else Ubicacion(),
            grupo_familiar=self.grupo_familiar.to_domain()
            if self.grupo_familiar
            else None,
        )


class UbicacionDim(Base):
    __tablename__ = "ubicacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("persona.id", ondelete="CASCADE"), unique=True
    )
    direccion: Mapped[str | None] = mapped_column(default=None)
    localidad: Mapped[str | None] = mapped_column(default=None)

    persona = relationship("PersonaDAO", back_populates="ubicacion")

    @classmethod
    def from_domain(cls, ubicacion: "Ubicacion") -> "UbicacionDim":
        return cls(direccion=ubicacion.direccion, localidad=ubicacion.localidad)

    def to_domain(self) -> Ubicacion:
        return Ubicacion(direccion=self.direccion, localidad=self.localidad)


class GrupoFamiliarDim(Base):
    __tablename__ = "grupo_familiar"

    id: Mapped[int] = mapped_column(primary_key=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("persona.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    cantidad: Mapped[int]

    persona = relationship("PersonaDAO", back_populates="grupo_familiar")
    miembros = relationship(
        "MiembroGrupoFamiliar",
        back_populates="grupo",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @classmethod
    def from_domain(cls, grupo_familiar: GrupoFamiliar) -> "GrupoFamiliarDim":
        instance = cls(id=grupo_familiar.id, cantidad=grupo_familiar.cantidad)

        instance.miembros = [
            MiembroGrupoFamiliar.from_domain(miembro)
            for miembro in grupo_familiar.familiares
        ]
        return instance

    def to_domain(self) -> GrupoFamiliar:
        return GrupoFamiliar(
            id=self.id,
            cantidad=self.cantidad,
            familiares=[miembro.to_domain() for miembro in self.miembros],
        )


class MiembroGrupoFamiliar(Base):
    __tablename__ = "miembro_grupo_familiar"

    id: Mapped[int] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(
        ForeignKey("grupo_familiar.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo: Mapped[FamiliarTipo] = mapped_column(Enum(FamiliarTipo), nullable=False)
    relacion: Mapped[FamiliarRelacion] = mapped_column(
        Enum(FamiliarRelacion), nullable=True
    )
    descripcion: Mapped[str] = mapped_column(default="")
    datos: Mapped[dict] = mapped_column(JSON)

    grupo = relationship("GrupoFamiliarDim", back_populates="miembros")

    @classmethod
    def from_domain(cls, familiar: Familiar) -> "MiembroGrupoFamiliar":
        if isinstance(familiar, FamiliarCargado):
            datos = {"dni": familiar.dni}
        else:
            datos = {"nombre_completo": familiar.nombre_completo}

        return cls(
            tipo=familiar.tipo,
            relacion=familiar.relacion.value if familiar.relacion else None,
            descripcion=familiar.descripcion,
            datos=datos,
        )

    def to_domain(self) -> Familiar:
        # Extrae solo las columnas mapeadas en un dict
        mapper = inspect(self).mapper
        data = {c.key: getattr(self, c.key) for c in mapper.column_attrs}

        return familiar_adapter.validate_python(data)


class SqlAlchemyPersonasRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, persona: Persona) -> Persona:
        dao = PersonaDAO.from_domain(persona)

        self.db.add(dao)
        self.db.flush()
        self.db.refresh(dao)

        return dao.to_domain()

    def get_all(self) -> list[Persona]:
        stmt = select(PersonaDAO)
        result = self.db.execute(stmt).scalars().all()
        return [dao.to_domain() for dao in result]

    def get_by_id(self, id: int) -> Optional[Persona]:
        dao: PersonaDAO = self.db.get(PersonaDAO, id)
        return dao.to_domain() if dao else None

    def get_by_dni(self, dni: str) -> Optional[Persona]:
        stmt = select(PersonaDAO).where(PersonaDAO.dni == dni)
        dao: PersonaDAO = self.db.execute(stmt).scalars().first()
        return dao.to_domain() if dao else None

    def put(self, id: int, persona: Persona) -> Persona:
        existing: PersonaDAO = self.db.get(PersonaDAO, id)

        if not existing:
            raise ValueError(f"Persona {id} no existe")

        # Update campos simples
        existing.dni = persona.dni
        existing.nombre = persona.nombre
        existing.apellido = persona.apellido
        existing.extranjero = persona.extranjero
        existing.family_owner = persona.family_owner
        existing.cargado_en_caritas = persona.cargado_en_caritas
        existing.descripcion = persona.descripcion

        # Ubicacion (overwrite)
        if existing.ubicacion:
            existing.ubicacion.direccion = persona.ubicacion.direccion
            existing.ubicacion.localidad = persona.ubicacion.localidad
        else:
            existing.ubicacion = UbicacionDim.from_domain(persona.ubicacion)

        # Grupo familiar (overwrite completo)
        if persona.grupo_familiar:
            if not persona.family_owner:
                raise ValueError("Solo family_owner puede tener grupo familiar")

            existing.grupo_familiar = GrupoFamiliarDim.from_domain(
                persona.grupo_familiar
            )
        else:
            existing.grupo_familiar = None

        self.db.flush()
        self.db.refresh(existing)

        return existing.to_domain()

    def delete(self, id: int) -> None:
        dao: PersonaDAO = self.db.get(PersonaDAO, id)
        if not dao:
            return

        self.db.delete(dao)
        self.db.commit()
        return None

    def delete_all(self) -> None:
        self.db.query(MiembroGrupoFamiliar).delete()
        self.db.query(GrupoFamiliarDim).delete()
        self.db.query(UbicacionDim).delete()
        self.db.query(PersonaDAO).delete()
        self.db.commit()
        return None
