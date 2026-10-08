from fastapi import APIRouter, Depends
from models import user
from dependencies import take_session


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def function_auth():

    '''
    Essa é a função padrão de autenticação do sitema
    '''

    return {"message": "Authentication route"}

@auth_router.post("/create_user")
async def create_user(email: str, password: str, name: str, session = Depends(take_session)):
    usuario = session.query(user).filter(user.email == email).first()
    if usuario:
        return {"message": "User already exists"}
    else:
        new_user = user(name=name, email=email, password=password)
        session.add(new_user)
        session.commit()
        return {"message": "User created successfully"}
   