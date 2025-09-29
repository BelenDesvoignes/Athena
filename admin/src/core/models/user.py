from src.core.database import Base
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.models.role_permission import Role



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))
    apellido: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    # ADICIONAL para proteger al admin principal
    system_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # corresponde a SI NO y Bloqueado Desbloqueado)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    role: Mapped["Role"] = relationship(back_populates="users", lazy="joined")


    def __repr__(self):
        return f"<User {self.email}>"


