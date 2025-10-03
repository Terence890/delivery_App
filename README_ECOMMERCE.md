# ShopEase - Full-Stack E-Commerce Platform

A comprehensive e-commerce platform with **three separate Expo mobile apps** for customers, delivery agents, and administrators.

## 🏗️ Architecture

### Backend (FastAPI + MongoDB)
- **Authentication**: JWT-based with role-based access control
- **Database**: MongoDB with geospatial support for delivery zones
- **API**: RESTful API with `/api` prefix

### Frontend (3 Separate Expo Apps)
1. **Customer App**: Browse products, manage cart, place orders
2. **Delivery Agent App**: Accept orders, manage deliveries
3. **Admin Panel**: Manage products, orders, delivery zones

## 🚀 Getting Started

### Test Accounts

**Admin Account:**
- Email: `admin@shop.com`
- Password: `admin123`
- Role: Full access to manage products, orders, and delivery zones

**Customer Account:**
- Email: `customer@test.com`
- Password: `customer123`
- Role: Browse and purchase products

**Delivery Agent Account:**
- Email: `driver@test.com`
- Password: `driver123`
- Role: Accept and deliver orders

### URLs
- **Backend API**: `https://<your-preview-url>/api`
- **Frontend App**: Accessible via Expo Go QR code

## 📱 Features

### Customer App Features
- **Product Catalog**: Browse products with categories and search
- **Shopping Cart**: Add/remove items, adjust quantities
- **Checkout**: Place orders with delivery address
- **Order Tracking**: View order status in real-time
- **User Profile**: View and manage account details

### Delivery Agent App Features
- **Available Orders**: View confirmed orders ready for delivery
- **Accept Orders**: Accept delivery assignments
- **Active Deliveries**: Manage ongoing deliveries
- **Status Updates**: Update order status (preparing → out for delivery → delivered)
- **Delivery History**: View completed deliveries and earnings

### Admin Panel Features
- **Dashboard**: Overview stats (products, orders, customers, agents, revenue)
- **Product Management**: Create, edit, delete products with images
- **Order Management**: View all orders, update status
- **User Management**: View customers and delivery agents
- **Real-time Statistics**: Monitor platform performance

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `PUT /api/auth/profile` - Update profile

### Products
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create product (Admin only)
- `PUT /api/products/{id}` - Update product (Admin only)
- `DELETE /api/products/{id}` - Delete product (Admin only)
- `GET /api/categories` - List all categories

### Cart
- `GET /api/cart` - Get user's cart
- `POST /api/cart/add` - Add item to cart
- `POST /api/cart/update` - Update item quantity
- `POST /api/cart/remove/{product_id}` - Remove item
- `DELETE /api/cart/clear` - Clear cart

### Orders
- `POST /api/orders` - Create order from cart
- `GET /api/orders` - List orders (filtered by role)
- `GET /api/orders/{id}` - Get order details
- `PUT /api/orders/{id}/status` - Update order status
- `POST /api/orders/{id}/accept` - Accept order (Delivery agent)

### Delivery Zones
- `GET /api/delivery-zones` - List all zones
- `POST /api/delivery-zones` - Create zone (Admin only)
- `PUT /api/delivery-zones/{id}/assign-agent` - Assign agent to zone

### Admin
- `GET /api/admin/stats` - Get platform statistics

## 🎯 User Flows

### Customer Flow
1. **Register/Login** → Select "Customer" role
2. **Browse Products** → Search or filter by category
3. **Add to Cart** → Adjust quantities
4. **Checkout** → Enter delivery address
5. **Track Order** → Monitor status updates

### Delivery Agent Flow
1. **Register/Login** → Select "Delivery Agent" role
2. **View Available Orders** → See confirmed orders
3. **Accept Order** → Take delivery assignment
4. **Start Delivery** → Mark as "Out for Delivery"
5. **Complete** → Mark as "Delivered"

### Admin Flow
1. **Login** with admin credentials
2. **Add Products** → With images, prices, stock
3. **Monitor Orders** → Update status, manage flow
4. **View Statistics** → Track performance

## 🔐 Security Features
- **JWT Authentication**: Secure token-based auth
- **Role-Based Access Control**: Customer, Delivery Agent, Admin roles
- **Password Hashing**: bcrypt for secure password storage
- **Authorization Middleware**: Protected endpoints

## 📊 Database Schema

### Collections
- **users**: User accounts with roles
- **products**: Product catalog
- **carts**: Shopping carts
- **orders**: Order records
- **delivery_zones**: Geospatial delivery zones

## 🎨 UI/UX Highlights
- **Modern Design**: Clean, professional interface
- **Role-Based Navigation**: Different apps for different roles
- **Responsive**: Works on all mobile devices
- **Real-time Updates**: Live order status updates
- **Touch-Optimized**: 44px+ touch targets
- **Intuitive Navigation**: Bottom tabs for main screens

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- MongoDB (with motor async driver)
- JWT for authentication
- bcrypt for password hashing

**Frontend:**
- Expo (React Native)
- TypeScript
- Zustand (State management)
- Axios (API calls)
- AsyncStorage (Local storage)
- React Navigation (Routing)
- Expo Router (File-based routing)

## 📝 Environment Variables

**Backend (.env):**
```
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
JWT_SECRET=your-super-secret-jwt-key-change-in-production-2024
```

**Frontend (.env):**
```
EXPO_PUBLIC_BACKEND_URL=<your-backend-url>
EXPO_PACKAGER_PROXY_URL=<proxy-url>
EXPO_PACKAGER_HOSTNAME=<hostname>
```

## 🚦 Order Status Flow
1. **pending** → Initial state after order creation
2. **confirmed** → Admin/system confirms order
3. **preparing** → Delivery agent accepts order
4. **out_for_delivery** → Agent starts delivery
5. **delivered** → Order completed
6. **cancelled** → Order cancelled

## 📦 Image Handling
- Images stored as **base64** in MongoDB
- Supports image picker in admin panel
- SVG placeholders for testing

## 🎯 Future Enhancements
- Real-time location tracking for deliveries
- Push notifications for order updates
- Payment gateway integration (Stripe/PayPal)
- Product reviews and ratings
- Wishlist functionality
- Delivery zone visualization with maps
- Analytics dashboard
- Multi-language support

## 🐛 Known Issues
None at the moment! 🎉

## 📄 License
MIT License - Feel free to use this project for learning and development.

---

Built with ❤️ using Expo, FastAPI, and MongoDB
