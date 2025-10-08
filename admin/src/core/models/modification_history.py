from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone, timedelta
from src.core.database import Base

arg_tz = timezone(timedelta(hours=-3))

class ModificationHistory(Base):
    """
    Representa un registro de modificaciones realizadas en un sitio histórico.
    
    Attributes:
        id (int): Identificador único del registro.
        sitio_id (int): ID del sitio modificado.
        usuario_id (int): ID del usuario que realizó la modificación.
        tipo_accion (str): Tipo de acción realizada (ej. "editar", "eliminar").
        fecha_modificacion (datetime): Fecha y hora de la modificación (UTC-3).
        sitio (Sitio): Relación con el sitio modificado.
        usuario (User): Relación con el usuario que realizó la modificación.
    """
    __tablename__ = "historial_modificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sitio_id: Mapped[int] = mapped_column(Integer, ForeignKey("sitios.id"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    tipo_accion: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_modificacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(arg_tz), nullable=False)

    sitio = relationship("Sitio", backref="historial_modificaciones")
    usuario = relationship("User", backref="historial_modificaciones")

    def __repr__(self):
        return f"<HistorialModificacion(sitio_id={self.sitio_id}, usuario_id={self.usuario_id}, tipo_accion={self.tipo_accion})>"
