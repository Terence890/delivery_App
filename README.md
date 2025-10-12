# Delivery App

This is a full-stack delivery application designed to connect customers, delivery agents, and administrators. The application features a robust backend API built with FastAPI and a dynamic mobile frontend developed using React Native (Expo).

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

- **User Authentication & Authorization**: Secure login and registration for Customers, Delivery Agents, and Admins.
- **Product Management**: Admins can add, view, update, and delete products. Includes product details like name, brand, description, price, category, stock, unit, variant, code, barcode, and image.
- **Shopping Cart**: Customers can add, remove, and update items in their cart.
- **Order Management**: Customers can place orders, view order history. Admins and Delivery Agents can manage order statuses.
- **Delivery Zone Management**: Admins can define delivery zones and assign agents.
- **Route Optimization**: Delivery agents can optimize their delivery routes using OSRM integration.
- **Admin Dashboard**: High-level statistics for administrators (total products, orders, customers, agents, revenue).
- **Image Handling**: Product images are stored as base64 encoded strings.
- **Bulk Product Upload**: Script for uploading products from a CSV file with image conversion.

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

## API Endpoints

The backend provides the following main API categories:

-   `/auth`: User registration, login, profile management.
-   `/products`: CRUD operations for products, category listing.
-   `/cart`: Add, remove, update, clear cart items.
-   `/orders`: Create, view, update orders.
-   `/delivery-zones`: Create, view, assign agents to delivery zones.
-   `/route`: Route optimization for delivery agents.
-   `/admin/stats`: Administrative statistics.

Detailed API documentation can be accessed via the automatically generated OpenAPI (Swagger UI) documentation at `http://127.0.0.1:8000/docs` when the backend server is running.

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'feat: Add new feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
