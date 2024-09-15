from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from requests import Session
import requests
from sqlalchemy import inspect

from Models import Users
from Schemas.user import ForgotPass, LoginUser, SignUpUser
from db.database import get_db
from hashing import hashPassword, verify_password
from tokenfuncs import create_access_token
from utils.get_user import get_current_user

router = APIRouter()

GOOGLE_CLIENT_ID ='754188762868-ak6bqkjap4jkldoof6oqu5doe2u090t0.apps.googleusercontent.com'
class TokenRequest(BaseModel):
    token: str
    
@router.post('/auth/google')
def get_token(token_request: TokenRequest, db:Session = Depends(get_db)):
    try:
        
        response= requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token_request.token}")
        id_info=response.json()

        if id_info['aud'] != GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=400, detail="Invalid Google Client ID")
        user = db.query(Users).filter(Users.email == id_info['email']).first()
        id =len(db.query(Users).all()) +1
        if user is None:
            user=Users(
                email=id_info['email'],
                username=id_info['name'],
                hashed_password="",  # No password for Google sign-in,
                id=id
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        user_dict = {
            c.key:getattr(user, c.key)  
            for c in inspect(user).mapper.column_attrs 
            if c.key !='hashed_password'
            }
        access_token = create_access_token(data={"sub": user.email})
        return {"token": access_token, "user":user_dict}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token or Google authentication failed"
        )


@router.get("/")
def read_route(request: Request):
    return {"message": "Hello World"}


@router.post("/signup")
def signup(request:Request, userData: SignUpUser, db:Session=Depends(get_db)):
    new_user = Users(username=userData.username, email=userData.email, hashed_password=hashPassword(userData.password))
    db.add(new_user)
    db.commit()
    return {"message":"User created Sucessfully"}

@router.get("/users")
def get_users(request:Request, db:Session=Depends(get_db)):
   users = db.query(Users).all()
   return users


@router.post("/login")
def get_token(request:Request, userData:LoginUser, db:Session = Depends(get_db)):
     user =db.query(Users).filter(Users.email == userData.email).first()
     if user:
        if  verify_password(userData.password, user.hashed_password):
           token= create_access_token(data={"sub": user.email})
           return {"user":{"username":user.username, "id":user.id, "email":user.email},"token": token}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Passwor")
     else:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
     
@router.get('/fetch/me')
def fetch_me(db: Session = Depends(get_db), user: Users = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

@router.post('/forgot-password')
def forgot_password(user_data:ForgotPass,db:Session= Depends(get_db) ):
        user=db.query(Users).filter(Users.email ==user_data.email).first()
        if not user:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found with this email"
        )
        else:
            user.hashed_password=hashPassword(user_data.new_pass)
            db.commit()
            return {"message":"password changed sucessfully"}
     

     



          
   
