
from pydantic import BaseModel, Field
from typing import Optional

class UserSchema(BaseModel):
    name: str
    email: str
    password: str
    active: Optional[bool] = True
    admin: Optional[bool] = False

    class Config:
        from_attributes = True    

class OrderSchema(BaseModel): 
    user_id: int
    car_id: int
    client_id: int
    discount: float = Field(default=0, ge=0, le=100)
    

    class Config:
        from_attributes = True       

class LoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True

class CarSchema(BaseModel):
    make: str
    model: str
    year: int
    price: float
    color: str
    mileage: int

    class Config:
        from_attributes = True

class ClientSchema(BaseModel):
    name: str
    document: str
    email: str
    phone: str

    class Config:
        from_attributes = True        
