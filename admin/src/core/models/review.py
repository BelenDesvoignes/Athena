# admin/src/core/models/review.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from src.core.database import Base  

class ReviewStatus(enum.Enum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"

class Review(Base):  
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer, ForeignKey("sitios.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  
    content = Column(Text, nullable=False)
    status = Column(Enum(ReviewStatus), nullable=False, default=ReviewStatus.PENDIENTE)
    rejection_reason = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted = Column(Boolean, default=False)

    user = relationship("User", back_populates="reviews") 
    site = relationship("Sitio", back_populates="reviews")  

