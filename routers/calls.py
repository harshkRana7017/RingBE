from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Integer
from sqlalchemy.orm import Session
from Schemas.call import CreateCall
from db.database import get_db
from utils.get_user import get_current_user
from Models import Calls, Users
from datetime import datetime

router = APIRouter()


# Create call
@router.post("/call")
def create_call(
    call_data:CreateCall,
    db:Session=Depends(get_db),
    user:Users=Depends(get_current_user)
    ):
    len =db.query(Calls).count()
    new_call = Calls(
        host_id=user.id,
        call_id=len + 1,
        is_call_private=call_data.is_call_private,
        scheduled_at=call_data.scheduled_at if call_data.scheduled_at else None,
        started_at=datetime.now() if not call_data.scheduled_at else None
    )
    member_ids = call_data.member_ids
    call_members=[]
    if member_ids :
         for member_id in member_ids:
                current_member=db.query(Users).filter(Users.id == member_id).first()
                if not current_member:
                    raise HTTPException(status_code=404, detail=f"User with id {member_id} not found")
                call_members.append(current_member)
    
    new_call.members = call_members
    db.add(new_call)
    db.commit()
    db.refresh(new_call)
    return {"message":"Call Scheduled Sucessfully", "call":new_call}


#End call
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
    
# reschedule call
@router.post('/call/reschedule/{call_id}')
def reschedule_call(call_id:int,
                    reschedule_time:datetime,
                    db:Session = Depends(get_db),
                    user:Users =Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Unsuccessful")
    call = db.query(Calls).filter(Calls.call_id == call_id).first()
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")
    if user.id not in call.members:
        raise HTTPException(status_code=403, detail="You are not a member of this call")
    call.scheduled_at = reschedule_time
    db.commit()
    return {"message":"Call Rescheduled Sucessfully"} 



# Get all hosted Calls by a User
@router.get("/calls/hosted")
def get_hosted_calls(db:Session=Depends(get_db),user:Users=Depends(get_current_user)):
    return db.query(Calls).filter(Calls.host_id == user.id).all()

# Get all calls for which user is a member 
@router.get("/member/calls")
def get_member_calls(db:Session = Depends(get_db), user:Users=Depends(get_current_user)):
    selected_user = db.query(Users).filter(Users.id  == user.id).first()
    if not selected_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {'user_calls' :selected_user.calls}

# Get Call from Call Id
@router.get("/call/{call_id}")
def get_call_members(call_id:int,db:Session = Depends(get_db), user:Users= Depends(get_current_user),):
    call = db.query(Calls).filter(Calls.call_id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail='Call not found')
    if user.id not in call.members:
        raise HTTPException(status_code=403, detail="You are not a member of this call")
    return  {"call": call, "members": call.members}

# Add Call Members to a Call
@router.post("/call/add/members")
def add_members(member_ids:List[int],
                id:Optional[int],
                db:Session = Depends(get_db), 
                user:Users=Depends(get_current_user)):
    if id and user:
        call =db.query(Calls).filter(Calls.call_id == id).first()

        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        
        call_members = []
        for member_id in member_ids:
            current_member=db.query(Users).filter(Users.id == member_id).first()
            if current_member not in call.members:
                call_members.append(current_member)

        call.members.extend(call_members)
        db.commit()
        return{"message":"call members added"}

    raise HTTPException(status_code=404,detail="Call not found")

    
# Removing Call Members
@router.post("/call/remove/members")
def remove_members(
    member_ids: List[int],
    id: int,
    db: Session = Depends(get_db), 
    user: Users = Depends(get_current_user)):
    call = db.query(Calls).filter(Calls.call_id == id).first()

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    if call.host_id != user.id:
        raise HTTPException(status_code=403, detail="Only the host can remove members")
    
    call.members=[member for member in call.members if member.id  not in member_ids]
    db.commit()

    return{"message":"members deleted sucessfully"}

 


            







