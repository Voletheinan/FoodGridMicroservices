# API Design Documentation - Microservices

This document outlines the REST API design for all microservices in the Food Delivery system. Each service exposes a set of endpoints for domain-specific operations.

---

## 1. User Service (Port 8001)

**Purpose:** Manages user registration, profiles, and delivery addresses.

### 1.1 POST /users - Create User

**HTTP Method:** POST  
**URL Path:** `/users`  
**Business Purpose:** Register a new user account with email for the food delivery platform. This is the first step for a customer to start using the system.

**Request Body:**
```json
{
  "username": "string (required)",
  "email": "string (required, email format)"
}
```

**Response (201 Created):**
```json
{
  "id": "string (MongoDB ObjectId)",
  "username": "string",
  "email": "string",
  "addresses": []
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid input"
}
```

---

### 1.2 GET /users/{user_id} - Get User by ID

**HTTP Method:** GET  
**URL Path:** `/users/{user_id}`  
**Business Purpose:** Retrieve detailed information about a specific user, including their profile and saved delivery addresses.

**Request Body:** None

**Response (200 OK):**
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "addresses": [
    {
      "id": "string",
      "street": "string",
      "city": "string",
      "state": "string",
      "zip_code": "string",
      "country": "string"
    }
  ]
}
```

**Response (404 Not Found):**
```json
{
  "detail": "User not found"
}
```

---

### 1.3 POST /users/{user_id}/addresses - Add Address

**HTTP Method:** POST  
**URL Path:** `/users/{user_id}/addresses`  
**Business Purpose:** Save a new delivery address for a user. Users can have multiple addresses for different locations (home, office, etc.).

**Request Body:**
```json
{
  "street": "string (required)",
  "city": "string (required)",
  "state": "string (required)",
  "zip_code": "string (required)",
  "country": "string (required)"
}
```

**Response (201 Created):**
```json
{
  "id": "string (MongoDB ObjectId)",
  "street": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "country": "string"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "User not found"
}
```

---

### 1.4 GET /users/{user_id}/addresses - Get User Addresses

**HTTP Method:** GET  
**URL Path:** `/users/{user_id}/addresses`  
**Business Purpose:** Retrieve all saved delivery addresses for a user to allow quick address selection during checkout.

**Request Body:** None

**Response (200 OK):**
```json
[
  {
    "id": "string",
    "street": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "country": "string"
  }
]
```

---

### 1.5 PUT /users/{user_id}/addresses/{address_id} - Update Address

**HTTP Method:** PUT  
**URL Path:** `/users/{user_id}/addresses/{address_id}`  
**Business Purpose:** Modify an existing delivery address when user information changes.

**Request Body:**
```json
{
  "street": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "country": "string"
}
```

**Response (200 OK):**
```json
{
  "id": "string",
  "street": "string",
  "city": "string",
  "state": "string",
  "zip_code": "string",
  "country": "string"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Address not found"
}
```

---

### 1.6 DELETE /users/{user_id}/addresses/{address_id} - Delete Address

**HTTP Method:** DELETE  
**URL Path:** `/users/{user_id}/addresses/{address_id}`  
**Business Purpose:** Remove a previously saved delivery address when no longer needed.

**Request Body:** None

**Response (200 OK):**
```json
{
  "message": "Address deleted"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Address not found"
}
```

---

## 2. Order Service (Port 8002)

**Purpose:** Manages customer orders, order status tracking, and shipper assignment.

### 2.1 POST /orders - Create Order

**HTTP Method:** POST  
**URL Path:** `/orders`  
**Business Purpose:** Create a new order with selected restaurant and menu items. The service validates that user and restaurant exist before creating the order (validates user_id and restaurant_id via HTTP calls to respective services).

**Request Body:**
```json
{
  "user_id": "string (MongoDB ObjectId, required)",
  "restaurant_id": "string (required)",
  "items": [
    {
      "menu_item_id": "string (required)",
      "quantity": "integer (required, >= 1)"
    }
  ]
}
```

**Response (201 Created):**
```json
{
  "id": "string (MongoDB ObjectId)",
  "user_id": "string",
  "restaurant_id": "string",
  "items": [
    {
      "menu_item_id": "string",
      "quantity": "integer"
    }
  ],
  "status": "cart",
  "shipper_id": null,
  "created_at": "string (ISO timestamp)"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "User not found" | "Restaurant not found"
}
```

**Response (502 Bad Gateway):**
```json
{
  "detail": "Cannot reach user service" | "Cannot reach restaurant service"
}
```

---

### 2.2 GET /orders/{order_id} - Get Order by ID

**HTTP Method:** GET  
**URL Path:** `/orders/{order_id}`  
**Business Purpose:** Retrieve full details of a specific order including items, status, and assigned shipper (used for order tracking).

**Request Body:** None

**Response (200 OK):**
```json
{
  "id": "string",
  "user_id": "string",
  "restaurant_id": "string",
  "items": [
    {
      "menu_item_id": "string",
      "quantity": "integer"
    }
  ],
  "status": "cart|confirmed|preparing|ready|shipped|delivered",
  "shipper_id": "string or null",
  "created_at": "string (ISO timestamp)"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Order not found"
}
```

---

### 2.3 GET /orders/users/{user_id}/orders - List User Orders

**HTTP Method:** GET  
**URL Path:** `/orders/users/{user_id}/orders`  
**Business Purpose:** Retrieve all orders placed by a specific user for order history and current order tracking.

**Request Body:** None

**Response (200 OK):**
```json
[
  {
    "id": "string",
    "user_id": "string",
    "restaurant_id": "string",
    "items": [...],
    "status": "string",
    "shipper_id": "string or null",
    "created_at": "string"
  }
]
```

---

### 2.4 PUT /orders/{order_id}/status - Update Order Status

**HTTP Method:** PUT  
**URL Path:** `/orders/{order_id}/status`  
**Business Purpose:** Update order status as it progresses through fulfillment stages (cart → confirmed → preparing → ready → shipped → delivered).

**Request Body:**
```json
{
  "status": "string (one of: cart, confirmed, preparing, ready, shipped, delivered)"
}
```

**Response (200 OK):**
```json
{
  "id": "string",
  "user_id": "string",
  "restaurant_id": "string",
  "items": [...],
  "status": "string",
  "shipper_id": "string or null",
  "created_at": "string"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Order not found"
}
```

---

### 2.5 PUT /orders/{order_id}/shipper - Assign Shipper

**HTTP Method:** PUT  
**URL Path:** `/orders/{order_id}/shipper`  
**Business Purpose:** Assign a shipper to an order when it is ready for delivery. Updates order status to "shipped".

**Request Body:**
```json
{
  "shipper_id": "string (required)"
}
```

**Response (200 OK):**
```json
{
  "id": "string",
  "user_id": "string",
  "restaurant_id": "string",
  "items": [...],
  "status": "shipped",
  "shipper_id": "string",
  "created_at": "string"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Order not found"
}
```

---

### 2.6 GET /orders/restaurants/{restaurant_id}/orders - List Restaurant Orders

**HTTP Method:** GET  
**URL Path:** `/orders/restaurants/{restaurant_id}/orders`  
**Business Purpose:** Retrieve all orders for a restaurant for kitchen management and order preparation.

**Request Body:** None

**Response (200 OK):**
```json
[
  {
    "id": "string",
    "user_id": "string",
    "restaurant_id": "string",
    "items": [...],
    "status": "string",
    "shipper_id": "string or null",
    "created_at": "string"
  }
]
```

---

## 3. Restaurant Service (Port 8003)

**Purpose:** Manages restaurant information, menu items, and food inventory.

### 3.1 POST /restaurants - Create Restaurant

**HTTP Method:** POST  
**URL Path:** `/restaurants`  
**Business Purpose:** Register a new restaurant on the platform with basic information (name, description, address, contact).

**Request Body:**
```json
{
  "name": "string (required)",
  "description": "string (required)",
  "address": "string (required)",
  "phone": "string (required)",
  "menu_items": []
}
```

**Response (201 Created):**
```json
{
  "id": "string (MongoDB ObjectId)",
  "name": "string",
  "description": "string",
  "address": "string",
  "phone": "string",
  "menu_items": []
}
```

---

### 3.2 GET /restaurants - List All Restaurants

**HTTP Method:** GET  
**URL Path:** `/restaurants`  
**Business Purpose:** Retrieve a list of all active restaurants available on the platform for browsing and discovery.

**Request Body:** None

**Response (200 OK):**
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "address": "string",
    "phone": "string",
    "menu_items": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "price": "float",
        "available": "boolean"
      }
    ]
  }
]
```

---

### 3.3 GET /restaurants/{restaurant_id} - Get Restaurant by ID

**HTTP Method:** GET  
**URL Path:** `/restaurants/{restaurant_id}`  
**Business Purpose:** Retrieve detailed information about a specific restaurant including its complete menu.

**Request Body:** None

**Response (200 OK):**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "address": "string",
  "phone": "string",
  "menu_items": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "price": "float",
      "available": "boolean"
    }
  ]
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Restaurant not found"
}
```

---

### 3.4 POST /restaurants/{restaurant_id}/menu-items - Add Menu Item

**HTTP Method:** POST  
**URL Path:** `/restaurants/{restaurant_id}/menu-items`  
**Business Purpose:** Add a new food item to a restaurant's menu with pricing and availability status.

**Request Body:**
```json
{
  "name": "string (required)",
  "description": "string (required)",
  "price": "float (required, >= 0)",
  "available": "boolean (default: true)"
}
```

**Response (201 Created):**
```json
{
  "id": "string (MongoDB ObjectId)",
  "name": "string",
  "description": "string",
  "price": "float",
  "available": "boolean"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Restaurant not found"
}
```

---

### 3.5 GET /restaurants/{restaurant_id}/menu-items - Get Menu Items

**HTTP Method:** GET  
**URL Path:** `/restaurants/{restaurant_id}/menu-items`  
**Business Purpose:** Retrieve all menu items for a restaurant to display in the ordering interface.

**Request Body:** None

**Response (200 OK):**
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "price": "float",
    "available": "boolean"
  }
]
```

---

### 3.6 PUT /restaurants/{restaurant_id}/menu-items/{item_id} - Update Menu Item

**HTTP Method:** PUT  
**URL Path:** `/restaurants/{restaurant_id}/menu-items/{item_id}`  
**Business Purpose:** Update menu item details (price, description) or availability status.

**Request Body:**
```json
{
  "name": "string",
  "description": "string",
  "price": "float",
  "available": "boolean"
}
```

**Response (200 OK):**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": "float",
  "available": "boolean"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Menu item not found"
}
```

---

### 3.7 DELETE /restaurants/{restaurant_id}/menu-items/{item_id} - Delete Menu Item

**HTTP Method:** DELETE  
**URL Path:** `/restaurants/{restaurant_id}/menu-items/{item_id}`  
**Business Purpose:** Remove a menu item from a restaurant's offerings when it is no longer available or sold.

**Request Body:** None

**Response (200 OK):**
```json
{
  "message": "Menu item deleted"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Menu item not found"
}
```

---

## 4. Shipper Service (Port 8004)

**Purpose:** Manages delivery personnel, their availability status, and location/vehicle information.

### 4.1 POST /shippers - Create Shipper

**HTTP Method:** POST  
**URL Path:** `/shippers`  
**Business Purpose:** Register a new delivery driver/shipper with vehicle and contact information.

**Request Body:**
```json
{
  "name": "string (required)",
  "phone": "string (required)",
  "vehicle": "string (required, e.g., 'Motorbike', 'Car')",
  "status": "string (default: 'available', one of: available, busy, offline)"
}
```

**Response (201 Created):**
```json
{
  "id": "string (MongoDB ObjectId)",
  "name": "string",
  "phone": "string",
  "vehicle": "string",
  "status": "available"
}
```

---

### 4.2 GET /shippers/{shipper_id} - Get Shipper by ID

**HTTP Method:** GET  
**URL Path:** `/shippers/{shipper_id}`  
**Business Purpose:** Retrieve detailed information about a specific shipper including vehicle type and current availability.

**Request Body:** None

**Response (200 OK):**
```json
{
  "id": "string",
  "name": "string",
  "phone": "string",
  "vehicle": "string",
  "status": "string"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Shipper not found"
}
```

---

### 4.3 GET /shippers - List Available Shippers

**HTTP Method:** GET  
**URL Path:** `/shippers`  
**Business Purpose:** Retrieve all available shippers for assignment to new orders. Only shows shippers with "available" status.

**Request Body:** None

**Response (200 OK):**
```json
[
  {
    "id": "string",
    "name": "string",
    "phone": "string",
    "vehicle": "string",
    "status": "available"
  }
]
```

---

### 4.4 PUT /shippers/{shipper_id}/status - Update Shipper Status

**HTTP Method:** PUT  
**URL Path:** `/shippers/{shipper_id}/status`  
**Business Purpose:** Update shipper availability status (e.g., set to "busy" when assigned to a delivery, "offline" when ending shift).

**Request Body:**
```json
{
  "status": "string (one of: available, busy, offline)"
}
```

**Response (200 OK):**
```json
{
  "id": "string",
  "name": "string",
  "phone": "string",
  "vehicle": "string",
  "status": "string"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Shipper not found"
}
```

---

## Summary Table

| Service | Endpoint | Method | Purpose |
|---------|----------|--------|---------|
| **User** | /users | POST | Create user |
| **User** | /users/{user_id} | GET | Get user |
| **User** | /users/{user_id}/addresses | POST | Add address |
| **User** | /users/{user_id}/addresses | GET | List addresses |
| **User** | /users/{user_id}/addresses/{address_id} | PUT | Update address |
| **User** | /users/{user_id}/addresses/{address_id} | DELETE | Delete address |
| **Order** | /orders | POST | Create order |
| **Order** | /orders/{order_id} | GET | Get order |
| **Order** | /orders/users/{user_id}/orders | GET | List user orders |
| **Order** | /orders/{order_id}/status | PUT | Update status |
| **Order** | /orders/{order_id}/shipper | PUT | Assign shipper |
| **Order** | /orders/restaurants/{restaurant_id}/orders | GET | List restaurant orders |
| **Restaurant** | /restaurants | POST | Create restaurant |
| **Restaurant** | /restaurants | GET | List restaurants |
| **Restaurant** | /restaurants/{restaurant_id} | GET | Get restaurant |
| **Restaurant** | /restaurants/{restaurant_id}/menu-items | POST | Add menu item |
| **Restaurant** | /restaurants/{restaurant_id}/menu-items | GET | List menu items |
| **Restaurant** | /restaurants/{restaurant_id}/menu-items/{item_id} | PUT | Update menu item |
| **Restaurant** | /restaurants/{restaurant_id}/menu-items/{item_id} | DELETE | Delete menu item |
| **Shipper** | /shippers | POST | Create shipper |
| **Shipper** | /shippers/{shipper_id} | GET | Get shipper |
| **Shipper** | /shippers | GET | List available shippers |
| **Shipper** | /shippers/{shipper_id}/status | PUT | Update status |

---

## Inter-Service Communication

**Order Service validates external references:**
- When creating an order, `order-service` makes HTTP calls to:
  - `GET http://user-service:8000/users/{user_id}` — verify user exists
  - `GET http://restaurant-service:8000/restaurants/{restaurant_id}` — verify restaurant exists
  
If validation fails, the order creation is rejected with appropriate error codes (400 or 502).

---

## Status Codes Reference

- **200 OK** — Successful GET/PUT request
- **201 Created** — Successful POST request (resource created)
- **400 Bad Request** — Invalid input or validation failed
- **404 Not Found** — Resource not found
- **502 Bad Gateway** — Unable to reach dependent service
