from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session, sessionmaker

from config import ALGORITHM, SECRET_KEY, oauth2_scheme
from models import User, db

SessionLocal = sessionmaker(bind=db)


def take_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_user_from_token(token: str, expected_type: str, session: Session):
    invalid_token = HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(dic_info.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise invalid_token
    # Impede que um refresh token seja usado como access token (e vice-versa)
    if dic_info.get("type") != expected_type:
        raise invalid_token
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return user


def verify_token(token: str = Depends(oauth2_scheme), session: Session = Depends(take_session)):
    return get_user_from_token(token, "access", session)


def verify_refresh_token(token: str = Depends(oauth2_scheme), session: Session = Depends(take_session)):
    return get_user_from_token(token, "refresh", session)
