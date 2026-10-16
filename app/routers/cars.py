from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import take_session, verify_token
from app.models import Car, User
from app.schemas import CarSchema, ResponseCarSchema

car_router = APIRouter(prefix="/cars", tags=["cars"], dependencies=[Depends(verify_token)])


@car_router.post("/add_car", status_code=201, response_model=ResponseCarSchema)
async def add_car(car_schema: CarSchema, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    if not user.admin:
        raise HTTPException(status_code=403, detail="You do not have permission to add cars.")
    new_car = Car(**car_schema.model_dump())
    session.add(new_car)
    session.commit()
    return new_car


@car_router.get("/list_cars", response_model=List[ResponseCarSchema])
async def list_cars(session: Session = Depends(take_session)):
    return session.query(Car).all()


@car_router.get("/get_car/{car_id}", response_model=ResponseCarSchema)
async def get_car(car_id: int, session: Session = Depends(take_session)):
    car = session.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car
