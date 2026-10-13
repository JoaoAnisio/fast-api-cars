from models import db
from sqlalchemy.orm import sessionmaker, Session
from models import User
from fastapi import Depends
from jose import jwt, JWTError
from main import SECRET_KEY, ALGORITHM, oauth2_scheme

def take_session():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:    
        session.close()

def verify_token(token: str = Depends(oauth2_scheme), session: Session = Depends(take_session)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(dic_info.get("sub"))
    except JWTError:
        raise Exception(status_code=401, detail="Invalid token")
    user = session.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise Exception(status_code=401, detail="User not found")
    return user        