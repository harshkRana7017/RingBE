from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreateCall(BaseModel):
    # call_members:Optional[list]
    is_call_private:bool
    scheduled_at:Optional[datetime]
    