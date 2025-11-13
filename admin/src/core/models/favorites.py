from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("public_users.id"))
    sitio_id: Mapped[int] = mapped_column(ForeignKey("sitios.id"))

    user = relationship("PublicUser", back_populates="favorites")
    sitio = relationship("Sitio", back_populates="favorites")
