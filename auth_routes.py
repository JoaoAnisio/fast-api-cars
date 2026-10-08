from fastapi import APIRouter, Depends, HTTPException
from models import user
from dependencies import take_session
from main import bcrypt_context
from schemas import UserSchema
from sqlalchemy.orm import Session


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def function_auth():
    '''
    Essa é a rota padrão de autenticação do sitema
    '''
    return {"message": "Authentication route"}

@auth_router.post("/create_user")
async def create_user(user_schema: UserSchema, session: Session = Depends(take_session)):
    usuario = session.query(user).filter(user.email == user_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        crypted_password = bcrypt_context.hash(user_schema  .password)
        new_user = user(name=user_schema.name, email=user_schema.email, password=crypted_password, active=user_schema.active, admin=user_schema.admin)
        session.add(new_user)
        session.commit()
        raise HTTPException(status_code=201, detail=f"User({user_schema.name}) created successfully")
    