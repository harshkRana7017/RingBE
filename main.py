from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from Schemas.user import LoginUser, SignUpUser
from sqlalchemy.orm import Session
from tokenfuncs import create_acess_token, decode_acess_token
from db.database import get_db
from Models import Users
from hashing import verify_password, hashPassword
import jwt 




app = FastAPI()

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


@app.get("/")
def read_route(request: Request):
    return {"message": "Hello World"}

@app.post("/signup")
def signup(request:Request, userData: SignUpUser, db:Session=Depends(get_db)):
    new_user = Users(username=userData.username, email=userData.email, hashed_password=hashPassword(userData.password))
    db.add(new_user)
    db.commit()
    return {"message":"done"}

@app.get("/users")
def get_users(request:Request, db:Session=Depends(get_db)):
   users = db.query(Users).all()
   return users


@app.get("/login")
def get_token(request:Request, userData:LoginUser, db:Session = Depends(get_db)):
     user =db.query(Users).filter(Users.email == userData.email).first()
     if user:
        if  verify_password(userData.password, user.hashed_password):
           token= create_acess_token(data={"sub": user.email})
           return {"token": token}
        else:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect Passwor")
     else:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
     

     



          
   
