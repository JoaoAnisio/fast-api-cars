# para rodar o código, executar no terminal: uvicorn main:app --reload

from fastapi import FastAPI

from auth_routes import auth_router
from car_routes import car_router
from client_routes import client_router
from order_routes import order_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)
app.include_router(car_router)
app.include_router(client_router)
