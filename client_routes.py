from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from dependencies import take_session, verify_token
from models import Client
from schemas import ClientSchema, ResponseClientSchema

client_router = APIRouter(prefix="/clients", tags=["clients"], dependencies=[Depends(verify_token)])


@client_router.post("/add_client", status_code=201, response_model=ResponseClientSchema)
async def add_client(client_schema: ClientSchema, session: Session = Depends(take_session)):
    existing = session.query(Client).filter(
        or_(Client.document == client_schema.document, Client.email == client_schema.email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Client with this document or email already exists")
    new_client = Client(**client_schema.model_dump())
    session.add(new_client)
    session.commit()
    return new_client


@client_router.get("/list_clients", response_model=List[ResponseClientSchema])
async def list_clients(session: Session = Depends(take_session)):
    return session.query(Client).all()


@client_router.get("/get_client/{client_id}", response_model=ResponseClientSchema)
async def get_client(client_id: int, session: Session = Depends(take_session)):
    client = session.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
