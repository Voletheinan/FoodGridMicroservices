# 🍕 FoodGrid - Microservices Food Delivery System

## 📋 Project Overview

A complete **microservices-based food delivery system** built with **FastAPI**, **MongoDB**, and **Docker**. The system demonstrates domain-driven design with 4 independent services, each with its own database and inter-service communication via REST APIs.

**Architecture Pattern:** Database per Service + Synchronous HTTP Communication

---

## 🏗️ System Architecture

### 4 Microservices:

#### 1. **User Service** (Port 8001)
- **Purpose:** User registration, profiles, delivery addresses
- **Database:** MongoDB `user_db`
- **Key Endpoints:**
  - `POST /users` → Create user (returns 201)
  - `GET /users/{user_id}` → Get user details
  - `POST /users/{user_id}/addresses` → Add delivery address
  - `GET /users/{user_id}/addresses` → List addresses

#### 2. **Restaurant Service** (Port 8003)
- **Purpose:** Restaurant catalog, menu management
- **Database:** MongoDB `restaurant_db`
- **Key Endpoints:**
  - `POST /restaurants` → Create restaurant (returns 201)
  - `GET /restaurants` → List all restaurants
  - `POST /restaurants/{restaurant_id}/menu-items` → Add menu item (returns 201)
  - `GET /restaurants/{restaurant_id}/menu-items` → List menu items

#### 3. **Order Service** (Port 8002)
- **Purpose:** Order lifecycle management with inter-service validation
- **Database:** MongoDB `order_db`
- **Key Endpoints:**
  - `POST /orders` → Create order (validates user + restaurant via HTTP calls, returns 201)
  - `GET /orders/{order_id}` → Get order with full details (user name, restaurant name, item names, shipper name)
  - `PUT /orders/{order_id}/status` → Update order status
  - `PUT /orders/{order_id}/shipper` → Assign shipper (auto updates shipper status to "busy")
  - `GET /orders/users/{user_id}/orders` → Get user's order history
  - `GET /orders/restaurants/{restaurant_id}/orders` → Get restaurant's orders

#### 4. **Shipper Service** (Port 8004)
- **Purpose:** Delivery personnel management
- **Database:** MongoDB `shipper_db`
- **Key Endpoints:**
  - `POST /shippers` → Create shipper (returns 201)
  - `GET /shippers` → List available shippers
  - `PUT /shippers/{shipper_id}/status` → Update shipper status (available/busy/offline)

### Infrastructure:

- **MongoDB 6.0** (Port 27017)
  - Credentials: `root:password`
  - Separate database per service
  - Automatic retry + health check on startup

- **Docker Network:** `microservices_network` (bridge)

---

## 📁 Project Structure

```
project/
├── docker-compose.yml          # Orchestration config
├── README.md                   # This file
├── API_DESIGN.md              # Detailed API specifications
├── DEMO_GUIDE.md              # Demo walkthrough
├── smoke_test.ps1             # Integration test script
│
├── user-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── schemas.py
│       ├── crud.py
│       └── routers/
│           └── users.py
│
├── order-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── schemas.py
│       ├── crud.py
│       └── routers/
│           └── orders.py
│
├── restaurant-service/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── schemas.py
│       ├── crud.py
│       └── routers/
│           └── restaurants.py
│
└── shipper-service/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── main.py
        ├── database.py
        ├── schemas.py
        ├── crud.py
        └── routers/
            └── shippers.py
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- PowerShell (for Windows) or Bash (for Linux/Mac)

### Run All Services

```powershell
# Navigate to project
cd C:\Users\AnThiwn\Desktop\project

# Start all services
docker-compose up --build

# Wait ~30 seconds for services to initialize
```

### Stop Services

```powershell
# Stop containers (keep volumes)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

---

## 🧪 Testing & Demo

### Health Check Endpoints

```powershell
# User Service
curl http://localhost:8001/health

# Order Service
curl http://localhost:8002/health

# Restaurant Service
curl http://localhost:8003/health

# Shipper Service
curl http://localhost:8004/health
```

### Interactive Testing with Swagger UI

Each service has an auto-generated Swagger UI:

- **User Service:** http://localhost:8001/docs
- **Order Service:** http://localhost:8002/docs
- **Restaurant Service:** http://localhost:8003/docs
- **Shipper Service:** http://localhost:8004/docs

Click "Try it out" on any endpoint to test!

### Example: Complete Demo Flow

#### 1. Create a User
```bash
POST http://localhost:8001/users
{
  "username": "john_doe",
  "email": "john@example.com"
}
# Response: { "id": "...", "username": "john_doe", ... }
```

#### 2. Create a Restaurant
```bash
POST http://localhost:8003/restaurants
{
  "name": "Pizza Palace",
  "description": "Best Italian pizza",
  "address": "123 Main St",
  "phone": "555-0001",
  "cuisine_type": "Italian"
}
# Response: { "id": "...", "name": "Pizza Palace", ... }
```

#### 3. Add Menu Items
```bash
POST http://localhost:8003/restaurants/{restaurant_id}/menu-items
{
  "name": "Margherita",
  "description": "Classic pizza",
  "price": 12.99
}
# Response: { "id": "...", "name": "Margherita", "price": 12.99 }
```

#### 4. Create an Order
```bash
POST http://localhost:8002/orders
{
  "user_id": "USER_ID_FROM_STEP_1",
  "restaurant_id": "RESTAURANT_ID_FROM_STEP_2",
  "items": [
    {
      "menu_item_id": "MENU_ITEM_ID_FROM_STEP_3",
      "quantity": 2
    }
  ],
  "delivery_address": "456 Oak Ave"
}
# Response: Full order with user_name, restaurant_name, item names!
```

#### 5. Create a Shipper
```bash
POST http://localhost:8004/shippers
{
  "name": "John Driver",
  "phone": "555-0002",
  "vehicle": "motorcycle"
}
# Response: { "id": "...", "name": "John Driver", "status": "available" }
```

#### 6. Assign Shipper to Order
```bash
PUT http://localhost:8002/orders/{order_id}/shipper
{
  "shipper_id": "SHIPPER_ID_FROM_STEP_5"
}
# Automatically updates shipper status to "busy"!
# Response: Order with shipper_name now included
```

#### 7. Update Order Status
```bash
PUT http://localhost:8002/orders/{order_id}/status
{
  "status": "delivered"
}
```

#### 8. Update Shipper Status (After Delivery)
```bash
PUT http://localhost:8004/shippers/{shipper_id}/status
{
  "status": "available"
}
```

---

## 🔄 Inter-Service Communication

### How It Works

When creating an order, **Order Service** validates user and restaurant:

```
Client → POST /orders
         ↓
Order Service validates:
  ├─→ GET http://user-service:8000/users/{user_id}
  └─→ GET http://restaurant-service:8000/restaurants/{restaurant_id}
         ↓
  If both exist → Create order (201)
  If either missing → Return 400
  If service unreachable → Return 502
```

### Automatic Shipper Status Update

When assigning shipper to order:

```
Client → PUT /orders/{order_id}/shipper
         ↓
Order Service:
  ├─→ Update order with shipper_id + status="shipped"
  └─→ PUT http://shipper-service:8000/shippers/{shipper_id}/status
      Body: {"status": "busy"}
         ↓
Shipper automatically becomes "busy"!
```

---

## 📊 Order Response Example

```json
{
  "id": "69265b143a46a1e30ef055e8",
  "user_id": "692655b8cb89a06a2df8b7e5",
  "user_name": "Thien an",
  "restaurant_id": "692642fc44b562c9a24c568c",
  "restaurant_name": "Pizza Palace",
  "items": [
    {
      "menu_item_id": "6926430a44b562c9a24c568d",
      "item_name": "Margherita",
      "price": 12.99,
      "quantity": 10
    }
  ],
  "status": "shipped",
  "shipper_id": "69265c592403b392a0484b68",
  "shipper_name": "Tống Hữu Định",
  "created_at": "2025-11-26T01:42:44.955436"
}
```

Notice: Response includes actual names instead of just IDs! Easy to understand.

---

## 🔧 Key Features Implemented

✅ **Domain-Driven Microservices** - 4 independent services by business domain
✅ **Database per Service** - Each service has its own MongoDB database
✅ **Inter-Service Communication** - Synchronous HTTP REST calls for validation
✅ **Proper HTTP Status Codes** - POST returns 201, GET returns 200, etc.
✅ **Database Retry Logic** - Handles MongoDB startup delays
✅ **Rich Response Data** - Orders show actual names, not just IDs
✅ **Automatic Status Updates** - Shipper status auto-updates when assigned
✅ **Order History Tracking** - Users and restaurants can view their orders
✅ **Health Endpoints** - Each service has `/health` for monitoring
✅ **Swagger/OpenAPI Documentation** - Auto-generated on `/docs` for each service

---

## 📚 Additional Documentation

- **[API_DESIGN.md](./API_DESIGN.md)** - Complete API specifications for all 23 endpoints
- **[DEMO_GUIDE.md](./DEMO_GUIDE.md)** - Step-by-step demo workflow + architectural Q&A

---

## 🛠️ Technologies Used

- **Framework:** FastAPI (async Python web framework)
- **Database:** MongoDB 6.0 (NoSQL)
- **Async Driver:** Motor (AsyncIOMotor for MongoDB)
- **HTTP Client:** httpx (for inter-service calls)
- **Validation:** Pydantic
- **Containerization:** Docker & Docker Compose
- **API Documentation:** Swagger/OpenAPI

---

## 📝 Environment Variables

Default values (can be overridden):

```
USER_SERVICE_URL=http://user-service:8000
RESTAURANT_SERVICE_URL=http://restaurant-service:8000
SHIPPER_SERVICE_URL=http://shipper-service:8000
MONGODB_URL=mongodb://root:password@mongo:27017/
```

---

## 🐛 Troubleshooting

### Services won't start?
```powershell
# Check logs
docker-compose logs -f

# Check specific service
docker-compose logs order-service

# Verify containers are running
docker ps
```

### MongoDB connection issues?
```powershell
# MongoDB needs ~10 seconds to start
# Services automatically retry connection

# Manual check
docker-compose logs mongo
```

### Can't reach services from outside Docker?
- Use `http://localhost:PORT` when running from host
- Use `http://service-name:8000` when running inside Docker network

---

## 📋 Assignment Requirements Checklist

✅ **1. Monolith Decomposition** - Decomposed into 4 domain services
✅ **2. Microservices Patterns** - Database per Service, sync HTTP communication
✅ **3.1 Service Architecture** - Each service has clean folder structure
✅ **3.2 HTTP Status Codes** - POST returns 201, proper error codes
✅ **3.3 API Design** - [See API_DESIGN.md](./API_DESIGN.md)
✅ **4.1 Docker Setup** - All services containerized with docker-compose
✅ **4.2 Health Checks** - `/health` endpoint on each service
✅ **4.3 Demo Capability** - [See DEMO_GUIDE.md](./DEMO_GUIDE.md)

---

## 👨‍💻 Development Notes

### Adding New Endpoints
1. Define schema in `app/schemas.py`
2. Implement CRUD in `app/crud.py`
3. Add route in `app/routers/`
4. Rebuild container: `docker-compose up --build SERVICE_NAME`

### Debugging Inter-Service Calls
- Check logs: `docker-compose logs order-service`
- Verify service URLs in environment
- Test manually: `curl http://service-name:8000/health`

### Testing
Run the smoke test script:
```powershell
.\smoke_test.ps1
```

---

## 📞 Contact & Support

For questions about architecture or implementation, refer to:
- `API_DESIGN.md` - Detailed endpoint specs
- `DEMO_GUIDE.md` - Demo walkthrough and Q&A

---

**Last Updated:** November 26, 2025
**Version:** 1.0
