from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.database import Base



"""Tabla de asosciacion muchos a muchos entre Sitio y Tag"""

sitios_tags = Table(
    "sitios_tags",
    Base.metadata,
    Column("sitio_id", Integer, ForeignKey("sitios.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
