from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import take_session, verify_token
from schemas import OrderSchema, ResponseOrderSchema
from models import Car, Client, Order, User
from typing import List

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])

@order_router.get("/")
async def function_orders():
    return {"message": "Orders route"}


@order_router.post("/create_order")
async def create_order(order_schema: OrderSchema, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    car = session.query(Car).filter(Car.id == order_schema.car_id).first()
    client = session.query(Client).filter(Client.id == order_schema.client_id).first()
    if not car:
        raise HTTPException(status_code=400, detail="Car not found")
    elif not client:
        raise HTTPException(status_code=400, detail="Client not found")
    
    existing = session.query(Order).filter(
        Order.car_id == order_schema.car_id,
        Order.status != "CANCELED"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Car is already associated with an order.")

    new_order = Order(user_id=user.id, car_id=order_schema.car_id, client_id=order_schema.client_id)
    new_order.discount = order_schema.discount
    new_order.calculate_price(order_schema.discount, car)
    session.add(new_order)
    session.commit()
    return {"message": "Order created successfully.", "order_id": new_order.id}


@order_router.post("/order/cancel/{order_id}")
async def cancel_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to cancel orders.")
    order.status = "CANCELED"
    session.commit()
    return {
        "message": f"Order: {order.id} canceled successfully.",
        "order": order
    }

@order_router.get("/list_orders")
async def list_orders(session: Session = Depends(take_session), user: User = Depends(verify_token)):
    if not user.admin or not user.active:
        raise HTTPException(status_code=401, detail="You do not have permission to list all orders.")
    else:
        orders = session.query(Order).all()
        return {"orders": orders}

@order_router.get("/my_orders", response_model=List[ResponseOrderSchema])
async def list_my_orders(session: Session = Depends(take_session), user: User = Depends(verify_token)):
    orders = session.query(Order).filter(Order.user_id == user.id).all()
    return orders

@order_router.delete("/delete_order/{order_id}")
async def delete_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to delete orders.")
    session.delete(order)
    session.commit()
    return {
        "message": f"Order: {order.id} deleted successfully.",
        "order": order
    }

@order_router.post("/order/complete/{order_id}")
async def complete_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to complete orders.")
    order.status = "COMPLETED"
    session.commit()
    return {
        "message": f"Order: {order.id} completed successfully.",
        "order": order
    }

@order_router.get("/get_order/{order_id}")
async def get_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=400, detail="Order not found")
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=401, detail="You do not have permission to view this order.")
    return {
        "order": order
         }

