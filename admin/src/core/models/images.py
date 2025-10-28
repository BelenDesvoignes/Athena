from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base

class Imagen(Base):
    __tablename__ = "imagenes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sitio_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id"), nullable=False)

    ruta: Mapped[str] = mapped_column(String(500), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(300), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    es_portada: Mapped[bool] = mapped_column(Boolean, default=False)
    creada: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    actualizada: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    sitio: Mapped["Sitio"] = relationship("Sitio", back_populates="imagenes")

    def __repr__(self):
        return f"<Imagen(id={self.id}, titulo={self.titulo}, principal={self.es_portada})>"
