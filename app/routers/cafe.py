from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.product import Product, RecipeItem
from app.services.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/cafe", tags=["Cafe"])


class ProductCreate(BaseModel):
    name: str
    code: str
    price: float
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    code: str
    price: float
    category: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class RecipeItemCreate(BaseModel):
    inventory_item_id: int
    quantity: float


@router.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_active_user)):
    # Check if code already exists
    if db.query(Product).filter(Product.code == product.code).first():
        raise HTTPException(status_code=400, detail="Product code already exists")
    
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/products", response_model=List[ProductResponse])
def get_products(category: str = None, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_active_user)):
    query = db.query(Product).filter(Product.is_active == True)
    if category:
        query = query.filter(Product.category == category)
    return query.all()


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_active_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products/{product_id}/recipe")
def add_recipe_item(product_id: int, recipe_item: RecipeItemCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_active_user)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_recipe = RecipeItem(
        product_id=product_id,
        inventory_item_id=recipe_item.inventory_item_id,
        quantity=recipe_item.quantity
    )
    db.add(new_recipe)
    db.commit()
    return {"message": "Recipe item added successfully"}


@router.get("/products/{product_id}/recipe")
def get_product_recipe(product_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_active_user)):
    recipe_items = db.query(RecipeItem).filter(RecipeItem.product_id == product_id).all()
    return recipe_items


@router.get("/menu")
def get_menu(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """Get categorized menu for POS"""
    products = db.query(Product).filter(Product.is_active == True).all()
    
    menu = {}
    for product in products:
        category = product.category or "Other"
        if category not in menu:
            menu[category] = []
        menu[category].append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image_url": product.image_url
        })
    
    return menu
