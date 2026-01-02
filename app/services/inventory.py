from sqlalchemy.orm import Session
from app.models.inventory import InventoryItem, InventoryTransaction, InventoryType
from typing import List, Dict


def check_stock_alerts(db: Session) -> List[Dict]:
    """Check for items below minimum stock and return alerts"""
    alerts = []
    low_stock_items = db.query(InventoryItem).filter(
        InventoryItem.current_stock <= InventoryItem.min_stock_alert,
        InventoryItem.is_active == True
    ).all()
    
    for item in low_stock_items:
        alerts.append({
            "id": item.id,
            "name": item.name,
            "code": item.code,
            "current_stock": item.current_stock,
            "min_stock_alert": item.min_stock_alert,
            "unit": item.unit,
            "inventory_type": item.inventory_type
        })
    
    return alerts


def deduct_inventory(db: Session, item_id: int, quantity: float, reference_type: str, reference_id: int, notes: str = None):
    """Deduct inventory and create transaction record"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise ValueError(f"Inventory item {item_id} not found")
    
    if item.current_stock < quantity:
        raise ValueError(f"Insufficient stock for {item.name}. Available: {item.current_stock}, Required: {quantity}")
    
    # Deduct stock
    item.current_stock -= quantity
    
    # Create transaction
    transaction = InventoryTransaction(
        item_id=item_id,
        transaction_type="usage",
        quantity=-quantity,
        unit_price=item.unit_price,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes
    )
    db.add(transaction)
    db.commit()


def add_inventory(db: Session, item_id: int, quantity: float, unit_price: float = None, notes: str = None):
    """Add inventory and create transaction record"""
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise ValueError(f"Inventory item {item_id} not found")
    
    # Add stock
    item.current_stock += quantity
    
    # Update unit price if provided
    if unit_price is not None:
        item.unit_price = unit_price
    
    # Create transaction
    transaction = InventoryTransaction(
        item_id=item_id,
        transaction_type="purchase",
        quantity=quantity,
        unit_price=unit_price or item.unit_price,
        notes=notes
    )
    db.add(transaction)
    db.commit()


def get_inventory_value(db: Session, inventory_type: InventoryType = None) -> float:
    """Calculate total inventory value"""
    query = db.query(InventoryItem)
    if inventory_type:
        query = query.filter(InventoryItem.inventory_type == inventory_type)
    
    items = query.all()
    total_value = sum(item.current_stock * item.unit_price for item in items)
    return total_value
