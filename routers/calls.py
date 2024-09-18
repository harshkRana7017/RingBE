from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from Schemas.call import CreateCall
from db.database import get_db
from utils.get_user import get_current_user
from Models import Calls, Users
from datetime import datetime

router = APIRouter()



@router.post("/call")
def create_call(
    call_data:CreateCall,
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


@router.post('/call/end/{call_id}')
def end_call(
    call_id:int,
    db:Session=Depends(get_db),
    user:Users=Depends(get_current_user)
):
    if user:
        call = db.query(Calls).filter(Calls.call_id == call_id).first()
        call.ended_at = datetime.now()
        db.commit()
        return {"message":"Call Ended Sucessfully"}
    




@router.get("/calls/hosted")
def get_hosted_calls(db:Session=Depends(get_db),user:Users=Depends(get_current_user)):
    return db.query(Calls).filter(Calls.host_id == user.id).all()

@router.get("/calls/members")
def get_member_calls(db:Session = Depends(get_db), user:Users=Depends(get_current_user)):
    return db.query(Calls).filter(user.id in Calls.call_members).all()





