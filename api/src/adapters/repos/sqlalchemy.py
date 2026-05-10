from typing import Self

from core.pydantic.common import (
    Familiar,
    FamiliarCargado,
    FamiliarRelacion,
    FamiliarTipo,
    GrupoFamiliar,
    Ubicacion,
    familiar_adapter,
)
from core.pydantic.ports import Persona, PersonasRepository
from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
    MetaData,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from ...utils.mappers import map_model_to_orm

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


Base = declarative_base(metadata=MetaData(naming_convention=NAMING_CONVENTION))


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

    ubicacion: Mapped["UbicacionDim | None"] = relationship(
        "UbicacionDim",
        back_populates="persona",
        uselist=False,
        lazy="joined",
        cascade="all, delete-orphan",
    )

    grupo_familiar: Mapped["GrupoFamiliarDim | None"] = relationship(
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
        return Persona.model_validate(self)


class UbicacionDim(Base):
    __tablename__ = "ubicacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    persona_id: Mapped[int] = mapped_column(
        ForeignKey("persona.id", ondelete="CASCADE"), unique=True
    )
    direccion: Mapped[str | None] = mapped_column(default=None)
    localidad: Mapped[str | None] = mapped_column(default=None)

    persona: Mapped["PersonaDAO"] = relationship(
        "PersonaDAO", back_populates="ubicacion"
    )

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

    persona: Mapped["PersonaDAO"] = relationship(
        "PersonaDAO", back_populates="grupo_familiar"
    )
    miembros: Mapped[list["MiembroGrupoFamiliar"]] = relationship(
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
        return GrupoFamiliar.model_validate(self)


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

    grupo: Mapped["GrupoFamiliarDim"] = relationship(
        "GrupoFamiliarDim", back_populates="miembros"
    )

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
        return familiar_adapter.validate_python(self)


class SqlAlchemyPersonasRepository(PersonasRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, persona: Persona) -> Persona:
        dao = PersonaDAO.from_domain(persona)

        self.db.add(dao)
        self.db.flush()
        self.db.commit()

        return dao.to_domain()

    def get_all(self) -> list[Persona]:
        stmt = select(PersonaDAO)
        result = self.db.execute(stmt).scalars().all()
        return [dao.to_domain() for dao in result]

    def get_by_id(self, id: int) -> Persona | None:
        dao: PersonaDAO = self.db.get(PersonaDAO, id)
        return dao.to_domain() if dao else None

    def get_by_dni(self, dni: str) -> Persona | None:
        stmt = select(PersonaDAO).where(PersonaDAO.dni == dni)
        dao: PersonaDAO = self.db.execute(stmt).scalars().first()
        return dao.to_domain() if dao else None

    def put(self, id: int, persona: Persona) -> Persona:
        existing: PersonaDAO = self.db.get(PersonaDAO, id)

        if not existing:
            raise ValueError(f"Persona {id} no existe")

        map_model_to_orm(
            persona,
            existing,
            exclude_fields={"ubicacion", "grupo_familiar"},
        )

        # Relaciones
        if persona.ubicacion:
            if existing.ubicacion is None:
                existing.ubicacion = UbicacionDim()

            map_model_to_orm(persona.ubicacion, existing.ubicacion)

        if persona.grupo_familiar:
            if existing.grupo_familiar is None:
                existing.grupo_familiar = GrupoFamiliarDim()

            map_model_to_orm(persona.grupo_familiar, existing.grupo_familiar)

        self.db.flush()
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
