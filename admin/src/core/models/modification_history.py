from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from src.core.database import Base

class ModificationHistory(Base):
    __tablename__ = "historial_modificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sitio_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    tipo_accion: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_modificacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    sitio = relationship("Sitio", backref="historial_modificaciones")
    usuario = relationship("User", backref="historial_modificaciones")

    def __repr__(self):
        return f"<HistorialModificacion(sitio_id={self.sitio_id}, usuario_id={self.usuario_id}, tipo_accion={self.tipo_accion})>"
