from numbers import Number
from db.base import Base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
import enum

class CallStatus(enum.Enum):
    ended="Ended"
    live="Live"
    scheduled="Scheduled"

class Call_Members(Base):
    __tablename__="call_members"

    call_id=Column(Integer, ForeignKey('calls.call_id'), primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey('users.id'), primary_key=True, index=True)
    
    

class Users(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    username=Column(String, unique=True, index=True, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    hashed_password=Column(String, nullable=False)

    calls =relationship('Calls', secondary='call_members', back_populates='members')



class Calls(Base):
    __tablename__="calls"

    call_id=Column(Integer, primary_key=True, index=True)
    host_id=Column(Integer, nullable=False)
    scheduled_at=Column(DateTime, nullable=True)
    started_at=Column(DateTime, nullable=True)
    ended_at=Column(DateTime, nullable=True)
    is_call_private=Column(Boolean, nullable=True)

    members=relationship('Users', secondary='call_members', back_populates='calls')



    @hybrid_property
    def call_duration(self):
        return self.ended_at - self.started_at
    
    @hybrid_property
    def call_status(self):
        if self.ended_at:
            return CallStatus.ended
        elif self.started_at and not self.ended_at:
            return CallStatus.live
        elif self.scheduled_at and not self.started_at:
            return CallStatus.scheduled
        


