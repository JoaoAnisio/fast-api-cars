from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.get("/")
async def function_auth():

    '''
    Essa é a função padrão de autenticação do sitema
    '''

    return {"message": "Authentication route"}

