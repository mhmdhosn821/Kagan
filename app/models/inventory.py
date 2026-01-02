from sqlalchemy import Column, Integer, String, Float, Boolean, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class InventoryType(str, enum.Enum):
    CAFE = "cafe"
    BARBERSHOP = "barbershop"


class InventoryItemType(str, enum.Enum):
    RAW_MATERIAL = "raw_material"  # مواد اولیه/مصرفی
    RETAIL_PRODUCT = "retail_product"  # محصولات ویترینی


class UnitType(str, enum.Enum):
    GRAM = "gram"
    ML = "ml"
    PIECE = "piece"
    LITER = "liter"
    KG = "kg"


class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, index=True)
    inventory_type = Column(SQLEnum(InventoryType), nullable=False)
    item_type = Column(SQLEnum(InventoryItemType), nullable=False)
    unit = Column(SQLEnum(UnitType), nullable=False)
    current_stock = Column(Float, default=0)
    min_stock_alert = Column(Float, default=0)  # حداقل موجودی برای هشدار
    unit_price = Column(Float, default=0)  # قیمت واحد
    retail_price = Column(Float, nullable=True)  # قیمت فروش (برای محصولات ویترینی)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("InventoryTransaction", back_populates="item")
    bom_items = relationship("BOMItem", back_populates="inventory_item")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # purchase, usage, sale, adjustment
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, default=0)
    reference_type = Column(String(50))  # invoice, service, etc.
    reference_id = Column(Integer)
    notes = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship("InventoryItem", back_populates="transactions")
