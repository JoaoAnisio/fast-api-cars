from fastapi import APIRouter, Depends, HTTPException
from models import User
from dependencies import take_session
from main import bcrypt_context
from schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(user_id: int):
    token = f"your_token_here_{user_id}" 
    return token

def authenticate_user(email: str, password: str, session: Session):
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return False
    elif not bcrypt_context.verify(password, user.password):
        return False
    return user

@auth_router.get("/")
async def function_auth():
    '''
    Essa é a rota padrão de autenticação do sitema
    '''
    return {"message": "Authentication route"}

@auth_router.post("/create_user")
async def create_user(user_schema: UserSchema, session: Session = Depends(take_session)):
    usuario = session.query(User).filter(User.email == user_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="User already exists")
    else:
        crypted_password = bcrypt_context.hash(user_schema  .password)
        new_user = User(name=user_schema.name, email=user_schema.email, password=crypted_password, active=user_schema.active, admin=user_schema.admin)
        session.add(new_user)
        session.commit()
        raise HTTPException(status_code=201, detail=f"User({user_schema.name}) created successfully")

@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(take_session)):
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found or incorrect password")
    else:
        access_token = create_token(user.id)
        return {"access_token": access_token, "token_type": "bearer"}