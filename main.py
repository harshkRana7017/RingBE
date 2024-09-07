from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from Schemas.user import LoginUser, SignUpUser
from fastapi.middleware.cors import CORSMiddleware 
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from tokenfuncs import create_access_token, decode_acess_token
from db.database import get_db
from Models import Users
from hashing import verify_password, hashPassword
from .routers import calls
import jwt 
import requests




app = FastAPI()
GOOGLE_CLIENT_ID ='754188762868-ak6bqkjap4jkldoof6oqu5doe2u090t0.apps.googleusercontent.com'


origins = [
    "http://localhost:5173",  # React app
    "http://localhost:8000",  # FastAPI app (if you ever need to call APIs from the same origin)
    # Add other origins as needed
]

app.add_middleware(CORSMiddleware, 
                   allow_origins=origins, 
                   allow_credentials=True, 
                   allow_methods=["*"],
                   allow_headers=["*"]
                   )
                   

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


app.include_router(calls.router)

class TokenRequest(BaseModel):
    token: str
    
@app.post('/auth/google')
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
        return {"access_token": access_token, "token_type": "bearer", "user":user_dict}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token or Google authentication failed"
        )


@app.get("/")
def read_route(request: Request):
    return {"message": "Hello World"}

@app.post("/signup")
def signup(request:Request, userData: SignUpUser, db:Session=Depends(get_db)):
    new_user = Users(username=userData.username, email=userData.email, hashed_password=hashPassword(userData.password))
    db.add(new_user)
    db.commit()
    return {"message":"User created Sucessfully"}

@app.get("/users")
def get_users(request:Request, db:Session=Depends(get_db)):
   users = db.query(Users).all()
   return users


@app.post("/login")
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
     

     



          
   
