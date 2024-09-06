from db.base import Base
from sqlalchemy import Column, String, Integer, Date
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List
import enum

class CallStatus(enum.Enum):
    ended="Ended"
    live="Live"
    scheduled="Scheduled"

    

class Users(Base):
    __tablename__="users"

    id=Column(Integer, primary_key=True, index=True)
    username=Column(String, unique=True, index=True, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    hashed_password=Column(String, nullable=False)


class Calls(Base):
    __tablename__="calls"

    call_id=Column(Integer, primary_key=True, index=True)
    host_id=Column(Integer, nullable=False)
    scheduled_at=Column(Date, nullable=True)
    started_at=Column(Date, nullable=False)
    ended_at=Column(Date, nullable=True)
    call_members=Column(List[Integer], nullable=False)
    is_call_private=Column(bool, nullable=True)


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
        


