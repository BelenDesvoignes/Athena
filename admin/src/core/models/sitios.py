from src.core.database import db, Base
from sqlalchemy import String, Integer, Boolean, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Sitio(Base):
    __tablename__ = "sitios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion_breve: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion_completa: Mapped[str] = mapped_column(String(1000), nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    provincia: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    estado_conservacion: Mapped[str] = mapped_column(String(20), nullable=False)  # Bueno, Regular, Malo
    inauguracion: Mapped[int] = mapped_column(Integer, nullable=False)  # Año
    registrado: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Relación con etiquetas (muchos a muchos)
    etiquetas = relationship("Etiqueta", secondary="sitio_etiqueta", back_populates="sitios")
    
    def __repr__(self):
        return f"<Sitio(id={self.id}, nombre={self.nombre})>"

    