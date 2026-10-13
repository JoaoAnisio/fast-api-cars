from fastapi import APIRouter, Depends, HTTPException
from models import User
from dependencies import take_session, verify_token
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UserSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm

auth_router = APIRouter(prefix="/auth", tags=["auth"])

def create_token(user_id: int,token_duration=timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))):
    expire = datetime.now(timezone.utc) + token_duration
    dict_to_encode = {"sub": str(user_id), "exp": expire}
    enconded_jwt = jwt.encode(dict_to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return enconded_jwt

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
        refresh_token = create_token(user.id, token_duration=timedelta(days=7))  # Token de refresh válido por 7 dias
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
            }

@auth_router.post("/login-form")
async def login_form(data_form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(take_session)):
    user = authenticate_user(data_form.username, data_form.password, session)
    if not user:
        raise HTTPException(status_code=400, detail="User not found or incorrect password")
    else:
        access_token = create_token(user.id)
        return {
            "access_token": access_token,
            "token_type": "bearer"
            }    

@auth_router.get("/refresh_token")
async def use_refresh_token(user: User = Depends(verify_token)):
    access_token = create_token(user.id)
    return {
        "access_token": access_token,        
        "token_type": "bearer"
        }