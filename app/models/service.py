from sqlalchemy import Column, Integer, String, Float, Boolean, Enum as SQLEnum, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ServiceCategory(str, enum.Enum):
    HAIRCUT = "haircut"  # اصلاح
    STYLING = "styling"  # گریم
    MASSAGE = "massage"  # ماساژ
    COLORING = "coloring"  # رنگ
    OTHER = "other"


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(SQLEnum(ServiceCategory), nullable=False)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=30)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bom_items = relationship("BOMItem", back_populates="service")
    invoice_items = relationship("InvoiceItem", back_populates="service")
