"""
Auto-initialization module for Kagan ERP
Handles automatic setup of .env file and database initialization
"""
import os
import shutil
from pathlib import Path
from app.database import SessionLocal, engine, Base
from app.models import User, UserRole, Customer, InventoryItem, InventoryType, InventoryItemType, UnitType
from app.models import Service, ServiceCategory, Product, BOMItem, RecipeItem
from app.services.auth import get_password_hash


def setup_env_file():
    """Copy .env.example to .env if .env doesn't exist"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if not env_path.exists():
        if env_example_path.exists():
            shutil.copy(env_example_path, env_path)
            print("✅ فایل .env ساخته شد")
            return True
        else:
            print("⚠️  فایل .env.example یافت نشد")
            return False
    return False


def create_database_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ دیتابیس آماده است")


def is_database_empty():
    """Check if database is empty (no admin user exists)"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        return admin is None
    finally:
        db.close()


def seed_initial_data():
    """Seed database with initial users and sample data"""
    db = SessionLocal()
    
    try:
        # Check if already initialized
        if not is_database_empty():
            return
        
        # Create users
        admin = User(
            username="admin",
            email="admin@kagan.local",
            full_name="مدیر سیستم",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin)
        
        barber = User(
            username="barber1",
            email="barber@kagan.local",
            full_name="علی رضایی",
            hashed_password=get_password_hash("barber123"),
            role=UserRole.BARBER,
            commission_percentage=30
        )
        db.add(barber)
        
        barista = User(
            username="barista1",
            email="barista@kagan.local",
            full_name="سارا محمدی",
            hashed_password=get_password_hash("barista123"),
            role=UserRole.BARISTA
        )
        db.add(barista)
        
        # Sample customers
        customers = [
            Customer(full_name="محمد احمدی", phone="09123456789", loyalty_points=100),
            Customer(full_name="زهرا کریمی", phone="09124567890", loyalty_points=50),
        ]
        for customer in customers:
            db.add(customer)
        
        # Cafe inventory
        cafe_items = [
            InventoryItem(
                name="شیر",
                code="CAF-001",
                inventory_type=InventoryType.CAFE,
                item_type=InventoryItemType.RAW_MATERIAL,
                unit=UnitType.LITER,
                current_stock=10.0,
                min_stock_alert=2.0,
                unit_price=50000
            ),
            InventoryItem(
                name="قهوه اسپرسو",
                code="CAF-002",
                inventory_type=InventoryType.CAFE,
                item_type=InventoryItemType.RAW_MATERIAL,
                unit=UnitType.KG,
                current_stock=5.0,
                min_stock_alert=1.0,
                unit_price=800000
            ),
            InventoryItem(
                name="شکلات",
                code="CAF-003",
                inventory_type=InventoryType.CAFE,
                item_type=InventoryItemType.RAW_MATERIAL,
                unit=UnitType.KG,
                current_stock=3.0,
                min_stock_alert=0.5,
                unit_price=300000
            ),
        ]
        
        # Barbershop inventory
        barbershop_items = [
            InventoryItem(
                name="رنگ مو",
                code="BAR-001",
                inventory_type=InventoryType.BARBERSHOP,
                item_type=InventoryItemType.RAW_MATERIAL,
                unit=UnitType.ML,
                current_stock=1000.0,
                min_stock_alert=200.0,
                unit_price=500
            ),
            InventoryItem(
                name="اکسیدان",
                code="BAR-002",
                inventory_type=InventoryType.BARBERSHOP,
                item_type=InventoryItemType.RAW_MATERIAL,
                unit=UnitType.ML,
                current_stock=1500.0,
                min_stock_alert=300.0,
                unit_price=300
            ),
            InventoryItem(
                name="شامپو",
                code="BAR-003",
                inventory_type=InventoryType.BARBERSHOP,
                item_type=InventoryItemType.RAW_MATERIAL,
                unit=UnitType.ML,
                current_stock=2000.0,
                min_stock_alert=500.0,
                unit_price=200
            ),
            InventoryItem(
                name="واکس مو",
                code="BAR-004",
                inventory_type=InventoryType.BARBERSHOP,
                item_type=InventoryItemType.RETAIL_PRODUCT,
                unit=UnitType.PIECE,
                current_stock=20.0,
                min_stock_alert=5.0,
                unit_price=150000,
                retail_price=250000
            ),
        ]
        
        for item in cafe_items + barbershop_items:
            db.add(item)
        
        db.flush()  # Flush to get IDs
        
        # Barbershop services
        services = [
            Service(
                name="اصلاح صورت",
                category=ServiceCategory.HAIRCUT,
                price=100000,
                duration_minutes=30
            ),
            Service(
                name="کوتاهی مو",
                category=ServiceCategory.HAIRCUT,
                price=150000,
                duration_minutes=45
            ),
            Service(
                name="رنگ مو",
                category=ServiceCategory.COLORING,
                price=300000,
                duration_minutes=90
            ),
            Service(
                name="ماساژ صورت",
                category=ServiceCategory.MASSAGE,
                price=80000,
                duration_minutes=20
            ),
        ]
        
        for service in services:
            db.add(service)
        
        db.flush()  # Flush to get service IDs
        
        # Add BOM for coloring service
        coloring_service = db.query(Service).filter(Service.name == "رنگ مو").first()
        color_item = db.query(InventoryItem).filter(InventoryItem.code == "BAR-001").first()
        oxidant_item = db.query(InventoryItem).filter(InventoryItem.code == "BAR-002").first()
        
        if coloring_service and color_item and oxidant_item:
            db.add(BOMItem(service_id=coloring_service.id, inventory_item_id=color_item.id, quantity=50))
            db.add(BOMItem(service_id=coloring_service.id, inventory_item_id=oxidant_item.id, quantity=50))
        
        # Cafe products
        products = [
            Product(
                name="اسپرسو",
                code="PROD-001",
                price=30000,
                category="coffee"
            ),
            Product(
                name="کاپوچینو",
                code="PROD-002",
                price=50000,
                category="coffee"
            ),
            Product(
                name="هات چاکلت",
                code="PROD-003",
                price=60000,
                category="dessert"
            ),
        ]
        
        for product in products:
            db.add(product)
        
        db.flush()  # Flush to get product IDs
        
        # Add recipes
        cappuccino = db.query(Product).filter(Product.code == "PROD-002").first()
        milk_item = db.query(InventoryItem).filter(InventoryItem.code == "CAF-001").first()
        coffee_item = db.query(InventoryItem).filter(InventoryItem.code == "CAF-002").first()
        
        if cappuccino and milk_item and coffee_item:
            db.add(RecipeItem(product_id=cappuccino.id, inventory_item_id=milk_item.id, quantity=0.15))
            db.add(RecipeItem(product_id=cappuccino.id, inventory_item_id=coffee_item.id, quantity=0.02))
        
        db.commit()
        print("✅ دادههای اولیه اضافه شد")
        
    except Exception as e:
        print(f"❌ خطا در مقداردهی اولیه: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def auto_setup():
    """
    Main auto-setup function that:
    1. Creates .env file if needed
    2. Creates database tables
    3. Seeds initial data if database is empty
    """
    # Setup .env file
    setup_env_file()
    
    # Create database tables
    create_database_tables()
    
    # Seed initial data if database is empty
    if is_database_empty():
        seed_initial_data()
