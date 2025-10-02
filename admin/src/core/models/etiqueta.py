from src.core.database import db, Base
from sqlalchemy import String, Integer, DateTime, func, Table, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import unicodedata
import re

sitio_etiqueta = Table(
    "sitio_etiqueta", Base.metadata,
    mapped_column("sitio_id", Integer, ForeignKey("sitios.id")),
    mapped_column("etiqueta_id", Integer, ForeignKey("etiquetas.id"))
)

class Etiqueta(Base):
    __tablename__ = "etiquetas"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)
    creado: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    sitios = relationship("Sitio", secondary="sitio_etiqueta", back_populates="etiquetas")

    def __init__(self, nombre):
        self.nombre = nombre
        self.slug = self.generate_slug(nombre)

    @staticmethod
    def generate_slug(nombre):
        # Normaliza, quita acentos, convierte a minúsculas, reemplaza espacios y caracteres no válidos por guiones
        nombre = unicodedata.normalize('NFKD', nombre).encode('ascii', 'ignore').decode('ascii')
        nombre = nombre.lower()
        nombre = re.sub(r'[^a-z0-9]+', '-', nombre)
        nombre = re.sub(r'-+', '-', nombre).strip('-')
        return nombre

    def __repr__(self):
        return f"<Etiqueta(id={self.id}, nombre={self.nombre}, slug={self.slug})>"