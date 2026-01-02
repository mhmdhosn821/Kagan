from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.service import Service, ServiceCategory
from app.models.booking import Booking, BookingStatus
from app.models.product import BOMItem
from app.models.user import User, UserRole
from app.services.auth import get_current_active_user

router = APIRouter(prefix="/barbershop", tags=["Barbershop"])


class ServiceCreate(BaseModel):
    name: str
    category: ServiceCategory
    price: float
    duration_minutes: int = 30
    description: Optional[str] = None


class ServiceResponse(BaseModel):
    id: int
    name: str
    category: ServiceCategory
    price: float
    duration_minutes: int
    description: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class BOMItemCreate(BaseModel):
    inventory_item_id: int
    quantity: float


class BookingCreate(BaseModel):
    customer_id: int
    barber_id: int
    service_id: int
    booking_datetime: datetime
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    id: int
    customer_id: int
    barber_id: int
    service_id: int
    booking_datetime: datetime
    status: BookingStatus
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


# Services endpoints
@router.post("/services", response_model=ServiceResponse)
def create_service(service: ServiceCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)):
    new_service = Service(**service.dict())
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service


@router.get("/services", response_model=List[ServiceResponse])
def get_services(category: ServiceCategory = None, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)):
    query = db.query(Service).filter(Service.is_active == True)
    if category:
        query = query.filter(Service.category == category)
    return query.all()


@router.get("/services/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_active_user)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/services/{service_id}/bom")
def add_bom_item(service_id: int, bom_item: BOMItemCreate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    new_bom = BOMItem(
        service_id=service_id,
        inventory_item_id=bom_item.inventory_item_id,
        quantity=bom_item.quantity
    )
    db.add(new_bom)
    db.commit()
    return {"message": "BOM item added successfully"}


@router.get("/services/{service_id}/bom")
def get_service_bom(service_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_active_user)):
    bom_items = db.query(BOMItem).filter(BOMItem.service_id == service_id).all()
    return bom_items


# Booking endpoints
@router.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)):
    new_booking = Booking(**booking.dict())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking


@router.get("/bookings", response_model=List[BookingResponse])
def get_bookings(barber_id: int = None, status: BookingStatus = None, 
                db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    query = db.query(Booking)
    if barber_id:
        query = query.filter(Booking.barber_id == barber_id)
    if status:
        query = query.filter(Booking.status == status)
    return query.order_by(Booking.booking_datetime.desc()).all()


@router.put("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, status: BookingStatus, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = status
    db.commit()
    return {"message": "Booking status updated"}


@router.get("/barbers")
def get_barbers(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    barbers = db.query(User).filter(
        User.role.in_([UserRole.BARBER, UserRole.ADMIN]),
        User.is_active == True
    ).all()
    return [{"id": b.id, "full_name": b.full_name, "commission_percentage": b.commission_percentage} for b in barbers]
