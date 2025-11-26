# Microservices Architecture - Food Delivery System

## 📋 Project Overview

This is a complete microservices-based food delivery system built with FastAPI, MongoDB, and Docker. The system is decomposed into domain-driven services, each with its own database.

## 🏗️ Architecture

### Services:

1. **User Service** (Port 8001)
   - Manages user registration and profile
   - Database: MongoDB `user_db`
   - Endpoints: POST/GET `/users`

2. **Order Service** (Port 8002)
   - Manages orders and order tracking
   - Database: MongoDB `order_db`
   - Endpoints: POST/GET `/orders`

### Infrastructure:

- **MongoDB 6.0** (Port 27017)
  - Root credentials: `root:password`
  - Separate databases for each service

### Communication:

- Services communicate via REST APIs
- Services are isolated with separate data stores (Database per Service pattern)
- Network: `microservices_network` (Docker bridge network)

## 📁 Project Structure

```
project/
├── docker-compose.yml
├── user-service/
│   ├── Dockerfile
# Microservices Food Delivery — README (Consolidated)

This repository now keeps only `README.md` as the single documentation file. All other auxiliary markdown files were removed to simplify the project root. Important instructions and quick references are below.

Summary
-------
- Project: Microservices prototype (FastAPI + MongoDB + Docker)
- Services included (implemented/prototyped):
  - `user-service` (port 8001) — users, addresses
  - `order-service` (port 8002) — orders, inter-service validation
  - `restaurant-service` (port 8003) — restaurants & menu (implemented)
  - `shipper-service` (port 8004) — shippers (implemented)
- Database: MongoDB (single container) with separate databases per service (e.g., `user_db`, `order_db`).

What's changed
--------------
- Removed other `.md` files — this `README.md` is the consolidated doc.
- POST endpoints now return HTTP `201 Created` for creations.
- `order-service` performs synchronous HTTP validation calls to `user-service` and `restaurant-service` before creating an order (uses `httpx`).
- Database connections use a short retry + ping logic on startup to reduce failures while Mongo is booting.
- A `smoke_test.ps1` script was added at repo root to run a basic integration smoke test locally on Windows PowerShell.

Quick Start (run everything)
----------------------------
Prerequisites:
- Docker and Docker Compose installed on your machine.

Commands (PowerShell):
```powershell
cd C:\Users\AnThiwn\Desktop\project
docker-compose up --build
```

Stop and remove containers:
```powershell
docker-compose down
docker-compose down -v   # remove volumes (DB data)
```

Smoke test (PowerShell)
-----------------------
After services start, run the included script to create sample user, restaurant and an order:
```powershell
.\smoke_test.ps1
```
The script waits for health endpoints, then posts test data and prints the created resources.

Health endpoints (quick checks)
-------------------------------
- User service:  http://localhost:8001/health
- Order service: http://localhost:8002/health
- Restaurant:    http://localhost:8003/health
- Shipper:       http://localhost:8004/health

Important API notes
-------------------
- POST endpoints return `201 Created` on success.
- `order-service` validates `user_id` and `restaurant_id` by calling the other services; if user or restaurant is missing it returns `400 Bad Request`. If a dependent service is unreachable it returns `502 Bad Gateway`.

Selected endpoints (examples)
----------------------------
User Service (port 8001)
- POST `/users` — create user. Request: `{ "username": "...", "email": "..." }`. Response: `201` with user object and `id`.
- GET `/users/{user_id}` — get user by id.

Order Service (port 8002)
- POST `/orders` — create order. Request: `{ "user_id":"..", "restaurant_id":"..", "items":[{"menu_item_id":"..","quantity":1}] }`.
  - Validates user & restaurant before insert.
- GET `/orders/{order_id}` — get order by id.

Notes about running and debugging
--------------------------------
- Logs: `docker-compose logs -f` to follow logs. Use `docker-compose logs order-service` to inspect specific service logs.
- If MongoDB is not ready, services now retry a few times on startup; check logs if they still fail.
- When testing across services, the container names (`user-service`, `order-service`, `restaurant-service`) are used as hostnames inside the Docker network. If you run services outside Docker, set env vars `USER_SERVICE_URL` and `RESTAURANT_SERVICE_URL` for `order-service` to point to reachable addresses.

Next steps (recommended)
------------------------
1. Add authentication (JWT) across services.
2. Add API Gateway (optional) to unify client access.
3. Add healthchecks in `docker-compose.yml` for Mongo and services.
4. Add simple pytest tests for key endpoints.

If you want, I can now:
- (A) Add an API Gateway prototype.
- (B) Add pytest tests for `user-service` and `order-service`.
- (C) Add healthchecks to `docker-compose.yml` and improve start ordering.

## Additional Documentation

**API Design Documentation:** See `API_DESIGN.md` for detailed API specifications including all endpoints, HTTP methods, request/response bodies, and business purposes for each service.

**Demo Guide:** See `DEMO_GUIDE.md` for step-by-step instructions on running the system, testing APIs, and architectural Q&A talking points.

---
Location of important scripts and files
- `docker-compose.yml` — orchestrates Mongo + services
- `smoke_test.ps1` — PowerShell smoke test script
- `API_DESIGN.md` — Detailed API endpoint documentation (requirement 3.3)
- `DEMO_GUIDE.md` — Demo walkthrough and architectural discussion points (requirement 4.3)
- `user-service/`, `order-service/`, `restaurant-service/`, `shipper-service/` — service folders

Contact me which next step you prefer and I will implement it.
