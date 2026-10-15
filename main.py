# para rodar o código, executar no terminal: uvicorn main:app --reload

from fastapi import FastAPI
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente '{name}' não definida. Crie o arquivo .env com SECRET_KEY, ALGORITHM e ACCESS_TOKEN_EXPIRE_MINUTES.")
    return value

SECRET_KEY = get_required_env("SECRET_KEY")
ALGORITHM = get_required_env("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_required_env("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")

from auth_routes import auth_router
from order_routes import order_router
from car_routes import car_router
from client_routes import client_router

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(car_router)
app.include_router(client_router)
