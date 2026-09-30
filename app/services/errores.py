"""Excepciones de dominio compartidas por los services (s10).

Centralizadas acá para que cualquier service/router las use sin dependencias cruzadas.
El router las traduce a códigos HTTP (típicamente 404).
"""


class EquipoNoEncontrado(Exception):
    """No existe el equipo referenciado."""


class ProyectoNoEncontrado(Exception):
    """No existe el proyecto referenciado."""


class TareaNoEncontrada(Exception):
    """No existe la tarea referenciada."""


class UsuarioNoEncontrado(Exception):
    """No existe el usuario referenciado (p. ej. como responsable o autor)."""


class EtiquetaNoEncontrada(Exception):
    """No existe alguna de las etiquetas referenciadas."""
