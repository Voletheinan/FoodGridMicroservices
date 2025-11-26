# Demo Guide — Food Delivery Microservices

This document provides step-by-step instructions for demonstrating the microservices system, including how to run it, test APIs, and answer architecture-related questions.

---

## Part 1: Running the System

### Prerequisites
- Docker and Docker Compose installed on your machine
- PowerShell (Windows) or Bash (Linux/macOS)
- curl or Postman (for API testing)

### Step 1: Start All Services

Navigate to the project root and bring up all containers:

```powershell
cd C:\Users\AnThiwn\Desktop\project
docker-compose up --build
```

**Expected Output:**
```
mongo_db | ready to accept connections
user_service | Connected to MongoDB: user_db
order_service | Connected to MongoDB: order_db
restaurant_service | Connected to MongoDB: restaurant_db
shipper_service | Connected to MongoDB: shipper_db
```

**Wait 30–60 seconds for all services to be ready.** Watch for "Connected to MongoDB" messages.

### Step 2: Verify All Services Are Healthy

In a new PowerShell terminal, check health endpoints:

```powershell
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
curl http://localhost:8004/health
```

**Expected Response (all services):**
```json
{
  "status": "healthy",
  "service": "user-service" | "order-service" | "restaurant-service" | "shipper-service"
}
```

---

## Part 2: API Testing Workflow

Follow this workflow to demonstrate key functionality. Run each command in PowerShell.

### 2.1 Create a User

**Create User "Alice":**

```powershell
$user = Invoke-RestMethod -Uri http://localhost:8001/users `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"username":"alice","email":"alice@example.com"}'

$user_id = $user.id
Write-Host "Created User: $user_id"
$user | ConvertTo-Json
```

**Expected Output:**
```
Created User: 674a1b2c3d4e5f6g7h8i9j0k
{
  "id": "674a1b2c3d4e5f6g7h8i9j0k",
  "username": "alice",
  "email": "alice@example.com",
  "addresses": []
}
```

### 2.2 Add Delivery Address for User

**Add an address to Alice's account:**

```powershell
$address = Invoke-RestMethod -Uri "http://localhost:8001/users/$user_id/addresses" `
  -Method Post `
  -ContentType "application/json" `
  -Body @{
    street = "123 Main St"
    city = "New York"
    state = "NY"
    zip_code = "10001"
    country = "USA"
  } | ConvertTo-Json -Depth 10

$address
```

**Expected Output:**
```json
{
  "id": "...",
  "street": "123 Main St",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "country": "USA"
}
```

### 2.3 Create a Restaurant

**Create "Pizza Palace" restaurant:**

```powershell
$restaurant = Invoke-RestMethod -Uri http://localhost:8003/restaurants `
  -Method Post `
  -ContentType "application/json" `
  -Body @{
    name = "Pizza Palace"
    description = "Italian pizza and pasta"
    address = "456 5th Ave, NYC"
    phone = "+1-555-0123"
  } | ConvertTo-Json -Depth 10

$rest_id = $restaurant.id
Write-Host "Created Restaurant: $rest_id"
$restaurant
```

**Expected Output:**
```json
{
  "id": "674a1c2d3e4f5g6h7i8j9k0l",
  "name": "Pizza Palace",
  "description": "Italian pizza and pasta",
  "address": "456 5th Ave, NYC",
  "phone": "+1-555-0123",
  "menu_items": []
}
```

### 2.4 Add Menu Items to Restaurant

**Add "Margherita Pizza" to menu:**

```powershell
$menu_item = Invoke-RestMethod -Uri "http://localhost:8003/restaurants/$rest_id/menu-items" `
  -Method Post `
  -ContentType "application/json" `
  -Body @{
    name = "Margherita Pizza"
    description = "Fresh basil, mozzarella, tomato sauce"
    price = 12.99
    available = $true
  } | ConvertTo-Json -Depth 10

$menu_id = $menu_item.id
Write-Host "Created Menu Item: $menu_id"
$menu_item
```

**Expected Output:**
```json
{
  "id": "674a1d2e3f4g5h6i7j8k9l0m",
  "name": "Margherita Pizza",
  "description": "Fresh basil, mozzarella, tomato sauce",
  "price": 12.99,
  "available": true
}
```

### 2.5 Create an Order

**Create order from user to restaurant (this validates user & restaurant via inter-service calls):**

```powershell
$order = Invoke-RestMethod -Uri http://localhost:8002/orders `
  -Method Post `
  -ContentType "application/json" `
  -Body @{
    user_id = $user_id
    restaurant_id = $rest_id
    items = @(
      @{
        menu_item_id = $menu_id
        quantity = 2
      }
    )
  } | ConvertTo-Json -Depth 10

$order_id = $order.id
Write-Host "Created Order: $order_id"
$order
```

**Expected Output:**
```json
{
  "id": "674a1e2f3g4h5i6j7k8l9m0n",
  "user_id": "674a1b2c3d4e5f6g7h8i9j0k",
  "restaurant_id": "674a1c2d3e4f5g6h7i8j9k0l",
  "items": [
    {
      "menu_item_id": "674a1d2e3f4g5h6i7j8k9l0m",
      "quantity": 2
    }
  ],
  "status": "cart",
  "shipper_id": null,
  "created_at": "2025-11-26T10:30:00.000Z"
}
```

**Note:** If you get a 400 error about "User not found" or "Restaurant not found", it means validation calls failed. This would indicate the dependent service is unreachable (check docker-compose logs).

### 2.6 Update Order Status

**Confirm the order (status: cart → confirmed):**

```powershell
$updated_order = Invoke-RestMethod -Uri "http://localhost:8002/orders/$order_id/status" `
  -Method Put `
  -ContentType "application/json" `
  -Body @{
    status = "confirmed"
  } | ConvertTo-Json -Depth 10

$updated_order
```

### 2.7 Create a Shipper and Assign to Order

**Create a shipper:**

```powershell
$shipper = Invoke-RestMethod -Uri http://localhost:8004/shippers `
  -Method Post `
  -ContentType "application/json" `
  -Body @{
    name = "John Doe"
    phone = "+1-555-9999"
    vehicle = "Motorbike"
    status = "available"
  } | ConvertTo-Json -Depth 10

$shipper_id = $shipper.id
Write-Host "Created Shipper: $shipper_id"
$shipper
```

**Assign shipper to order:**

```powershell
$shipped_order = Invoke-RestMethod -Uri "http://localhost:8002/orders/$order_id/shipper" `
  -Method Put `
  -ContentType "application/json" `
  -Body @{
    shipper_id = $shipper_id
  } | ConvertTo-Json -Depth 10

Write-Host "Order assigned to shipper. Status updated to: $($shipped_order.status)"
$shipped_order
```

### 2.8 Retrieve Order History

**Get all orders from user:**

```powershell
$user_orders = Invoke-RestMethod -Uri "http://localhost:8001/users/$user_id"
$user_orders | ConvertTo-Json -Depth 10
```

**Or get all orders for restaurant:**

```powershell
$rest_orders = Invoke-RestMethod -Uri "http://localhost:8002/orders/restaurants/$rest_id/orders"
$rest_orders | ConvertTo-Json -Depth 10
```

---

## Part 3: Demonstrating Inter-Service Communication

### Key Point: Order Service Validates References

When you created the order, the `order-service` made HTTP calls:

1. **Called User Service:** `GET http://user-service:8000/users/{user_id}`
2. **Called Restaurant Service:** `GET http://restaurant-service:8000/restaurants/{restaurant_id}`

**To show this in action:**

1. Open a second terminal and watch Order Service logs:
```powershell
docker-compose logs -f order-service
```

2. Create another order (you'll see logs showing the validation calls)
3. Try creating an order with a fake `user_id` → you'll get a 400 error "User not found"

**This demonstrates:** Services communicate and validate data integrity without sharing a database.

---

## Part 4: Architecture Q&A Talking Points

Prepare to answer these questions during demo:

### Q1: "Why did you split the system into 4 services instead of 1 monolith?"

**Answer:**
- **Domain-Driven Design (DDD):** Each service owns a bounded context:
  - **User Service:** User identity & address management
  - **Order Service:** Order lifecycle & fulfillment
  - **Restaurant Service:** Restaurant catalog & menu
  - **Shipper Service:** Delivery personnel & availability
- **Independent Scalability:** If orders spike, scale only `order-service` without scaling the user database.
- **Technology Freedom:** Each service can use different languages/databases (we used MongoDB for all, but could mix).
- **Team Independence:** Different teams can own different services and deploy independently.
- **Fault Isolation:** If restaurant service goes down, users can still place orders (they'd just fail validation, but system degrades gracefully).

### Q2: "What are the trade-offs / limitations of your design?"

**Limitations & Trade-offs:**

1. **Complexity:**
   - Multiple Docker containers to manage
   - Network calls between services add latency
   - Harder to debug distributed issues (logs spread across services)

2. **Data Consistency:**
   - No ACID transactions across services
   - If order-service saves an order but shipper-service fails later, the system is inconsistent
   - We use eventual consistency (accept temporary inconsistency)

3. **Network Dependency:**
   - Order creation depends on user-service & restaurant-service being reachable
   - If network partitions, order creation fails with 502 error
   - In production, would need circuit breakers & retries (not implemented here)

4. **Operational Overhead:**
   - Each service needs monitoring, logging, deployment pipeline
   - Running 4 services + MongoDB = 5 containers (more complex than 1 monolith)

5. **Shared Mongo Instance:**
   - We use 1 MongoDB with 4 separate databases (not true separation)
   - In production, each service would have its own Mongo instance (cost & complexity trade-off)

### Q3: "How do services talk to each other?"

**Answer:**
- **Synchronous HTTP (REST):** Services call each other via HTTP when they need immediate responses
  - Example: Order service validates user & restaurant before creating order
  - Used for: validation, lookups, status checks
- **Database per Service:** No shared database; services don't query each other's tables
  - Example: Order stores `user_id` as foreign reference (not a database FK)
- **Potential Future Enhancement:** Message queues (RabbitMQ, Kafka) for async communication:
  - Example: Order created → publish event → Restaurant service subscribes and prepares food
  - Decouples services, improves resilience

### Q4: "What about authentication & authorization?"

**Answer:**
- **Not Implemented:** This is a prototype showing architecture concepts
- **In Production:** Would add:
  - JWT tokens issued by User Service
  - All requests include token
  - Services validate token before processing

### Q5: "How would you scale this system?"

**Answer:**
1. **Horizontal Scaling:** Run multiple instances of each service behind a load balancer
2. **Database Replication:** Use MongoDB sharding for high-volume data
3. **Caching:** Add Redis for frequently accessed data (restaurants, menus)
4. **Async Processing:** Use message queues for long-running operations (payment, notification)
5. **API Gateway:** Single entry point for all clients (we removed ours, but would add back for production)

### Q6: "What would you improve if given more time?"

**Answer:**
1. **Healthchecks in Docker:** Add liveness & readiness probes
2. **Circuit Breakers:** Prevent cascading failures when services are slow
3. **Distributed Tracing:** Use OpenTelemetry to track requests across services
4. **Authentication:** Add JWT tokens across services
5. **Tests:** Add pytest for each service
6. **Async Messaging:** Replace HTTP with event-driven communication for order/delivery
7. **API Gateway:** Re-add gateway with rate limiting, CORS, logging
8. **Database Per Service:** Use separate MongoDB instances (or PostgreSQL per service)

---

## Part 5: Troubleshooting During Demo

### Symptom: "Services won't start"
**Action:**
```powershell
docker-compose logs
# Look for MongoDB connection errors
# Services retry connection; wait 30–60 seconds
```

### Symptom: "404 Not Found when calling APIs"
**Action:**
- Confirm service is running: `docker-compose ps`
- Confirm correct port: user=8001, order=8002, restaurant=8003, shipper=8004
- Check service logs: `docker-compose logs order-service`

### Symptom: "Order creation fails with 502 Bad Gateway"
**Action:**
- Order service tried to call user/restaurant service but failed
- Check if those services are running: `docker-compose logs user-service`
- Confirm network connectivity: all services on `microservices_network`

### Symptom: "Database errors (MongoDB not ready)"
**Action:**
- Mongo needs time to start
- Wait another 30 seconds
- Check logs: `docker-compose logs mongo`

---

## Summary: Demo Flow (10–15 minutes)

1. (**2 min**) Start docker-compose → show all services healthy
2. (**1 min**) Explain the 4 services & their domain responsibility
3. (**8 min**) Run API test workflow:
   - Create user → Add address
   - Create restaurant → Add menu item
   - Create order (show validation calls in logs)
   - Update order status → Assign shipper
4. (**3 min**) Answer architecture Q&A
5. (**1 min**) Discuss improvements for production

**Key Talking Points to Emphasize:**
- ✅ Services are independent and scalable
- ✅ Database per service (no shared tables)
- ✅ Inter-service validation (order service calls user/restaurant)
- ✅ Containerized with Docker for consistency
- ⚠️ Trade-offs: complexity, network latency, eventual consistency
- 🔮 Future: async messaging, circuit breakers, authentication

---

## Automated Smoke Test Script

If you want to automate the entire demo, use the provided `smoke_test.ps1`:

```powershell
.\smoke_test.ps1
```

This script automatically:
- Waits for service health checks
- Creates user, restaurant, and order
- Prints results

---

## Quick Reference: Service Ports & URLs

| Service | Port | Health Endpoint |
|---------|------|-----------------|
| User | 8001 | http://localhost:8001/health |
| Order | 8002 | http://localhost:8002/health |
| Restaurant | 8003 | http://localhost:8003/health |
| Shipper | 8004 | http://localhost:8004/health |
| MongoDB | 27017 | (internal only) |

---

**Good luck with your demo!** 🚀
