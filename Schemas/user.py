from pydantic import BaseModel, EmailStr
class LoginUser(BaseModel):
    email:EmailStr
    password:str

class SignUpUser(BaseModel):
    username:str
    email:EmailStr
    password:str

    

