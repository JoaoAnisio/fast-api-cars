from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.orm import Session

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY, bcrypt_context
from dependencies import take_session, verify_refresh_token
from models import User
from schemas import LoginSchema, MessageResponse, UserSchema

auth_router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_token(user_id: int, token_type: str = "access", token_duration: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    expire = datetime.now(timezone.utc) + token_duration
    dict_to_encode = {"sub": str(user_id), "type": token_type, "exp": expire}
    return jwt.encode(dict_to_encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(email: str, password: str, session: Session):
    user = session.query(User).filter(User.email == email).first()
    if not user or not bcrypt_context.verify(password, user.password) or not user.active:
        return None
    return user


def invalid_credentials():
    return HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})


@auth_router.get("/")
async def function_auth():
    '''
    Essa é a rota padrão de autenticação do sistema
    '''
    return {"message": "Authentication route"}


@auth_router.post("/create_user", status_code=201, response_model=MessageResponse)
async def create_user(user_schema: UserSchema, session: Session = Depends(take_session)):
    if session.query(User).filter(User.email == user_schema.email).first():
        raise HTTPException(status_code=409, detail="User already exists")
    crypted_password = bcrypt_context.hash(user_schema.password)
    # Cadastro público cria sempre um usuário comum e ativo
    new_user = User(name=user_schema.name, email=user_schema.email, password=crypted_password, active=True, admin=False)
    session.add(new_user)
    session.commit()
    return {"message": f"User({user_schema.name}) created successfully"}


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = Depends(take_session)):
    user = authenticate_user(login_schema.email, login_schema.password, session)
    if not user:
        raise invalid_credentials()
    return {
        "access_token": create_token(user.id),
        "refresh_token": create_token(user.id, token_type="refresh", token_duration=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)),
        "token_type": "bearer",
    }


@auth_router.post("/login-form")
async def login_form(data_form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(take_session)):
    user = authenticate_user(data_form.username, data_form.password, session)
    if not user:
        raise invalid_credentials()
    return {"access_token": create_token(user.id), "token_type": "bearer"}


@auth_router.get("/refresh_token")
async def use_refresh_token(user: User = Depends(verify_refresh_token)):
    return {"access_token": create_token(user.id), "token_type": "bearer"}
