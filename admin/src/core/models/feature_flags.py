from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.core.models.user import User


class FeatureFlag(Base):
    """
    Representa un flag del sistema.
    
    Attributes:
        id (int): Identificador único del flag.
        key (str): Clave única para referenciar el flag.
        display_name (str): Nombre legible del flag.
        description (str, opcional): Descripción del flag.
        is_enabled (bool): Indica si el flag está habilitado (ON) o deshabilitado (OFF).
        maintenance_message (str, opcional): Mensaje mostrado si el flag es modo mantenimiento.
        last_modified_at (datetime): Fecha y hora de la última modificación.
        last_modified_by (int, opcional): ID del usuario que realizó la última modificación.
    """

    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)   
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)     
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    maintenance_message: Mapped[str] = mapped_column(String(255), nullable=True)
    last_modified_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_modified_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    last_modified_by_user: Mapped["User"] = relationship(
        "User",
        lazy="select",
        foreign_keys=[last_modified_by]
    )

    def __repr__(self):
        return f"<FeatureFlag {self.key}={'ON' if self.is_enabled else 'OFF'}>"