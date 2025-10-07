from src.core.database import Base
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.core.models.user import User

class FeatureFlag(Base):
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