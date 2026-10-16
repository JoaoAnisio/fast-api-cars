# para rodar o código, executar no terminal: uvicorn app.main:app --reload

from fastapi import FastAPI

from app.routers.auth import auth_router
from app.routers.cars import car_router
from app.routers.clients import client_router
from app.routers.orders import order_router

app = FastAPI(title="Fast API Cars", description="API de gestão de vendas de carros", version="1.0.0")

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(car_router)
app.include_router(client_router)
