#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for E-commerce Platform
Tests authentication, products, cart, orders, and admin functionality
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://ecozone-app.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

# Test accounts (as provided in review request)
TEST_ACCOUNTS = {
    "admin": {"email": "admin@shop.com", "password": "admin123"},
    "customer": {"email": "customer@test.com", "password": "customer123"},
    "delivery_agent": {"email": "driver@test.com", "password": "driver123"}
}

class APITester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.created_products = []
        self.test_orders = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, token: str = None) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{BASE_URL}{endpoint}"
        headers = HEADERS.copy()
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return False, {"error": "Invalid method"}, 400
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return response.status_code < 400, response_data, response.status_code
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0
    
    def test_authentication(self):
        """Test authentication for all user roles"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        for role, credentials in TEST_ACCOUNTS.items():
            # Test login
            success, data, status_code = self.make_request(
                "POST", "/auth/login", credentials
            )
            
            if success and "access_token" in data:
                self.tokens[role] = data["access_token"]
                user_info = data.get("user", {})
                expected_role = "delivery_agent" if role == "delivery_agent" else role
                
                if user_info.get("role") == expected_role:
                    self.log_result(f"Login {role}", True, f"Token received, role: {user_info.get('role')}")
                else:
                    self.log_result(f"Login {role}", False, f"Role mismatch: expected {expected_role}, got {user_info.get('role')}")
            else:
                self.log_result(f"Login {role}", False, f"Status: {status_code}, Response: {data}")
        
        # Test invalid credentials
        success, data, status_code = self.make_request(
            "POST", "/auth/login", {"email": "invalid@test.com", "password": "wrong"}
        )
        self.log_result("Invalid login rejection", not success and status_code == 401, 
                       f"Status: {status_code}")
        
        # Test /auth/me endpoint
        if "customer" in self.tokens:
            success, data, status_code = self.make_request(
                "GET", "/auth/me", token=self.tokens["customer"]
            )
            self.log_result("Get current user", success and data.get("email") == "customer@test.com",
                           f"Status: {status_code}, Email: {data.get('email')}")
    
    def test_products(self):
        """Test product endpoints"""
        print("\n=== TESTING PRODUCT ENDPOINTS ===")
        
        # Test get all products
        success, data, status_code = self.make_request("GET", "/products")
        products_exist = success and isinstance(data, list) and len(data) > 0
        self.log_result("Get all products", products_exist, 
                       f"Status: {status_code}, Products count: {len(data) if isinstance(data, list) else 0}")
        
        # Test get categories
        success, data, status_code = self.make_request("GET", "/categories")
        categories_exist = success and "categories" in data and len(data["categories"]) > 0
        self.log_result("Get categories", categories_exist,
                       f"Status: {status_code}, Categories: {data.get('categories', [])}")
        
        # Test get specific product (use first product if available)
        if products_exist and isinstance(data, list) and len(data) > 0:
            product_id = data[0].get("id")
            success, product_data, status_code = self.make_request("GET", f"/products/{product_id}")
            self.log_result("Get specific product", success and product_data.get("id") == product_id,
                           f"Status: {status_code}, Product: {product_data.get('name', 'N/A')}")
        
        # Test admin-only product creation
        if "admin" in self.tokens:
            new_product = {
                "name": "Test Product API",
                "description": "Created via API test",
                "price": 99.99,
                "category": "Test",
                "stock": 10,
                "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
            }
            
            success, data, status_code = self.make_request(
                "POST", "/products", new_product, self.tokens["admin"]
            )
            
            if success and data.get("id"):
                self.created_products.append(data["id"])
                self.log_result("Create product (admin)", True, f"Created product: {data.get('name')}")
                
                # Test update product
                update_data = {**new_product, "name": "Updated Test Product", "price": 149.99}
                success, updated_data, status_code = self.make_request(
                    "PUT", f"/products/{data['id']}", update_data, self.tokens["admin"]
                )
                self.log_result("Update product (admin)", success and updated_data.get("name") == "Updated Test Product",
                               f"Status: {status_code}, Updated name: {updated_data.get('name')}")
            else:
                self.log_result("Create product (admin)", False, f"Status: {status_code}, Response: {data}")
        
        # Test non-admin cannot create products
        if "customer" in self.tokens:
            success, data, status_code = self.make_request(
                "POST", "/products", {"name": "Unauthorized", "price": 1}, self.tokens["customer"]
            )
            self.log_result("Create product blocked (customer)", not success and status_code == 403,
                           f"Status: {status_code}")
    
    def test_cart_flow(self):
        """Test cart management"""
        print("\n=== TESTING CART MANAGEMENT ===")
        
        if "customer" not in self.tokens:
            self.log_result("Cart tests", False, "No customer token available")
            return
        
        customer_token = self.tokens["customer"]
        
        # Get initial cart (should be empty or create new)
        success, cart_data, status_code = self.make_request("GET", "/cart", token=customer_token)
        self.log_result("Get cart", success, f"Status: {status_code}, Items: {len(cart_data.get('items', []))}")
        
        # Clear cart first
        success, data, status_code = self.make_request("DELETE", "/cart/clear", token=customer_token)
        self.log_result("Clear cart", success, f"Status: {status_code}")
        
        # Get products to add to cart
        success, products, status_code = self.make_request("GET", "/products")
        if not success or not products or len(products) < 2:
            self.log_result("Cart tests", False, "Not enough products available for cart testing")
            return
        
        # Add first product to cart
        product1 = products[0]
        add_item1 = {"product_id": product1["id"], "quantity": 2}
        success, data, status_code = self.make_request("POST", "/cart/add", add_item1, token=customer_token)
        self.log_result("Add item to cart", success, f"Status: {status_code}, Product: {product1.get('name')}")
        
        # Add second product to cart
        product2 = products[1]
        add_item2 = {"product_id": product2["id"], "quantity": 1}
        success, data, status_code = self.make_request("POST", "/cart/add", add_item2, token=customer_token)
        self.log_result("Add second item to cart", success, f"Status: {status_code}, Product: {product2.get('name')}")
        
        # View cart with items
        success, cart_data, status_code = self.make_request("GET", "/cart", token=customer_token)
        cart_has_items = success and len(cart_data.get("items", [])) == 2
        self.log_result("View cart with items", cart_has_items, 
                       f"Status: {status_code}, Items count: {len(cart_data.get('items', []))}")
        
        # Update quantity of first item
        update_item = {"product_id": product1["id"], "quantity": 3}
        success, data, status_code = self.make_request("POST", "/cart/update", update_item, token=customer_token)
        self.log_result("Update cart item quantity", success, f"Status: {status_code}")
        
        # Remove second item
        success, data, status_code = self.make_request("POST", f"/cart/remove/{product2['id']}", token=customer_token)
        self.log_result("Remove item from cart", success, f"Status: {status_code}")
        
        # Verify cart has only one item
        success, cart_data, status_code = self.make_request("GET", "/cart", token=customer_token)
        one_item_left = success and len(cart_data.get("items", [])) == 1
        self.log_result("Cart after removal", one_item_left,
                       f"Status: {status_code}, Items count: {len(cart_data.get('items', []))}")
    
    def test_order_flow(self):
        """Test order creation and management"""
        print("\n=== TESTING ORDER MANAGEMENT ===")
        
        if "customer" not in self.tokens:
            self.log_result("Order tests", False, "No customer token available")
            return
        
        customer_token = self.tokens["customer"]
        
        # Prepare cart for order
        success, products, status_code = self.make_request("GET", "/products")
        if not success or not products:
            self.log_result("Order tests", False, "No products available for order testing")
            return
        
        # Clear and add items to cart
        self.make_request("DELETE", "/cart/clear", token=customer_token)
        
        # Add items to cart for order
        product = products[0]
        add_item = {"product_id": product["id"], "quantity": 1}
        success, data, status_code = self.make_request("POST", "/cart/add", add_item, token=customer_token)
        
        if not success:
            self.log_result("Order tests", False, "Failed to add items to cart for order")
            return
        
        # Create order
        order_data = {
            "items": [add_item],
            "delivery_address": "123 Test Street, Test City, 12345"
        }
        
        success, order_response, status_code = self.make_request("POST", "/orders", order_data, token=customer_token)
        
        if success and order_response.get("id"):
            order_id = order_response["id"]
            self.test_orders.append(order_id)
            self.log_result("Create order", True, f"Order ID: {order_id}, Total: ${order_response.get('total_amount', 0)}")
            
            # Verify cart is cleared after order
            success, cart_data, status_code = self.make_request("GET", "/cart", token=customer_token)
            cart_cleared = success and len(cart_data.get("items", [])) == 0
            self.log_result("Cart cleared after order", cart_cleared, f"Cart items: {len(cart_data.get('items', []))}")
            
            # Test get specific order
            success, order_details, status_code = self.make_request("GET", f"/orders/{order_id}", token=customer_token)
            self.log_result("Get order details", success and order_details.get("id") == order_id,
                           f"Status: {status_code}, Order status: {order_details.get('status')}")
            
        else:
            self.log_result("Create order", False, f"Status: {status_code}, Response: {order_response}")
        
        # Test get orders list
        success, orders_list, status_code = self.make_request("GET", "/orders", token=customer_token)
        has_orders = success and isinstance(orders_list, list) and len(orders_list) > 0
        self.log_result("Get customer orders", has_orders,
                       f"Status: {status_code}, Orders count: {len(orders_list) if isinstance(orders_list, list) else 0}")
        
        # Test empty cart order creation
        self.make_request("DELETE", "/cart/clear", token=customer_token)
        empty_order_data = {
            "items": [],
            "delivery_address": "123 Test Street"
        }
        success, data, status_code = self.make_request("POST", "/orders", empty_order_data, token=customer_token)
        self.log_result("Empty cart order rejection", not success and status_code == 400,
                       f"Status: {status_code}")
    
    def test_delivery_agent_flow(self):
        """Test delivery agent functionality"""
        print("\n=== TESTING DELIVERY AGENT FLOW ===")
        
        if "delivery_agent" not in self.tokens:
            self.log_result("Delivery agent tests", False, "No delivery agent token available")
            return
        
        agent_token = self.tokens["delivery_agent"]
        
        # Get available orders (should see confirmed orders)
        success, orders, status_code = self.make_request("GET", "/orders", token=agent_token)
        self.log_result("Get available orders (delivery agent)", success,
                       f"Status: {status_code}, Orders count: {len(orders) if isinstance(orders, list) else 0}")
        
        # If we have test orders, try to accept one
        if self.test_orders and "admin" in self.tokens:
            order_id = self.test_orders[0]
            
            # First, admin confirms the order
            status_update = {"status": "confirmed"}
            success, data, status_code = self.make_request(
                "PUT", f"/orders/{order_id}/status", status_update, self.tokens["admin"]
            )
            self.log_result("Admin confirm order", success, f"Status: {status_code}")
            
            # Delivery agent accepts order
            success, data, status_code = self.make_request("POST", f"/orders/{order_id}/accept", token=agent_token)
            self.log_result("Accept order (delivery agent)", success, f"Status: {status_code}")
            
            if success:
                # Update order status to out_for_delivery
                status_update = {"status": "out_for_delivery"}
                success, data, status_code = self.make_request(
                    "PUT", f"/orders/{order_id}/status", status_update, agent_token
                )
                self.log_result("Update to out_for_delivery", success, f"Status: {status_code}")
                
                # Update order status to delivered
                status_update = {"status": "delivered"}
                success, data, status_code = self.make_request(
                    "PUT", f"/orders/{order_id}/status", status_update, agent_token
                )
                self.log_result("Update to delivered", success, f"Status: {status_code}")
    
    def test_admin_functionality(self):
        """Test admin-specific functionality"""
        print("\n=== TESTING ADMIN FUNCTIONALITY ===")
        
        if "admin" not in self.tokens:
            self.log_result("Admin tests", False, "No admin token available")
            return
        
        admin_token = self.tokens["admin"]
        
        # Test admin statistics
        success, stats, status_code = self.make_request("GET", "/admin/stats", token=admin_token)
        has_stats = success and all(key in stats for key in ["total_products", "total_orders", "total_customers"])
        self.log_result("Get admin statistics", has_stats,
                       f"Status: {status_code}, Products: {stats.get('total_products', 0)}, Orders: {stats.get('total_orders', 0)}")
        
        # Test get all orders (admin view)
        success, all_orders, status_code = self.make_request("GET", "/orders", token=admin_token)
        self.log_result("Get all orders (admin)", success,
                       f"Status: {status_code}, Orders count: {len(all_orders) if isinstance(all_orders, list) else 0}")
        
        # Test non-admin cannot access admin stats
        if "customer" in self.tokens:
            success, data, status_code = self.make_request("GET", "/admin/stats", token=self.tokens["customer"])
            self.log_result("Admin stats blocked (customer)", not success and status_code == 403,
                           f"Status: {status_code}")
    
    def test_error_cases(self):
        """Test various error scenarios"""
        print("\n=== TESTING ERROR CASES ===")
        
        # Test accessing protected endpoint without token
        success, data, status_code = self.make_request("GET", "/cart")
        self.log_result("Protected endpoint without token", not success and status_code == 401,
                       f"Status: {status_code}")
        
        # Test invalid product ID
        success, data, status_code = self.make_request("GET", "/products/invalid-id")
        self.log_result("Invalid product ID", not success and status_code == 404,
                       f"Status: {status_code}")
        
        # Test invalid order ID
        if "customer" in self.tokens:
            success, data, status_code = self.make_request("GET", "/orders/invalid-id", token=self.tokens["customer"])
            self.log_result("Invalid order ID", not success and status_code == 404,
                           f"Status: {status_code}")
    
    def cleanup(self):
        """Clean up test data"""
        print("\n=== CLEANUP ===")
        
        if "admin" in self.tokens and self.created_products:
            for product_id in self.created_products:
                success, data, status_code = self.make_request(
                    "DELETE", f"/products/{product_id}", token=self.tokens["admin"]
                )
                self.log_result(f"Delete test product {product_id}", success, f"Status: {status_code}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting E-commerce Backend API Tests")
        print(f"Base URL: {BASE_URL}")
        
        # Run tests in order
        self.test_authentication()
        self.test_products()
        self.test_cart_flow()
        self.test_order_flow()
        self.test_delivery_agent_flow()
        self.test_admin_functionality()
        self.test_error_cases()
        self.cleanup()
        
        # Summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)