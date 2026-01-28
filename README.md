# Delivery App

A comprehensive full-stack delivery application that revolutionizes the delivery ecosystem by seamlessly connecting customers, delivery agents, and administrators. Built with modern technologies, this platform features a high-performance backend API powered by FastAPI and three separate, role-specific mobile applications developed using React Native (Expo).


## Architecture Overview

The Delivery App follows a modern microservices-inspired architecture with clear separation of concerns:

## Screenshots

Get a visual preview of the Delivery App across different user roles and features.

### Authentication

<table>
  <tr>
    <td width="50%">
      <h4>Login Screen</h4>
      <img src="Screenshot/Login.jpg" alt="Login Screen" width="100%"/>
      <p><em>Secure login interface with role-based authentication for customers, delivery agents, and administrators.</em></p>
    </td>
    <td width="50%">
      <h4>Registration Screen</h4>
      <img src="Screenshot/Register.jpg" alt="Registration Screen" width="100%"/>
      <p><em>User registration with comprehensive form validation and role selection.</em></p>
    </td>
  </tr>
</table>

### Customer Application

<table>
  <tr>
    <td width="50%">
      <h4>Home Page</h4>
      <img src="Screenshot/Customer_Home_page.jpg" alt="Customer Home Page" width="100%"/>
      <p><em>Browse products with intuitive categorization, search functionality, and product details.</em></p>
    </td>
    <td width="50%">
      <h4>Shopping Cart</h4>
      <img src="Screenshot/Customer_Cart_Page.jpg" alt="Customer Cart Page" width="100%"/>
      <p><em>Review cart items, adjust quantities, and proceed to checkout seamlessly.</em></p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h4>Orders Page</h4>
      <img src="Screenshot/Customer_Order_page.jpg" alt="Customer Orders Page" width="100%"/>
      <p><em>Track order history, view order status, and manage deliveries in real-time.</em></p>
    </td>
    <td width="50%">
      <h4>Profile Page</h4>
      <img src="Screenshot/Customer_Profile_Page.jpg" alt="Customer Profile Page" width="100%"/>
      <p><em>Manage personal information, delivery addresses, and account settings.</em></p>
    </td>
  </tr>
</table>

### Delivery Agent Application

<table>
  <tr>
    <td width="50%">
      <h4>Available Deliveries</h4>
      <img src="Screenshot/Driver_Available_Page.jpg" alt="Delivery Agent Available Deliveries" width="100%"/>
      <p><em>View available delivery requests with location details and accept orders efficiently.</em></p>
    </td>
    <td width="50%">
      <h4>Active Deliveries</h4>
      <img src="Screenshot/Active_Page.jpg" alt="Active Deliveries Page" width="100%"/>
      <p><em>Manage ongoing deliveries, update delivery status, and track delivery progress.</em></p>
    </td>
  </tr>
</table>

### Admin Application

<table>
  <tr>
    <td width="50%">
      <h4>Dashboard</h4>
      <img src="Screenshot/Admin_dashboard.jpg" alt="Admin Dashboard" width="100%"/>
      <p><em>Comprehensive dashboard with key metrics, statistics, and system overview for administrators.</em></p>
    </td>
    <td width="50%">
      <h4>Product Management</h4>
      <img src="Screenshot/Admin_product_page.jpg" alt="Admin Product Page" width="100%"/>
      <p><em>Manage product catalog, add new items, update pricing, and control inventory.</em></p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h4>Order Management</h4>
      <img src="Screenshot/Admin_order_page.jpg" alt="Admin Order Page" width="100%"/>
      <p><em>Monitor and manage all orders, track delivery status, and handle order operations.</em></p>
    </td>
    <td width="50%">
      <h4>Profile Settings</h4>
      <img src="Screenshot/Admin_profile_page.jpg" alt="Admin Profile Page" width="100%"/>
      <p><em>Manage administrator profile, system settings, and account preferences.</em></p>
    </td>
  </tr>
</table>

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ and pip
- Node.js (LTS) and npm/yarn
- MongoDB instance
- Expo Go app on your mobile device

### 1. Clone the Repository
```bash
git clone <repository-url>
cd delivery_App
```

### 2. Backend Setup (5 minutes)
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Edit with your MongoDB URL

# Run the server
uvicorn server:app --reload
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup (5 minutes)
```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install  # or yarn install

# Configure environment
echo "EXPO_PUBLIC_API_URL=http://YOUR_IP_ADDRESS:8000" > .env

# Start Expo
npm start  # or yarn start
```

### 4. Test the App
1. Scan the QR code with Expo Go app
2. Use test credentials:
   - **Customer**: customer@test.com / customer123
   - **Admin**: admin@shop.com / admin123
   - **Driver**: driver@test.com / driver123

### 5. Verify Everything Works
- ✅ Browse products as customer
- ✅ Add items to cart
- ✅ Create products as admin
- ✅ View orders as delivery agent

## Features

### Core Features

#### 🔐 Authentication & Security
- **Multi-Role Authentication**: Secure JWT-based login system supporting three user roles
- **Password Security**: Bcrypt hashing for password protection
- **Token Management**: 30-day token expiry with automatic refresh handling
- **Role-Based Access Control**: Granular permissions for each user type
- **Secure API Endpoints**: Protected routes with role validation

#### 🛍️ Customer Features
- **Product Browsing**: 
  - Category-based filtering (drinks, snacks, dairy, sweets, oils, enterprise)
  - Search functionality across product names and descriptions
  - Paginated product listing for performance
  - Real-time stock status indicators
- **Shopping Cart Management**:
  - Add/remove products with quantity control
  - Persistent cart across sessions
  - Real-time price calculations
  - Stock validation before checkout
- **Order Placement**:
  - Streamlined checkout process
  - Delivery address specification
  - Order history with status tracking
  - Order timeline visualization

#### 🚚 Delivery Agent Features
- **Order Management**:
  - View available orders in real-time
  - Accept order functionality
  - Status updates (preparing → out for delivery → delivered)
  - Delivery history tracking
- **Route Optimization**:
  - OSRM integration for optimal routing
  - Multi-waypoint route planning
  - Turn-by-turn navigation support
  - Delivery zone awareness

#### 👨‍💼 Admin Features
- **Product Management**:
  - Complete CRUD operations
  - Image upload with base64 conversion
  - Bulk product import via CSV
  - Inventory tracking and alerts
  - Category management
- **Order Oversight**:
  - View all system orders
  - Manual status updates
  - Order assignment to agents
  - Revenue tracking
- **Delivery Zone Management**:
  - Create geographical delivery zones
  - Polygon-based zone definition
  - Agent assignment to zones
  - Zone performance analytics
- **Analytics Dashboard**:
  - Real-time statistics
  - Total products, orders, customers, agents
  - Revenue calculations
  - Performance metrics

### Technical Features

- **Asynchronous Operations**: Non-blocking API calls for better performance
- **Real-time Stock Management**: Automatic inventory updates on order placement
- **Responsive Design**: Optimized for various mobile screen sizes
- **Error Handling**: Comprehensive error messages and fallback mechanisms
- **Data Validation**: Input validation at both frontend and backend
- **Image Optimization**: Base64 encoding for simplified image handling
- **Geospatial Support**: MongoDB geospatial queries for zone management

## Tech Stack

### Backend

The backend is built with Python using the FastAPI framework, providing a high-performance and easy-to-use API.

- **Framework**: FastAPI
- **Database**: MongoDB (via Motor - an asynchronous driver)
- **Authentication**: JWT (JSON Web Tokens) for secure API access, bcrypt for password hashing.
- **Routing**: OSRM (Open Source Routing Machine) for route optimization.
- **Environment Management**: `python-dotenv`
- **HTTP Client**: `httpx` for asynchronous HTTP requests.
- **Other Libraries**:
  - `pydantic`: Data validation and settings management.
  - `uvicorn`: ASGI server for running FastAPI.
  - `python-jose`: JWT implementation.
  - `Pillow`: Image processing (for bulk upload script).
  - `pandas`: Data manipulation (for bulk upload script).

### Frontend

The frontend is a cross-platform mobile application developed with React Native using the Expo framework.

- **Framework**: React Native (Expo)
- **Navigation**: Expo Router, React Navigation
- **State Management**: Zustand (for `authStore`)
- **HTTP Client**: Axios
- **UI Components**: `@expo/vector-icons`, `react-native-maps`
- **Utilities**:
  - `expo-location`: For location services.
  - `expo-image-picker`: For image selection.
  - `date-fns`: Date utility library.
  - `react-hook-form`: Form management.
  - `react-native-safe-area-context`: For handling safe areas on different devices.

## System Architecture

### Backend Architecture

The backend follows a modular design pattern with clear separation of concerns:

#### API Structure

```python
# Main Application Structure
app = FastAPI()
├── Authentication Module
│   ├── /auth/register
│   ├── /auth/login
│   └── /auth/me
├── Product Module
│   ├── GET /products
│   ├── GET /products/{id}
│   ├── POST /products (Admin)
│   ├── PUT /products/{id} (Admin)
│   ├── DELETE /products/{id} (Admin)
│   └── GET /categories
├── Cart Module
│   ├── GET /cart
│   ├── POST /cart/add
│   ├── POST /cart/update
│   ├── POST /cart/remove/{id}
│   └── DELETE /cart/clear
├── Order Module
│   ├── POST /orders
│   ├── GET /orders
│   ├── GET /orders/{id}
│   ├── PUT /orders/{id}/status
│   └── POST /orders/{id}/accept
├── Delivery Zone Module
│   ├── GET /delivery-zones
│   ├── POST /delivery-zones (Admin)
│   └── PUT /delivery-zones/{id}/assign-agent (Admin)
├── Routing Module
│   └── POST /route/optimize
└── Admin Module
    └── GET /admin/stats (Admin)
```

#### Security Implementation

1. **Authentication Flow**:
   ```python
   # JWT Token Structure
   {
     "sub": "user_id",
     "role": "customer|delivery_agent|admin",
     "exp": "timestamp"
   }
   ```

2. **Password Hashing**:
   - Bcrypt with automatic salt generation
   - Cost factor optimized for security/performance balance

3. **Role-Based Middleware**:
   ```python
   @Depends(require_role([UserRole.ADMIN]))
   ```

#### Data Models

**User Model**:
```python
{
  "id": "uuid",
  "email": "string",
  "password": "hashed_string",
  "name": "string",
  "role": "customer|delivery_agent|admin",
  "phone": "string (optional)",
  "address": "string (optional)",
  "delivery_zone_id": "string (optional)",
  "created_at": "datetime"
}
```

**Product Model**:
```python
{
  "id": "uuid",
  "name": "string",
  "brand": "string",
  "description": "string",
  "price": "float",
  "category": "string",
  "stock": "integer",
  "unit": "string",
  "variant": "string",
  "code": "string (optional)",
  "barcode": "string (optional)",
  "image": "base64_string",
  "created_at": "datetime"
}
```

**Order Model**:
```python
{
  "id": "uuid",
  "user_id": "string",
  "user_name": "string",
  "user_phone": "string",
  "user_address": "string",
  "items": [
    {
      "product_id": "string",
      "product_name": "string",
      "quantity": "integer",
      "price": "float"
    }
  ],
  "total_amount": "float",
  "status": "pending|confirmed|preparing|out_for_delivery|delivered|cancelled",
  "delivery_agent_id": "string (optional)",
  "delivery_location": {"lat": "float", "lng": "float"},
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Frontend Architecture

#### Application Structure

Each of the three apps follows a similar architectural pattern:

```
frontend/
├── app/                    # Main application code
│   ├── (customer)/        # Customer app screens
│   │   ├── home.tsx       # Product browsing
│   │   ├── cart.tsx       # Shopping cart
│   │   ├── orders.tsx     # Order history
│   │   ├── map.tsx        # Order tracking
│   │   └── profile.tsx    # User profile
│   ├── (delivery)/        # Delivery agent screens
│   │   ├── orders.tsx     # Available orders
│   │   ├── active.tsx     # Active deliveries
│   │   ├── map.tsx        # Navigation
│   │   ├── history.tsx    # Completed deliveries
│   │   └── profile.tsx    # Agent profile
│   ├── (admin)/           # Admin panel screens
│   │   ├── dashboard.tsx  # Statistics overview
│   │   ├── products.tsx   # Product management
│   │   ├── orders.tsx     # Order management
│   │   ├── delivery-zones.tsx # Zone management
│   │   └── profile.tsx    # Admin profile
│   ├── _layout.tsx        # Root layout
│   ├── index.tsx          # Entry point
│   ├── login.tsx          # Login screen
│   └── register.tsx       # Registration screen
├── store/                 # State management
│   ├── authStore.ts       # Authentication state
│   └── useProtectedRoute.ts # Route protection
└── utils/                 # Utilities
    └── axios.ts           # API client configuration
```

#### Design System

1. **Color Schemes**:
   - Customer App: Blue (#007AFF) - Trust and reliability
   - Delivery Agent: Green (#34C759) - Action and movement
   - Admin Panel: Orange (#FF9500) - Authority and attention

2. **Navigation Pattern**:
   - Tab-based navigation for main sections
   - Stack navigation for detailed views
   - Modal overlays for quick actions

3. **Component Architecture**:
   ```typescript
   // Reusable Product Card Component
   interface ProductCardProps {
     product: Product;
     onPress: () => void;
     onAddToCart: (productId: string) => void;
   }
   ```

#### State Management Strategy

1. **Global State (Zustand)**:
   - Authentication state
   - User profile data
   - Cart persistence

2. **Local State (React Hooks)**:
   - UI state (loading, modals)
   - Form data
   - Temporary selections

3. **Persistent Storage (AsyncStorage)**:
   - JWT tokens
   - User preferences
   - Cart backup

### Database Design

#### MongoDB Collections

1. **users**:
   - Indexes: email (unique), role, delivery_zone_id
   - Purpose: User authentication and profile management

2. **products**:
   - Indexes: category, name (text search), stock
   - Purpose: Product catalog and inventory

3. **carts**:
   - Indexes: user_id (unique)
   - Purpose: Shopping cart persistence

4. **orders**:
   - Indexes: user_id, status, delivery_agent_id, created_at
   - Purpose: Order tracking and history

5. **delivery_zones**:
   - Indexes: 2dsphere on coordinates
   - Purpose: Geographical delivery area management

#### Data Relationships

```
users (1) ─── (1) carts
  │
  ├─── (n) orders
  │
  └─── (1) delivery_zones (for agents)

products (n) ─── (n) carts.items
  │
  └─── (n) orders.items

delivery_zones (1) ─── (n) users (agents)
```

## Project Structure

```
.github/
backend/
├── requirements.txt
├── server.py
├── test_db_connection.py
├── upload_products.py
frontend/
├── app/
│   ├── (admin)/
│   ├── (customer)/
│   ├── (delivery)/
│   ├── _layout.tsx
│   ├── index.tsx
│   └── login.tsx
├── assets/
├── store/
│   ├── authStore.ts
│   └── useProtectedRoute.ts
├── utils/
│   └── axios.ts
├── package.json
├── tsconfig.json
DATA.csv
LOGIN_CREDENTIALS.md
README.md
```

- `backend/`: Contains the FastAPI application, database connection, API endpoints, and utility scripts.
- `frontend/`: Contains the React Native Expo application, organized by user roles (admin, customer, delivery).
- `DATA.csv`: Sample data for bulk product upload.
- `LOGIN_CREDENTIALS.md`: Placeholder for login credentials.

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- Python 3.9+
- Node.js (LTS recommended)
- npm or yarn
- MongoDB instance (local or cloud-hosted)
- Expo Go app on your mobile device (for testing the frontend)

### Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file** in the `backend/` directory with the following content:
    ```env
    MONGO_URL="your_mongodb_connection_string"
    DB_NAME="delivery_app_db"
    JWT_SECRET="your_super_secret_jwt_key"
    ALGORITHM="HS256"
    ```
    Replace placeholders with your actual MongoDB connection string and a strong JWT secret.

5.  **Run the FastAPI server:**
    ```bash
    uvicorn server:app --reload
    ```
    The API will be accessible at `http://127.0.0.1:8000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    # or yarn install
    ```

3.  **Create a `.env` file** in the `frontend/` directory with the following content:
    ```env
    EXPO_PUBLIC_API_URL="http://192.168.1.x:8000" # Replace with your backend IP address
    ```
    **Important**: Replace `http://192.168.1.x:8000` with the actual IP address of your machine where the backend is running, followed by port `8000`. Do not use `localhost` or `127.0.0.1` if testing on a physical device.

4.  **Start the Expo development server:**
    ```bash
    npm start
    # or yarn start
    ```

5.  **Open the app**: Scan the QR code with the Expo Go app on your mobile device or choose to run on a web browser/emulator.

## API Documentation

### Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### API Endpoints

#### Authentication Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/auth/register` | Register new user | Public |
| POST | `/auth/login` | User login | Public |
| GET | `/auth/me` | Get current user | Authenticated |
| PUT | `/auth/profile` | Update user profile | Authenticated |

**Request/Response Examples:**
```json
// POST /auth/register
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "role": "customer",
  "phone": "+1234567890",
  "address": "123 Main St"
}

// Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "customer"
  }
}
```

#### Product Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/products` | List products with pagination | Public |
| GET | `/products/{id}` | Get product details | Public |
| POST | `/products` | Create new product | Admin |
| PUT | `/products/{id}` | Update product | Admin |
| DELETE | `/products/{id}` | Delete product | Admin |
| GET | `/categories` | List all categories | Public |

**Query Parameters (GET /products):**
- `category`: Filter by category (optional)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

#### Cart Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/cart` | Get user's cart | Authenticated |
| POST | `/cart/add` | Add item to cart | Authenticated |
| POST | `/cart/update` | Update item quantity | Authenticated |
| POST | `/cart/remove/{product_id}` | Remove item | Authenticated |
| DELETE | `/cart/clear` | Clear entire cart | Authenticated |

**Cart Operations Example:**
```json
// POST /cart/add
{
  "product_id": "product-uuid",
  "quantity": 2
}
```

#### Order Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/orders` | Create order from cart | Customer |
| GET | `/orders` | List orders (filtered by role) | Authenticated |
| GET | `/orders/{id}` | Get order details | Authenticated |
| PUT | `/orders/{id}/status` | Update order status | Agent/Admin |
| POST | `/orders/{id}/accept` | Accept order for delivery | Delivery Agent |

**Order Status Flow:**
```
pending → confirmed → preparing → out_for_delivery → delivered
                                           ↓
                                       cancelled
```

#### Delivery Zone Endpoints

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/delivery-zones` | List all zones | Authenticated |
| POST | `/delivery-zones` | Create new zone | Admin |
| PUT | `/delivery-zones/{id}/assign-agent` | Assign agent | Admin |

**Zone Creation Example:**
```json
// POST /delivery-zones
{
  "name": "Downtown Zone",
  "coordinates": [
    {"lat": 40.7128, "lng": -74.0060},
    {"lat": 40.7580, "lng": -73.9855},
    {"lat": 40.7614, "lng": -73.9776},
    {"lat": 40.7489, "lng": -73.9680}
  ]
}
```

#### Route Optimization

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/route/optimize` | Get optimized delivery route | Agent/Admin |

**Request Example:**
```json
// POST /route/optimize
[
  {"latitude": 40.7128, "longitude": -74.0060},
  {"latitude": 40.7580, "longitude": -73.9855},
  {"latitude": 40.7614, "longitude": -73.9776}
]
```

#### Admin Statistics

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/admin/stats` | Get platform statistics | Admin |

**Response Example:**
```json
{
  "total_products": 150,
  "total_orders": 1234,
  "total_customers": 567,
  "total_agents": 25,
  "total_revenue": 45678.90
}
```

### Error Responses

All API errors follow a consistent format:
```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

### API Documentation

Interactive API documentation is available via Swagger UI at:
```
http://127.0.0.1:8000/docs
```

Alternative ReDoc documentation:
```
http://127.0.0.1:8000/redoc
```

## Testing

### Backend Testing

The project includes comprehensive backend API testing with a test suite covering all major endpoints.

#### Running Backend Tests

```bash
# Navigate to the project root
cd delivery_App

# Run the backend test suite
python backend_test.py
```

#### Test Coverage

- **Authentication Tests**: Login, registration, token validation
- **Product Tests**: CRUD operations, role-based access
- **Cart Tests**: Add, update, remove items, clear cart
- **Order Tests**: Order creation, status updates, role-based visibility
- **Admin Tests**: Statistics, user management
- **Error Cases**: Invalid inputs, unauthorized access

**Current Test Results**: 97.1% success rate (34/35 tests passing)

### Frontend Testing

#### Manual Testing Checklist

**Customer App:**
- [ ] User registration and login
- [ ] Product browsing and search
- [ ] Category filtering
- [ ] Add/remove from cart
- [ ] Checkout process
- [ ] Order tracking

**Delivery Agent App:**
- [ ] Login as delivery agent
- [ ] View available orders
- [ ] Accept order
- [ ] Update delivery status
- [ ] Route optimization
- [ ] Delivery history

**Admin Panel:**
- [ ] Admin authentication
- [ ] View dashboard statistics
- [ ] Product CRUD operations
- [ ] Order management
- [ ] Delivery zone creation
- [ ] Agent assignment

### Test Accounts

```
Admin:
  Email: admin@shop.com
  Password: admin123

Customer:
  Email: customer@test.com
  Password: customer123

Delivery Agent:
  Email: driver@test.com
  Password: driver123
```

## Deployment

### Backend Deployment

#### Option 1: Traditional VPS

```bash
# Install dependencies
sudo apt update
sudo apt install python3.9 python3-pip nginx

# Clone repository
git clone <repository-url>
cd delivery_App/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
nano .env  # Edit with production values

# Run with Gunicorn
gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/delivery-app
```

#### Option 2: Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t delivery-app-backend .
docker run -d -p 8000:8000 --env-file .env delivery-app-backend
```

#### Option 3: Cloud Platforms

**Heroku:**
```bash
# Create Procfile
echo "web: uvicorn server:app --host=0.0.0.0 --port=${PORT:-5000}" > Procfile

# Deploy
heroku create delivery-app-api
heroku config:set MONGO_URL="your-mongo-url"
git push heroku main
```

**AWS Elastic Beanstalk:**
```bash
# Install EB CLI
pip install awsebcli

# Initialize and deploy
eb init -p python-3.9 delivery-app
eb create delivery-app-env
eb deploy
```

### Frontend Deployment

#### Building for Production

```bash
cd frontend

# Install EAS CLI
npm install -g eas-cli

# Configure EAS
eas build:configure

# Build for Android
eas build --platform android

# Build for iOS (requires Apple Developer account)
eas build --platform ios
```

#### Publishing to App Stores

**Google Play Store:**
1. Generate signed APK/AAB
2. Create Google Play Console account
3. Upload build and fill app details
4. Submit for review

**Apple App Store:**
1. Generate IPA file
2. Use App Store Connect
3. Upload via Xcode or Transporter
4. Submit for review

### Environment Variables

**Backend (.env):**
```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
DB_NAME=delivery_app_production
JWT_SECRET=your-super-secret-jwt-key
ALGORITHM=HS256
```

**Frontend (.env):**
```env
EXPO_PUBLIC_API_URL=https://api.yourdeliveryapp.com
```

### Production Considerations

1. **Security**:
   - Use HTTPS everywhere
   - Implement rate limiting
   - Add request validation
   - Enable CORS properly

2. **Performance**:
   - Enable MongoDB indexing
   - Implement caching (Redis)
   - Use CDN for images
   - Enable API response compression

3. **Monitoring**:
   - Set up error tracking (Sentry)
   - Implement logging (CloudWatch, LogDNA)
   - Add performance monitoring (New Relic, DataDog)
   - Configure uptime monitoring

4. **Backup**:
   - Automated database backups
   - Point-in-time recovery
   - Disaster recovery plan

## Troubleshooting

### Common Issues and Solutions

#### Backend Issues

**MongoDB Connection Error:**
```bash
# Error: Could not connect to MongoDB
# Solution: Check your MONGO_URL in .env file
# Ensure MongoDB is running and accessible
```

**JWT Token Invalid:**
```bash
# Error: Could not validate credentials
# Solution: Ensure JWT_SECRET is set correctly
# Check token expiration (30 days by default)
```

**Port Already in Use:**
```bash
# Error: Address already in use
# Solution:
lsof -i :8000  # Find process using port
kill -9 <PID>  # Kill the process
```

#### Frontend Issues

**Expo Connection Error:**
```bash
# Error: Unable to connect to development server
# Solution: Update EXPO_PUBLIC_API_URL with your machine's IP
# Not localhost or 127.0.0.1 for physical devices
```

**Metro Bundler Issues:**
```bash
# Solution: Clear cache
expo start -c
# or
npx react-native start --reset-cache
```

**Build Failures:**
```bash
# iOS build issues
cd ios && pod install

# Android build issues
cd android && ./gradlew clean
```

### Performance Optimization

1. **Backend Optimization**:
   - Enable MongoDB indexing on frequently queried fields
   - Implement pagination for large datasets
   - Use projection to limit returned fields
   - Enable compression middleware

2. **Frontend Optimization**:
   - Implement lazy loading for images
   - Use React.memo for expensive components
   - Enable Hermes for Android
   - Optimize bundle size

## Future Enhancements Roadmap

### Phase 1: Core Improvements (Q1 2024)
- [ ] **Real-time Order Tracking**: WebSocket integration for live updates
- [ ] **Push Notifications**: Firebase Cloud Messaging integration
- [ ] **Payment Gateway**: Stripe/PayPal integration
- [ ] **Multi-language Support**: i18n implementation

### Phase 2: Advanced Features (Q2 2024)
- [ ] **AI-Powered Recommendations**: Product suggestions based on order history
- [ ] **Voice Search**: Voice-to-text product search
- [ ] **Scheduled Deliveries**: Allow customers to schedule delivery times
- [ ] **Loyalty Program**: Points system and rewards

### Phase 3: Business Intelligence (Q3 2024)
- [ ] **Advanced Analytics Dashboard**: Sales trends, customer insights
- [ ] **Inventory Predictions**: ML-based stock predictions
- [ ] **Dynamic Pricing**: Time and demand-based pricing
- [ ] **Multi-vendor Support**: Transform into marketplace

### Phase 4: Scale & Optimize (Q4 2024)
- [ ] **Microservices Architecture**: Split monolith into services
- [ ] **GraphQL API**: Alternative to REST
- [ ] **Blockchain Integration**: For supply chain transparency
- [ ] **AR Product Preview**: Augmented reality for products

### Technical Debt Improvements
- [ ] Migrate from base64 to cloud storage (S3/Cloudinary)
- [ ] Implement comprehensive unit tests (target 80% coverage)
- [ ] Add CI/CD pipeline (GitHub Actions/GitLab CI)
- [ ] Implement API versioning
- [ ] Add request/response logging
- [ ] Implement rate limiting

## Contributing

We welcome contributions from the community! Here's how you can help:

### Getting Started

1. **Fork the Repository**
   ```bash
   # Clone your fork
   git clone https://github.com/your-username/delivery-app.git
   cd delivery-app
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add tests if applicable

4. **Commit Your Changes**
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
   
   Follow conventional commits:
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Test additions/changes
   - `chore:` Build process/auxiliary changes

5. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Include screenshots for UI changes

### Code Style Guidelines

- **Python (Backend)**: Follow PEP 8
- **TypeScript (Frontend)**: Use ESLint configuration
- **Commits**: Use conventional commits format
- **Documentation**: Update README for new features

### Reporting Issues

- Use GitHub Issues
- Include reproduction steps
- Provide system information
- Attach relevant logs/screenshots

## License

This project is licensed under the MIT License - see the LICENSE file for details.
