"""Capa de infraestructura de base de datos (s07).

Contiene el motor/sesión de SQLAlchemy (database.py) y los modelos ORM (models.py),
separados de las entidades de dominio de app/models/. Solo los repositorios importan
esta capa; el dominio nunca depende de ella.
"""
