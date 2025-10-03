# 🔐 Login Credentials for ShopEase E-Commerce App

## Test Accounts

### 👤 Customer Account
**Purpose:** Browse products, add to cart, place orders
- **Email:** `customer@test.com`
- **Password:** `customer123`
- **App Experience:** Customer Shopping App (Blue theme)

### 🚚 Delivery Agent Account  
**Purpose:** Accept and deliver orders
- **Email:** `driver@test.com`
- **Password:** `driver123`
- **App Experience:** Delivery Agent App (Green theme)

### 👨‍💼 Admin Account
**Purpose:** Manage products, orders, and platform
- **Email:** `admin@shop.com`
- **Password:** `admin123`
- **App Experience:** Admin Panel (Orange theme)

---

## 📝 Important Notes

1. **Case Sensitive:** Email addresses are NOT case-sensitive (converted to lowercase automatically)
2. **Password:** Passwords ARE case-sensitive - make sure to type exactly as shown
3. **Role Selection:** During registration, you can select your role (Customer/Delivery Agent/Admin)

## 🎯 Quick Test Flow

### For Customer:
1. Login with customer@test.com / customer123
2. You'll see the home screen with products
3. Browse products, add to cart, checkout

### For Delivery Agent:
1. Login with driver@test.com / driver123
2. You'll see available orders (if any have been confirmed)
3. Accept orders and manage deliveries

### For Admin:
1. Login with admin@shop.com / admin123
2. You'll see the dashboard with statistics
3. Manage products, view all orders, update statuses

## 🐛 Troubleshooting

**"Invalid email or password" error?**
- Double-check you're typing the password exactly as shown (case-sensitive)
- Make sure there are no extra spaces
- Try copy-pasting the credentials

**App not navigating after login?**
- Check the console logs for debugging info
- Make sure you have internet connection
- Try logging out and logging in again

**Backend not responding?**
- Backend is running on port 8001
- All test accounts are already created in the database
- No additional setup needed

---

## 🔄 Testing Different Roles

You can test all three different app experiences by:
1. Logging out from the current account
2. Logging in with a different role's credentials
3. The app will automatically route you to the appropriate interface based on your role

---

**Need to create a new account?**
Use the Register screen and select your desired role (Customer/Delivery Agent/Admin)
