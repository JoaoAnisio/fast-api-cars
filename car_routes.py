from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import take_session, verify_token
from schemas import CarSchema
from models import Car, User

car_router = APIRouter(prefix="/cars", tags=["cars"], dependencies=[Depends(verify_token)])

@car_router.post("/add_car")
async def add_car(car_schema: CarSchema, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    if not user.admin:
        raise HTTPException(status_code=401, detail="You do not have permission to add cars.")
    new_car = Car(**car_schema.dict())
    session.add(new_car)
    session.commit()
    return {"message": f"Car added successfully. Car ID: {new_car.id}", "car": new_car}

@car_router.get("/list_cars")
async def list_cars(session: Session = Depends(take_session), user: User = Depends(verify_token)):
        cars = session.query(Car).all()
        return {"cars": cars}

@car_router.get("/get_car/{car_id}")
async def get_car(car_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    car = session.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"car": car}

