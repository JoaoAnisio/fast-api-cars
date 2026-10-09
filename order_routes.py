from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies import take_session
from schemas import OrderSchema
from models import Order

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def function_orders():
    return {"message": "Orders route"}

@order_router.post("/create_order")
async def create_order(order_schema: OrderSchema, session = Depends(take_session)):
    new_order = Order(user_id=order_schema.user_id, car_id=order_schema.car_id)
    session.add(new_order)
    session.commit()
    return {"message": f"Order created successfully. Order ID: {new_order.id}"}