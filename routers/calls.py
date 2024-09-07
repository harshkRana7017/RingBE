from fastapi import APIRouter, Depends
from main import get_current_user
from sqlalchemy.orm import Session
from db.database import get_db
from ..Models import Calls, Users
from datetime import datetime

router = APIRouter()

@router.post("/call")
def create_call(
    is_private_call:bool,
    db:Session=Depends(get_db),
    user:Users=Depends(get_current_user)
    ):
    len =len(db.query(Calls).all())
    new_call ={}
    new_call["host_id"]=user.id
    new_call["call_members"]=[user.id]
    new_call["call_id"]=len+1
    new_call["is_private_call"]=is_private_call
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





