"""Capa de repositories: acceso a datos.

Encapsula el almacenamiento tras una interfaz estable. En s05 usa memoria; en s07
pasa a PostgreSQL vía ORM. El dominio depende de esta capa, nunca al revés.
"""
