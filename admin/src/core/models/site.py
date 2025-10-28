from datetime import datetime
from typing import List
from geoalchemy2.types import Geometry
from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .tag import sitios_tags
from src.core.database import Base


class Sitio(Base):
    __tablename__ = "sitios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion_breve: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion_completa: Mapped[str] = mapped_column(String(1000), nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    estado_conservacion: Mapped[str] = mapped_column(String(20), nullable=False)
    inauguracion: Mapped[int] = mapped_column(Integer, nullable=False)
    registrado: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ubicacion: Mapped[str] = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)

    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=sitios_tags, back_populates="sitios", lazy="selectin")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="site", lazy="selectin")
    imagenes: Mapped[List["Imagen"]] = relationship(
        "Imagen", back_populates="sitio", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self):
        return f"<Sitio(id={self.id}, nombre={self.nombre})>"
