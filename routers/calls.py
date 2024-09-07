from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from utils.get_user import get_current_user
from Models import Calls, Users
from datetime import datetime

router = APIRouter()

class CallCreateRequest(BaseModel):
    is_call_private: bool

@router.post("/call")
def create_call(
    call_data:CallCreateRequest,
    db:Session=Depends(get_db),
    user:Users=Depends(get_current_user)
    ):
    len =db.query(Calls).count()
    new_call ={}
    new_call["host_id"]=user.id
    # new_call["call_members"]=[user.id]
    new_call["call_id"]=len+1
    new_call["is_call_private"]=call_data.is_call_private
    new_call["started_at"]=datetime.now()
    db.add(Calls(**new_call))
    db.commit()
    return {"message":"Call Scheduled Sucessfully", "call":new_call}

    
    




@router.get("/hosted/calls")
def get_hosted_calls(db:Session=Depends(get_db),user:Users=Depends(get_current_user)):
    return db.query(Calls).filter(Calls.host_id == user.id).all()

@router.get("/member/calls")
def get_member_calls(db:Session = Depends(get_db), user:Users=Depends(get_current_user)):
    return db.query(Calls).filter(user.id in Calls.call_members).all()





