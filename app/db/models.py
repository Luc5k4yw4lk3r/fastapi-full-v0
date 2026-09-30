"""Modelos ORM de SQLAlchemy — el modelo ER completo de TaskFlow (s07).

Son la representación de PERSISTENCIA, separada de las entidades de dominio Pydantic
(app/models/). Los repositorios mapean entre ambos mundos, así el dominio nunca importa
SQLAlchemy. Incluye las 6 entidades + 2 tablas de enlace para las relaciones M:N
(usuario↔equipo, tarea↔etiqueta). El ER formal está en docs/diagrams/s07-er.mmd.
"""

from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

# --- Tablas de enlace M:N (solo claves foráneas, sin entidad propia) ---
usuario_equipo = Table(
    "usuario_equipo",
    Base.metadata,
    Column("usuario_id", ForeignKey("usuarios.id"), primary_key=True),
    Column("equipo_id", ForeignKey("equipos.id"), primary_key=True),
)

tarea_etiqueta = Table(
    "tarea_etiqueta",
    Base.metadata,
    Column("tarea_id", ForeignKey("tareas.id"), primary_key=True),
    Column("etiqueta_id", ForeignKey("etiquetas.id"), primary_key=True),
)


class EquipoORM(Base):
    __tablename__ = "equipos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    proyectos: Mapped[list["ProyectoORM"]] = relationship(back_populates="equipo")
    miembros: Mapped[list["UsuarioORM"]] = relationship(
        secondary=usuario_equipo, back_populates="equipos"
    )


class UsuarioORM(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    equipos: Mapped[list["EquipoORM"]] = relationship(
        secondary=usuario_equipo, back_populates="miembros"
    )


class ProyectoORM(Base):
    __tablename__ = "proyectos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(160))
    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"))
    descripcion: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    equipo: Mapped["EquipoORM"] = relationship(back_populates="proyectos")
    # Borrar un proyecto borra sus tareas (y, en cascada, sus comentarios).
    tareas: Mapped[list["TareaORM"]] = relationship(
        back_populates="proyecto", cascade="all, delete-orphan"
    )


class TareaORM(Base):
    __tablename__ = "tareas"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descripcion: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    # El estado se guarda como string; el dominio valida con el Enum Estado.
    estado: Mapped[str] = mapped_column(String(20), default="backlog")
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.id"))
    responsable_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    proyecto: Mapped["ProyectoORM"] = relationship(back_populates="tareas")
    responsable: Mapped["UsuarioORM | None"] = relationship()
    # Borrar una tarea borra sus comentarios.
    comentarios: Mapped[list["ComentarioORM"]] = relationship(
        back_populates="tarea", cascade="all, delete-orphan"
    )
    etiquetas: Mapped[list["EtiquetaORM"]] = relationship(
        secondary=tarea_etiqueta, back_populates="tareas"
    )


class ComentarioORM(Base):
    __tablename__ = "comentarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    tarea_id: Mapped[int] = mapped_column(ForeignKey("tareas.id"))
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    texto: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    tarea: Mapped["TareaORM"] = relationship(back_populates="comentarios")
    autor: Mapped["UsuarioORM"] = relationship()


class EtiquetaORM(Base):
    __tablename__ = "etiquetas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(60))
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    tareas: Mapped[list["TareaORM"]] = relationship(
        secondary=tarea_etiqueta, back_populates="etiquetas"
    )
