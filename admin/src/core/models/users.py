from src.core.database import db, Base
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


def __init__(self, nombre, email, password):
    # encripta la clave antes de guardarla
    self.nombre = nombre
    self.email = email
    self.password = generate_password_hash(password)


def check_password(self, password):
    # compara la clave encriptada con la clave ingresada
    return check_password_hash(self.password, password)
