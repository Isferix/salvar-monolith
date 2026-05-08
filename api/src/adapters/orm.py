from typing import List, Optional

from core.pydantic.common import (
    Familiar,
    FamiliarCargado,
    FamiliarDesconocido,
    FamiliarRelacion,
    FamiliarTipo,
    GrupoFamiliar,
    Ubicacion,
)
from core.pydantic.ports import Persona
from sqlalchemy import (
    JSON,
    Boolean,
    ForeignKey,
    Integer,
    MetaData,
    String,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dni: Mapped[str] = mapped_column(String, unique=True, index=True)
    nombre: Mapped[Optional[str]] = mapped_column(String, default=None)
    apellido: Mapped[Optional[str]] = mapped_column(String, default=None)
    extranjero: Mapped[bool] = mapped_column(Boolean, default=False)
    family_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    cargado_en_caritas: Mapped[bool] = mapped_column(Boolean, default=False)
    descripcion: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, default=None
    )

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
    def from_domain(cls, persona: Persona) -> "PersonaDAO":
        return cls(
            id=persona.id,
            dni=persona.dni,
            nombre=persona.nombre,
            apellido=persona.apellido,
            extranjero=persona.extranjero,
            family_owner=persona.family_owner,
            cargado_en_caritas=persona.cargado_en_caritas,
            descripcion=persona.descripcion,
            ubicacion=UbicacionDim.from_domain(persona.ubicacion),
            grupo_familiar=(
                GrupoFamiliarDim.from_domain(persona.grupo_familiar)
                if persona.grupo_familiar
                else None
            ),
        )

    def to_domain(self) -> Persona:
        return Persona(
            id=self.id,
            dni=self.dni,
            nombre=self.nombre,
            apellido=self.apellido,
            extranjero=self.extranjero,
            family_owner=self.family_owner,
            cargado_en_caritas=self.cargado_en_caritas,
            descripcion=self.descripcion,
            ubicacion=self.ubicacion.to_domain() if self.ubicacion else Ubicacion(),
            grupo_familiar=self.grupo_familiar.to_domain()
            if self.grupo_familiar
            else None,
        )


class UbicacionDim(Base):
    __tablename__ = "ubicacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("persona.id", ondelete="CASCADE"), unique=True
    )
    direccion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    localidad: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    persona = relationship("PersonaDAO", back_populates="ubicacion")

    @classmethod
    def from_domain(cls, ubicacion: "Ubicacion") -> "UbicacionDim":
        return cls(direccion=ubicacion.direccion, localidad=ubicacion.localidad)  # type: ignore

    def to_domain(self) -> Ubicacion:
        return Ubicacion(direccion=self.direccion, localidad=self.localidad)


class GrupoFamiliarDim(Base):
    __tablename__ = "grupo_familiar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    persona_id: Mapped[int] = mapped_column(
        Integer,
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
        instance = cls(cantidad=grupo_familiar.cantidad)  # type: ignore
        instance.miembros = [
            MiembroGrupoFamiliar(
                tipo=miembro.tipo,
                relacion=miembro.relacion,
                descripcion=miembro.descripcion,
                datos=miembro.__dict__,
            )
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grupo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("grupo_familiar.id", ondelete="CASCADE"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(String, nullable=False)
    relacion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    datos: Mapped[dict] = mapped_column(JSON)

    grupo = relationship("GrupoFamiliarDim", back_populates="miembros")

    @classmethod
    def from_domain(cls, familiar: Familiar) -> "MiembroGrupoFamiliar":
        if familiar.tipo == FamiliarTipo.CARGADO:
            datos = {"dni": familiar.dni}  # type: ignore
        elif familiar.tipo == FamiliarTipo.DESCONOCIDO:
            datos = {"nombre_completo": familiar.nombre_completo}  # type: ignore
        else:
            raise ValueError(f"Unknown familiar type: {familiar.tipo}")
        return cls(
            tipo=familiar.tipo,  # type: ignore
            relacion=familiar.relacion.value if familiar.relacion else None,  # type: ignore
            descripcion=familiar.descripcion,  # type: ignore
            datos=datos,  # type: ignore
        )

    def to_domain(self) -> Familiar:
        tipo = FamiliarTipo(self.tipo)

        base_kwargs = dict(
            id=self.id,
            relacion=FamiliarRelacion(self.relacion) if self.relacion else None,
            descripcion=self.descripcion,
        )

        if tipo == FamiliarTipo.CARGADO:
            return FamiliarCargado(
                **base_kwargs,  # type: ignore
                dni=self.datos.get("dni"),  # type: ignore
            )
        elif tipo == FamiliarTipo.DESCONOCIDO:
            return FamiliarDesconocido(
                **base_kwargs,  # type: ignore
                nombre_completo=self.datos.get("nombre_completo"),  # type: ignore
            )
        else:
            raise ValueError(f"Unknown familiar type: {self.tipo}")


class SqlAlchemyPersonasRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    @staticmethod
    def _commit(session: Session):
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise

    # -------------------------
    # CREATE / UPSERT
    # -------------------------
    def save(self, persona: Persona) -> Persona:
        with self.session_factory() as session:
            if persona.grupo_familiar:
                persona.grupo_familiar.normalizar()

            dao = PersonaDAO.from_domain(persona)

            session = self.session_factory()
            session.add(dao)
            session.flush()  # genera IDs
            session.refresh(dao)

            self._commit(session)

            return dao.to_domain()

    # -------------------------
    # READ ALL
    # -------------------------
    def get_all(self) -> List[Persona]:
        with self.session_factory() as session:
            stmt = select(PersonaDAO)
            result = session.execute(stmt).scalars().all()
            return [dao.to_domain() for dao in result]

    # -------------------------
    # READ BY ID
    # -------------------------
    def get_by_id(self, id: int) -> Optional[Persona]:
        with self.session_factory() as session:
            dao: PersonaDAO = session.get(PersonaDAO, id)  # type: ignore
            return dao.to_domain() if dao else None

    # -------------------------
    # READ BY DNI
    # -------------------------
    def get_by_dni(self, dni: str) -> Optional[Persona]:
        with self.session_factory() as session:
            stmt = select(PersonaDAO).where(PersonaDAO.dni == dni)
            dao: PersonaDAO = session.execute(stmt).scalars().first()  # type: ignore
            return dao.to_domain() if dao else None

    # -------------------------
    # UPDATE (PUT)
    # -------------------------
    def put(self, id: int, persona: Persona) -> Persona:
        with self.session_factory() as session:
            existing: PersonaDAO = session.get(PersonaDAO, id)  # type: ignore

            if not existing:
                raise ValueError(f"Persona {id} no existe")

            if persona.grupo_familiar:
                persona.grupo_familiar.normalizar()

            # --------
            # Update campos simples
            # --------
            existing.dni = persona.dni
            existing.nombre = persona.nombre
            existing.apellido = persona.apellido
            existing.extranjero = persona.extranjero
            existing.family_owner = persona.family_owner
            existing.cargado_en_caritas = persona.cargado_en_caritas
            existing.descripcion = persona.descripcion

            # --------
            # Ubicacion (overwrite)
            # --------
            if existing.ubicacion:
                existing.ubicacion.direccion = persona.ubicacion.direccion
                existing.ubicacion.localidad = persona.ubicacion.localidad
            else:
                existing.ubicacion = UbicacionDim.from_domain(persona.ubicacion)

            # --------
            # Grupo familiar (overwrite completo)
            # --------
            if persona.grupo_familiar:
                if not persona.family_owner:
                    raise ValueError("Solo family_owner puede tener grupo familiar")

                existing.grupo_familiar = GrupoFamiliarDim.from_domain(
                    persona.grupo_familiar
                )
            else:
                existing.grupo_familiar = None

            session.flush()
            session.refresh(existing)

            self._commit(session)

            return existing.to_domain()

    # -------------------------
    # DELETE
    # -------------------------
    def delete(self, id: int) -> None:
        with self.session_factory() as session:
            dao: PersonaDAO = self.session.get(PersonaDAO, id)  # type: ignore

            if not dao:
                return

            session.delete(dao)
            session.flush()
            self._commit(session)

    def delete_all(self) -> None:
        with self.session_factory() as session:
            session.query(MiembroGrupoFamiliar).delete()
            session.query(GrupoFamiliarDim).delete()
            session.query(UbicacionDim).delete()
            session.query(PersonaDAO).delete()
            self._commit(session)
