from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import take_session, verify_token
from schemas import ClientSchema
from models import  Client, User

client_router = APIRouter(prefix="/clients", tags=["clients"], dependencies=[Depends(verify_token)])

@client_router.post("/add_client")
async def add_client(client_schema: ClientSchema, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    new_client = Client(**client_schema.dict())
    session.add(new_client)
    session.commit()
    return {"message": f"Client added successfully. Client ID: {new_client.id}", "client": new_client}

@client_router.get("/list_clients")
async def list_clients(session: Session = Depends(take_session), user: User = Depends(verify_token)):
        clients = session.query(Client).all()
        return {"clients": clients}

@client_router.get("/get_client/{client_id}")
async def get_client(client_id: int, session: Session = Depends(take_session), user: User = Depends(verify_token)):
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"client": client}