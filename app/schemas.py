from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    name: str
    email: str
    password: str


class LoginSchema(BaseModel):
    email: str
    password: str


class CarSchema(BaseModel):
    make: str
    model: str
    year: int
    price: float
    color: str
    mileage: int


class ClientSchema(BaseModel):
    name: str
    document: str
    email: str
    phone: str


class OrderSchema(BaseModel):
    car_id: int
    client_id: int
    discount: float = Field(default=0, ge=0, le=100)


class MessageResponse(BaseModel):
    message: str


class ResponseCarSchema(CarSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ResponseClientSchema(ClientSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ResponseOrderSchema(BaseModel):
    id: int
    car_id: int
    client_id: int
    status: str
    car_price: float
    total_price: float
    discount: float | None = Field(default=0, ge=0, le=100)
    order_date: datetime

    model_config = ConfigDict(from_attributes=True)
