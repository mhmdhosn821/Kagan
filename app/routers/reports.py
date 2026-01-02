from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.database import get_db
from app.models.invoice import Invoice, InvoiceItem, InvoiceType
from app.models.inventory import InventoryTransaction
from app.models.user import User, UserRole
from app.services.auth import get_current_active_user
from app.services.inventory import get_inventory_value

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get dashboard summary"""
    today = datetime.utcnow().date()
    
    # Today's sales
    today_sales = db.query(func.sum(Invoice.final_amount)).filter(
        func.date(Invoice.created_at) == today
    ).scalar() or 0
    
    # This month's sales
    month_start = today.replace(day=1)
    month_sales = db.query(func.sum(Invoice.final_amount)).filter(
        Invoice.created_at >= month_start
    ).scalar() or 0
    
    # Total invoices today
    today_invoices = db.query(func.count(Invoice.id)).filter(
        func.date(Invoice.created_at) == today
    ).scalar() or 0
    
    # Inventory value
    inventory_value = get_inventory_value(db)
    
    return {
        "today_sales": today_sales,
        "month_sales": month_sales,
        "today_invoices": today_invoices,
        "inventory_value": inventory_value
    }


@router.get("/sales")
def get_sales_report(start_date: str = None, end_date: str = None, 
                    invoice_type: InvoiceType = None, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)):
    """Get sales report for a date range"""
    query = db.query(Invoice)
    
    if start_date:
        query = query.filter(Invoice.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Invoice.created_at <= datetime.fromisoformat(end_date))
    if invoice_type:
        query = query.filter(Invoice.invoice_type == invoice_type)
    
    invoices = query.all()
    
    total_sales = sum(inv.final_amount for inv in invoices)
    total_discount = sum(inv.discount_amount for inv in invoices)
    invoice_count = len(invoices)
    
    return {
        "invoices": invoices,
        "total_sales": total_sales,
        "total_discount": total_discount,
        "invoice_count": invoice_count
    }


@router.get("/commission")
def get_commission_report(barber_id: int = None, start_date: str = None, end_date: str = None,
                         db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get commission report for barbers"""
    query = db.query(InvoiceItem).join(Invoice)
    
    if barber_id:
        query = query.filter(InvoiceItem.barber_id == barber_id)
    if start_date:
        query = query.filter(Invoice.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Invoice.created_at <= datetime.fromisoformat(end_date))
    
    items = query.filter(InvoiceItem.barber_id.isnot(None)).all()
    
    # Calculate commission by barber
    commission_by_barber = {}
    for item in items:
        barber = db.query(User).filter(User.id == item.barber_id).first()
        if barber and barber.commission_percentage:
            if item.barber_id not in commission_by_barber:
                commission_by_barber[item.barber_id] = {
                    "barber_name": barber.full_name,
                    "commission_percentage": barber.commission_percentage,
                    "total_sales": 0,
                    "commission_amount": 0
                }
            
            total_price = item.total_price
            commission = total_price * (barber.commission_percentage / 100)
            commission_by_barber[item.barber_id]["total_sales"] += total_price
            commission_by_barber[item.barber_id]["commission_amount"] += commission
    
    return {"commissions": list(commission_by_barber.values())}


@router.get("/inventory-usage")
def get_inventory_usage_report(start_date: str = None, end_date: str = None,
                               db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get inventory usage report"""
    query = db.query(InventoryTransaction).filter(
        InventoryTransaction.transaction_type == "usage"
    )
    
    if start_date:
        query = query.filter(InventoryTransaction.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(InventoryTransaction.created_at <= datetime.fromisoformat(end_date))
    
    transactions = query.all()
    
    # Group by item
    usage_by_item = {}
    for trans in transactions:
        if trans.item_id not in usage_by_item:
            usage_by_item[trans.item_id] = {
                "item_name": trans.item.name,
                "total_quantity": 0,
                "total_cost": 0
            }
        usage_by_item[trans.item_id]["total_quantity"] += abs(trans.quantity)
        usage_by_item[trans.item_id]["total_cost"] += abs(trans.quantity) * trans.unit_price
    
    return {"usage": list(usage_by_item.values())}


@router.get("/profit")
def get_profit_report(start_date: str = None, end_date: str = None,
                     db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get profit report"""
    # Get sales
    sales_query = db.query(func.sum(Invoice.final_amount))
    
    if start_date:
        sales_query = sales_query.filter(Invoice.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        sales_query = sales_query.filter(Invoice.created_at <= datetime.fromisoformat(end_date))
    
    total_sales = sales_query.scalar() or 0
    
    # Get costs (inventory usage)
    cost_query = db.query(
        func.sum(InventoryTransaction.quantity * InventoryTransaction.unit_price)
    ).filter(InventoryTransaction.transaction_type == "usage")
    
    if start_date:
        cost_query = cost_query.filter(InventoryTransaction.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        cost_query = cost_query.filter(InventoryTransaction.created_at <= datetime.fromisoformat(end_date))
    
    total_cost = abs(cost_query.scalar() or 0)
    
    # Calculate profit
    gross_profit = total_sales - total_cost
    profit_margin = (gross_profit / total_sales * 100) if total_sales > 0 else 0
    
    return {
        "total_sales": total_sales,
        "total_cost": total_cost,
        "gross_profit": gross_profit,
        "profit_margin": profit_margin
    }
