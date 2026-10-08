
from pydantic import BaseModel
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
    

    class Config:
        from_attributes = True       