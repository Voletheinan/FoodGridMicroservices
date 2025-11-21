from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import orders

app = FastAPI(title="Order Service", version="1.0.0")


@app.on_event("startup")
async def startup():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


app.include_router(orders.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "order-service"}
