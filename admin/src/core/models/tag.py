from src.core.database import db, Base
from typing import List
from sqlalchemy import String, Integer, Boolean, DateTime, func, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column,relationship
from datetime import datetime, timezone


sitios_tags = Table(
    'sitios_tags',
    Base.metadata,
    Column('sitio_id', Integer, ForeignKey('sitios.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50))
    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    sitios: Mapped[List["Sitio"]] = relationship(
        "Sitio", secondary=sitios_tags, back_populates="tags", lazy="selectin"
    )

    def __repr__(self):
        return f"<Tag {self.slug}>"
