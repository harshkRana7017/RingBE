from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from requests import Session

from Models import Users
from db.database import get_db
from tokenfuncs import decode_acess_token


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session=Depends(get_db))->Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload=decode_acess_token(token)
        email:str =payload["sub"]
        if email is None:
            raise credentials_exception
        user=db.query(Users).filter(Users.email == email).first()
        if user is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    return user