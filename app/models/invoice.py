from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class InvoiceType(str, enum.Enum):
    BARBERSHOP = "barbershop"
    CAFE = "cafe"
    MIXED = "mixed"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    MIXED = "mixed"


class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    invoice_type = Column(SQLEnum(InvoiceType), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float, default=0)
    payment_method = Column(SQLEnum(PaymentMethod), default=PaymentMethod.CASH)
    paid = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    created_by_user = relationship("User", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    item_type = Column(String(20), nullable=False)  # service, product, retail
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)  # For retail items
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    barber_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # آرایشگری که خدمت را انجام داده
    
    # Relationships
    invoice = relationship("Invoice", back_populates="items")
    service = relationship("Service", back_populates="invoice_items")
    product = relationship("Product", back_populates="invoice_items")
    inventory_item = relationship("InventoryItem")
    barber = relationship("User")
