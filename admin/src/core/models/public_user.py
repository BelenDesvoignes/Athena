from sqlalchemy import String, Integer
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base


class PublicUser(Base):
    __tablename__ = "public_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

  
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="user", lazy="selectin")