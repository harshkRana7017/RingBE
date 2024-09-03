from db.base import Base
from sqlalchemy import Column, String, Integer

class Users(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    username=Column(String, unique=True, index=True, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    hashed_password=Column(String, nullable=False)