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
        sitio_id (int, opcional): ID del sitio modificado (puede ser None si se eliminó).
        sitio_nombre (str): Nombre del sitio en el momento de la modificación.
        usuario_id (int): ID del usuario que realizó la modificación.
        tipo_accion (str): Tipo de acción realizada (ej. "editar", "eliminar").
        fecha_modificacion (datetime): Fecha y hora de la modificación (UTC-3).
        usuario (User): Relación con el usuario que realizó la modificación.
    """
    __tablename__ = "historial_modificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sitio_id: Mapped[int] = mapped_column(Integer, nullable=True)
    sitio_nombre: Mapped[str] = mapped_column(String(100))
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    tipo_accion: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_modificacion: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(arg_tz), nullable=False
    )
    
    usuario = relationship("User", backref="historial_modificaciones")

    def __repr__(self):
        return f"<HistorialModificacion(sitio_id={self.sitio_id}, sitio_nombre={self.sitio_nombre}, usuario_id={self.usuario_id}, tipo_accion={self.tipo_accion})>"
