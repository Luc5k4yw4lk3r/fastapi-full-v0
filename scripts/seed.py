"""Seeds realistas de TaskFlow (s08).

Carga datos de ejemplo realistas (equipos, usuarios con membresías M:N, proyectos,
etiquetas, tareas en varios estados con responsable/etiquetas, y comentarios) para poder
probar el tablero y el endpoint de agentes con contexto real.

Es **idempotente por clave natural** (nombre/email/título): si una fila ya existe, no la
duplica. No usa ids fijos, así las secuencias de la BD avanzan correctamente.

Uso (con Postgres arriba): `python scripts/seed.py`
Carga DATABASE_URL desde `.env` automáticamente si la variable no está seteada.
"""

import os
import sys
from pathlib import Path

# Permite `python scripts/seed.py` desde cualquier lado: agrega el root del proyecto al path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _cargar_env() -> None:
    """Mini-cargador de .env (sin dependencias): setea las variables que falten."""
    env = Path(__file__).resolve().parent.parent / ".env"
    if not env.exists():
        return
    for linea in env.read_text().splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())


_cargar_env()

# Importar DESPUÉS de cargar el .env: el engine lee DATABASE_URL al importarse.
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.db.models import (  # noqa: E402
    ComentarioORM,
    EquipoORM,
    EtiquetaORM,
    ProyectoORM,
    TareaORM,
    UsuarioORM,
)


def _get_or_create(db: Session, modelo, filtros: dict, extra: dict | None = None):
    """Devuelve la fila que cumple `filtros` o la crea con filtros+extra."""
    fila = db.scalars(select(modelo).filter_by(**filtros)).first()
    if fila is not None:
        return fila
    fila = modelo(**filtros, **(extra or {}))
    db.add(fila)
    db.flush()
    return fila


def sembrar() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        # --- Equipos ---
        core = _get_or_create(db, EquipoORM, {"nombre": "Core"})
        plataforma = _get_or_create(db, EquipoORM, {"nombre": "Plataforma"})

        # --- Usuarios ---
        ada = _get_or_create(db, UsuarioORM, {"email": "ada@taskflow.dev"}, {"nombre": "Ada Lovelace"})
        lin = _get_or_create(db, UsuarioORM, {"email": "lin@taskflow.dev"}, {"nombre": "Lin Torvalds"})
        mateo = _get_or_create(db, UsuarioORM, {"email": "mateo@taskflow.dev"}, {"nombre": "Mateo Díaz"})
        sofia = _get_or_create(db, UsuarioORM, {"email": "sofia@taskflow.dev"}, {"nombre": "Sofía Ruiz"})

        # Membresías M:N (idempotente: solo agrega si falta)
        def afiliar(usuario: UsuarioORM, equipo: EquipoORM) -> None:
            if equipo not in usuario.equipos:
                usuario.equipos.append(equipo)

        afiliar(ada, core)
        afiliar(ada, plataforma)
        afiliar(lin, core)
        afiliar(mateo, plataforma)
        afiliar(sofia, plataforma)

        # --- Proyectos ---
        general = _get_or_create(db, ProyectoORM, {"nombre": "General"}, {"equipo_id": core.id})
        onboarding = _get_or_create(
            db,
            ProyectoORM,
            {"nombre": "Onboarding App"},
            {"equipo_id": plataforma.id, "descripcion": "Flujo de alta de nuevos usuarios"},
        )

        # --- Etiquetas ---
        bug = _get_or_create(db, EtiquetaORM, {"nombre": "bug"}, {"color": "#e5484d"})
        feature = _get_or_create(db, EtiquetaORM, {"nombre": "feature"}, {"color": "#30a46c"})
        urgente = _get_or_create(db, EtiquetaORM, {"nombre": "urgente"}, {"color": "#f76b15"})
        docs = _get_or_create(db, EtiquetaORM, {"nombre": "docs"}, {"color": "#0091ff"})

        # --- Tareas ---  (titulo como clave natural)
        def tarea(titulo, proyecto, estado, responsable=None, etiquetas=()):
            t = _get_or_create(
                db,
                TareaORM,
                {"titulo": titulo},
                {
                    "proyecto_id": proyecto.id,
                    "estado": estado,
                    "responsable_id": responsable.id if responsable else None,
                },
            )
            for e in etiquetas:
                if e not in t.etiquetas:
                    t.etiquetas.append(e)
            return t

        tarea("Configurar el tablero inicial", general, "hecho", ada, [feature])
        t_orden = tarea("Arreglar el orden de columnas", general, "en progreso", lin, [bug, urgente])
        tarea("Escribir documentación de la API", general, "backlog", None, [docs])
        t_bienvenida = tarea("Diseñar pantalla de bienvenida", onboarding, "en progreso", mateo, [feature])
        tarea("Validar formulario de registro", onboarding, "backlog", sofia, [bug])
        tarea("Publicar guía de onboarding", onboarding, "backlog", None, [docs])

        # --- Comentarios --- (idempotente por (tarea, texto))
        def comentar(t: TareaORM, autor: UsuarioORM, texto: str) -> None:
            existe = db.scalars(
                select(ComentarioORM).filter_by(tarea_id=t.id, texto=texto)
            ).first()
            if existe is None:
                db.add(ComentarioORM(tarea_id=t.id, autor_id=autor.id, texto=texto))

        comentar(t_orden, lin, "El orden se rompe al mover una tarjeta a 'hecho'.")
        comentar(t_orden, ada, "Lo miro hoy, parece el índice de ordenamiento.")
        comentar(t_bienvenida, mateo, "¿Usamos el logo nuevo o el actual?")

        db.commit()
        print("Seeds cargados (idempotente):")
        print(f"  equipos={db.scalars(select(EquipoORM)).all().__len__()}", end="  ")
        print(f"usuarios={len(db.scalars(select(UsuarioORM)).all())}", end="  ")
        print(f"proyectos={len(db.scalars(select(ProyectoORM)).all())}", end="  ")
        print(f"tareas={len(db.scalars(select(TareaORM)).all())}", end="  ")
        print(f"comentarios={len(db.scalars(select(ComentarioORM)).all())}")


if __name__ == "__main__":
    sembrar()
