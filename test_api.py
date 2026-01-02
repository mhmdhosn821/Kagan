#!/usr/bin/env python
"""
Test script for Kagan ERP API endpoints
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
    assert response.status_code == 200
    print("  ✅ Health check passed\n")

def test_login():
    """Test login and return token"""
    print("Testing authentication...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    print(f"  Status: {response.status_code}")
    data = response.json()
    print(f"  User: {data['username']} ({data['role']})")
    assert response.status_code == 200
    assert "access_token" in data
    print("  ✅ Authentication passed\n")
    return data["access_token"]

def test_customers(token):
    """Test customer endpoints"""
    print("Testing customer endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get customers
    response = requests.get(f"{BASE_URL}/customers/", headers=headers)
    print(f"  Get customers - Status: {response.status_code}")
    customers = response.json()
    print(f"  Found {len(customers)} customers")
    assert response.status_code == 200
    print("  ✅ Customer endpoints passed\n")

def test_inventory(token):
    """Test inventory endpoints"""
    print("Testing inventory endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get inventory items
    response = requests.get(f"{BASE_URL}/inventory/", headers=headers)
    print(f"  Get inventory - Status: {response.status_code}")
    items = response.json()
    print(f"  Found {len(items)} inventory items")
    
    # Get alerts
    response = requests.get(f"{BASE_URL}/inventory/alerts", headers=headers)
    print(f"  Get alerts - Status: {response.status_code}")
    alerts = response.json()
    print(f"  Found {alerts['count']} alerts")
    
    # Get inventory value
    response = requests.get(f"{BASE_URL}/inventory/value", headers=headers)
    print(f"  Get inventory value - Status: {response.status_code}")
    value = response.json()
    print(f"  Total inventory value: {value['total_value']:,.0f} Rials")
    
    assert response.status_code == 200
    print("  ✅ Inventory endpoints passed\n")

def test_barbershop(token):
    """Test barbershop endpoints"""
    print("Testing barbershop endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get services
    response = requests.get(f"{BASE_URL}/barbershop/services", headers=headers)
    print(f"  Get services - Status: {response.status_code}")
    services = response.json()
    print(f"  Found {len(services)} services")
    for service in services[:3]:
        print(f"    - {service['name']}: {service['price']:,.0f} Rials")
    
    # Get barbers
    response = requests.get(f"{BASE_URL}/barbershop/barbers", headers=headers)
    print(f"  Get barbers - Status: {response.status_code}")
    barbers = response.json()
    print(f"  Found {len(barbers)} barbers")
    
    assert response.status_code == 200
    print("  ✅ Barbershop endpoints passed\n")

def test_cafe(token):
    """Test cafe endpoints"""
    print("Testing cafe endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get products
    response = requests.get(f"{BASE_URL}/cafe/products", headers=headers)
    print(f"  Get products - Status: {response.status_code}")
    products = response.json()
    print(f"  Found {len(products)} products")
    for product in products:
        print(f"    - {product['name']}: {product['price']:,.0f} Rials")
    
    # Get menu
    response = requests.get(f"{BASE_URL}/cafe/menu", headers=headers)
    print(f"  Get menu - Status: {response.status_code}")
    menu = response.json()
    print(f"  Menu has {len(menu)} categories")
    
    assert response.status_code == 200
    print("  ✅ Cafe endpoints passed\n")

def test_reports(token):
    """Test reports endpoints"""
    print("Testing reports endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get dashboard
    response = requests.get(f"{BASE_URL}/reports/dashboard", headers=headers)
    print(f"  Get dashboard - Status: {response.status_code}")
    dashboard = response.json()
    print(f"  Today's sales: {dashboard['today_sales']:,.0f} Rials")
    print(f"  Month sales: {dashboard['month_sales']:,.0f} Rials")
    print(f"  Today's invoices: {dashboard['today_invoices']}")
    print(f"  Inventory value: {dashboard['inventory_value']:,.0f} Rials")
    
    assert response.status_code == 200
    print("  ✅ Reports endpoints passed\n")

def main():
    """Run all tests"""
    print("=" * 60)
    print("KAGAN ERP API TEST SUITE")
    print("=" * 60)
    print()
    
    try:
        test_health()
        token = test_login()
        test_customers(token)
        test_inventory(token)
        test_barbershop(token)
        test_cafe(token)
        test_reports(token)
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
