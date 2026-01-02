from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Product(Base):
    """محصولات کافه (نوشیدنی‌ها و غذاها)"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, index=True)
    price = Column(Float, nullable=False)
    category = Column(String(50))  # coffee, tea, dessert, etc.
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recipe_items = relationship("RecipeItem", back_populates="product")
    invoice_items = relationship("InvoiceItem", back_populates="product")


class RecipeItem(Base):
    """فرمولاسیون محصولات کافه - Recipe/BOM for cafe products"""
    __tablename__ = "recipe_items"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # مقدار مورد نیاز
    
    # Relationships
    product = relationship("Product", back_populates="recipe_items")
    inventory_item = relationship("InventoryItem")


class BOMItem(Base):
    """Bill of Materials for barbershop services"""
    __tablename__ = "bom_items"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # مقدار مورد نیاز
    
    # Relationships
    service = relationship("Service", back_populates="bom_items")
    inventory_item = relationship("InventoryItem", back_populates="bom_items")
