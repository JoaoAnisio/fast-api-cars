from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.config import MAX_DISCOUNT_SELLER
from app.dependencies import take_session, verify_token
from app.models import Car, Client, Order, OrderStatus, User
from app.schemas import MessageResponse, OrderSchema, ResponseOrderSchema

order_router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(verify_token)])


def get_order_for_user(order_id: int, action: str, session: Session, user: User) -> Order:
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not user.admin and user.id != order.user_id:
        raise HTTPException(status_code=403, detail=f"You do not have permission to {action} this order.")
    return order


@order_router.post("/create_order", status_code=201)
async def create_order(order_schema: OrderSchema, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    if order_schema.discount > MAX_DISCOUNT_SELLER and not user.admin:
        raise HTTPException(status_code=403, detail=f"Discount above {MAX_DISCOUNT_SELLER:g}% requires admin approval.")

    car =session.query(Car).filter(Car.id == order_schema.car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    client = session.query(Client).filter(Client.id == order_schema.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    existing = session.query(Order).filter(
        Order.car_id == order_schema.car_id,
        Order.status != OrderStatus.CANCELED.value
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Car is already associated with an order.")

    new_order = Order(user_id=user.id, car_id=order_schema.car_id, client_id=order_schema.client_id)
    new_order.discount = order_schema.discount
    new_order.calculate_price(order_schema.discount, car)
    session.add(new_order)
    session.commit()
    return {"message": "Order created successfully.", "order_id": new_order.id}


@order_router.post("/order/cancel/{order_id}", response_model=ResponseOrderSchema)
async def cancel_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    order = get_order_for_user(order_id, "cancel", session, user)
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Only pending orders can be canceled.")
    order.status = OrderStatus.CANCELED.value
    session.commit()
    return order


@order_router.post("/order/complete/{order_id}", response_model=ResponseOrderSchema)
async def complete_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    order = get_order_for_user(order_id, "complete", session, user)
    if order.status != OrderStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Only pending orders can be completed.")
    order.status = OrderStatus.COMPLETED.value
    session.commit()
    return order


@order_router.get("/list_orders", response_model=List[ResponseOrderSchema])
async def list_orders(session: Session = Depends(take_session), user: User = Depends(verify_token)):
    if not user.admin:
        raise HTTPException(status_code=403, detail="You do not have permission to list all orders.")
    return session.query(Order).options(joinedload(Order.car)).all()


@order_router.get("/my_orders", response_model=List[ResponseOrderSchema])
async def list_my_orders(session: Session = Depends(take_session), user: User = Depends(verify_token)):
    return session.query(Order).options(joinedload(Order.car)).filter(Order.user_id == user.id).all()


@order_router.get("/get_order/{order_id}", response_model=ResponseOrderSchema)
async def get_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    return get_order_for_user(order_id, "view", session, user)


@order_router.delete("/delete_order/{order_id}", response_model=MessageResponse)
async def delete_order(order_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    order = get_order_for_user(order_id, "delete", session, user)
    session.delete(order)
    session.commit()
    return {"message": f"Order: {order_id} deleted successfully."}
