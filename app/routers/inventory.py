from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.inventory import InventoryItem, InventoryTransaction, InventoryType, InventoryItemType, UnitType
from app.services.auth import get_current_active_user, require_admin
from app.services.inventory import check_stock_alerts, add_inventory, get_inventory_value
from app.models.user import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


class InventoryItemCreate(BaseModel):
    name: str
    code: str
    inventory_type: InventoryType
    item_type: InventoryItemType
    unit: UnitType
    min_stock_alert: float
    unit_price: float
    retail_price: Optional[float] = None


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    min_stock_alert: Optional[float] = None
    unit_price: Optional[float] = None
    retail_price: Optional[float] = None
    is_active: Optional[bool] = None


class InventoryItemResponse(BaseModel):
    id: int
    name: str
    code: str
    inventory_type: InventoryType
    item_type: InventoryItemType
    unit: UnitType
    current_stock: float
    min_stock_alert: float
    unit_price: float
    retail_price: Optional[float] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    quantity: float
    unit_price: Optional[float] = None
    notes: Optional[str] = None


@router.post("/", response_model=InventoryItemResponse)
def create_inventory_item(item: InventoryItemCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(require_admin)):
    # Check if code already exists
    if db.query(InventoryItem).filter(InventoryItem.code == item.code).first():
        raise HTTPException(status_code=400, detail="Item code already exists")
    
    new_item = InventoryItem(**item.dict())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.get("/", response_model=List[InventoryItemResponse])
def get_inventory_items(inventory_type: InventoryType = None, skip: int = 0, limit: int = 100,
                       db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    query = db.query(InventoryItem)
    if inventory_type:
        query = query.filter(InventoryItem.inventory_type == inventory_type)
    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/alerts")
def get_stock_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    alerts = check_stock_alerts(db)
    return {"alerts": alerts, "count": len(alerts)}


@router.get("/value")
def get_total_inventory_value(inventory_type: InventoryType = None, db: Session = Depends(get_db),
                             current_user: User = Depends(get_current_active_user)):
    value = get_inventory_value(db, inventory_type)
    return {"inventory_type": inventory_type, "total_value": value}


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(item_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(item_id: int, item_update: InventoryItemUpdate, db: Session = Depends(get_db),
                         current_user: User = Depends(require_admin)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.post("/{item_id}/add-stock")
def add_stock(item_id: int, adjustment: StockAdjustment, db: Session = Depends(get_db),
             current_user: User = Depends(get_current_active_user)):
    try:
        add_inventory(db, item_id, adjustment.quantity, adjustment.unit_price, adjustment.notes)
        return {"message": "Stock added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{item_id}/transactions")
def get_item_transactions(item_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)):
    transactions = db.query(InventoryTransaction).filter(
        InventoryTransaction.item_id == item_id
    ).order_by(InventoryTransaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions
