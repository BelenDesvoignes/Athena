# definicion del modelo
# plano de tabla de usuarios en la db. Describe los campos y como
# manejar los datos a bajo nivel

from src.core.database import db, Base
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))
    apellido: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        String(20), nullable=False, default="Usuario público"
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    fecha_actualizacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )




    

def __init__(self, nombre, apellido, email, password, rol="Usuario público", activo=True):
#encripta la clave antes de guardarla 
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        # self.password = generate_password_hash(password)
        self.rol = rol
        self.activo = activo


