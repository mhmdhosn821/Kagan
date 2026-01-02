from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.invoice import Invoice, InvoiceItem, InvoiceType, PaymentMethod
from app.models.product import BOMItem, RecipeItem
from app.services.auth import get_current_active_user
from app.services.inventory import deduct_inventory
from app.models.user import User

router = APIRouter(prefix="/invoices", tags=["Invoices"])


class InvoiceItemCreate(BaseModel):
    item_type: str  # service, product, retail
    service_id: int = None
    product_id: int = None
    inventory_item_id: int = None
    quantity: int = 1
    unit_price: float
    barber_id: int = None


class InvoiceCreate(BaseModel):
    customer_id: int = None
    invoice_type: InvoiceType
    items: List[InvoiceItemCreate]
    discount_amount: float = 0
    payment_method: PaymentMethod = PaymentMethod.CASH
    notes: str = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int = None
    invoice_type: InvoiceType
    created_by: int
    total_amount: float
    discount_amount: float
    final_amount: float
    payment_method: PaymentMethod
    paid: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/", response_model=InvoiceResponse)
def create_invoice(invoice_data: InvoiceCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)):
    # Generate invoice number
    last_invoice = db.query(Invoice).order_by(Invoice.id.desc()).first()
    invoice_number = f"INV-{(last_invoice.id + 1) if last_invoice else 1:06d}"
    
    # Calculate total
    total_amount = sum(item.unit_price * item.quantity for item in invoice_data.items)
    final_amount = total_amount - invoice_data.discount_amount
    
    # Create invoice
    new_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=invoice_data.customer_id,
        invoice_type=invoice_data.invoice_type,
        created_by=current_user.id,
        total_amount=total_amount,
        discount_amount=invoice_data.discount_amount,
        final_amount=final_amount,
        payment_method=invoice_data.payment_method,
        notes=invoice_data.notes
    )
    db.add(new_invoice)
    db.flush()
    
    # Add invoice items and deduct inventory
    for item_data in invoice_data.items:
        invoice_item = InvoiceItem(
            invoice_id=new_invoice.id,
            item_type=item_data.item_type,
            service_id=item_data.service_id,
            product_id=item_data.product_id,
            inventory_item_id=item_data.inventory_item_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_data.unit_price * item_data.quantity,
            barber_id=item_data.barber_id
        )
        db.add(invoice_item)
        
        # Deduct inventory based on item type
        try:
            if item_data.item_type == "service" and item_data.service_id:
                # Deduct BOM items for service
                bom_items = db.query(BOMItem).filter(BOMItem.service_id == item_data.service_id).all()
                for bom in bom_items:
                    deduct_inventory(db, bom.inventory_item_id, bom.quantity * item_data.quantity, 
                                   "invoice", new_invoice.id, f"Service: {item_data.service_id}")
            
            elif item_data.item_type == "product" and item_data.product_id:
                # Deduct recipe items for product
                recipe_items = db.query(RecipeItem).filter(RecipeItem.product_id == item_data.product_id).all()
                for recipe in recipe_items:
                    deduct_inventory(db, recipe.inventory_item_id, recipe.quantity * item_data.quantity,
                                   "invoice", new_invoice.id, f"Product: {item_data.product_id}")
            
            elif item_data.item_type == "retail" and item_data.inventory_item_id:
                # Deduct retail item directly
                deduct_inventory(db, item_data.inventory_item_id, item_data.quantity,
                               "invoice", new_invoice.id, "Retail sale")
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
    
    # Add loyalty points if customer exists
    if invoice_data.customer_id:
        from app.models.customer import Customer
        customer = db.query(Customer).filter(Customer.id == invoice_data.customer_id).first()
        if customer:
            # Add 1 point per 10,000 Rials spent
            points = int(final_amount / 10000)
            customer.loyalty_points += points
    
    db.commit()
    db.refresh(new_invoice)
    return new_invoice


@router.get("/", response_model=List[InvoiceResponse])
def get_invoices(skip: int = 0, limit: int = 50, invoice_type: InvoiceType = None,
                db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    query = db.query(Invoice)
    if invoice_type:
        query = query.filter(Invoice.invoice_type == invoice_type)
    return query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_active_user)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id == invoice_id).all()
    
    return {
        "invoice": invoice,
        "items": items
    }
