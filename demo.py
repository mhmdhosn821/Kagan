#!/usr/bin/env python
"""
Demo script for Kagan ERP System
Shows how to create an invoice with automatic inventory deduction
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def login():
    """Login and get token"""
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = response.json()["access_token"]
    print(f"✅ Logged in as admin\n")
    return token

def show_inventory(token):
    """Show current inventory"""
    print("📦 Current Inventory Status:")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/inventory/", headers=headers)
    items = response.json()
    
    for item in items:
        print(f"  {item['name']}: {item['current_stock']} {item['unit']} (Alert: {item['min_stock_alert']})")
    print()

def create_cafe_invoice(token):
    """Create a cafe invoice"""
    print("☕ Creating Cafe Invoice...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get first customer
    customers = requests.get(f"{BASE_URL}/customers/", headers=headers).json()
    customer_id = customers[0]["id"]
    
    # Get cappuccino product
    products = requests.get(f"{BASE_URL}/cafe/products", headers=headers).json()
    cappuccino = next(p for p in products if "کاپوچینو" in p["name"])
    
    invoice_data = {
        "customer_id": customer_id,
        "invoice_type": "cafe",
        "items": [
            {
                "item_type": "product",
                "product_id": cappuccino["id"],
                "quantity": 2,
                "unit_price": cappuccino["price"]
            }
        ],
        "discount_amount": 0,
        "payment_method": "cash"
    }
    
    response = requests.post(f"{BASE_URL}/invoices/", headers=headers, json=invoice_data)
    invoice = response.json()
    
    print(f"  Invoice #{invoice['invoice_number']} created")
    print(f"  Total: {invoice['final_amount']:,.0f} Rials")
    print(f"  Items: 2x کاپوچینو")
    print(f"  ✅ Inventory automatically deducted\n")

def create_barbershop_invoice(token):
    """Create a barbershop invoice"""
    print("✂️ Creating Barbershop Invoice...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get second customer
    customers = requests.get(f"{BASE_URL}/customers/", headers=headers).json()
    customer_id = customers[1]["id"]
    
    # Get coloring service
    services = requests.get(f"{BASE_URL}/barbershop/services", headers=headers).json()
    coloring = next(s for s in services if "رنگ" in s["name"])
    
    # Get barber
    barbers = requests.get(f"{BASE_URL}/barbershop/barbers", headers=headers).json()
    barber_id = barbers[0]["id"]
    
    invoice_data = {
        "customer_id": customer_id,
        "invoice_type": "barbershop",
        "items": [
            {
                "item_type": "service",
                "service_id": coloring["id"],
                "quantity": 1,
                "unit_price": coloring["price"],
                "barber_id": barber_id
            }
        ],
        "discount_amount": 0,
        "payment_method": "card"
    }
    
    response = requests.post(f"{BASE_URL}/invoices/", headers=headers, json=invoice_data)
    invoice = response.json()
    
    print(f"  Invoice #{invoice['invoice_number']} created")
    print(f"  Total: {invoice['final_amount']:,.0f} Rials")
    print(f"  Service: رنگ مو")
    print(f"  ✅ Materials automatically deducted (50ml رنگ + 50ml اکسیدان)\n")

def show_dashboard(token):
    """Show dashboard summary"""
    print("📊 Dashboard Summary:")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reports/dashboard", headers=headers)
    data = response.json()
    
    print(f"  Today's Sales: {data['today_sales']:,.0f} Rials")
    print(f"  Today's Invoices: {data['today_invoices']}")
    print(f"  Inventory Value: {data['inventory_value']:,.0f} Rials")
    print()

def show_commission_report(token):
    """Show commission report"""
    print("💰 Commission Report:")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reports/commission", headers=headers)
    data = response.json()
    
    for commission in data["commissions"]:
        print(f"  {commission['barber_name']}: {commission['commission_amount']:,.0f} Rials ({commission['commission_percentage']}%)")
        print(f"    Total Sales: {commission['total_sales']:,.0f} Rials")
    print()

def main():
    print("=" * 60)
    print("KAGAN ERP SYSTEM DEMO")
    print("=" * 60)
    print()
    
    try:
        token = login()
        
        print("BEFORE TRANSACTIONS:")
        print("-" * 60)
        show_inventory(token)
        show_dashboard(token)
        
        print("CREATING TRANSACTIONS:")
        print("-" * 60)
        create_cafe_invoice(token)
        create_barbershop_invoice(token)
        
        print("AFTER TRANSACTIONS:")
        print("-" * 60)
        show_inventory(token)
        show_dashboard(token)
        show_commission_report(token)
        
        print("=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ DEMO FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
