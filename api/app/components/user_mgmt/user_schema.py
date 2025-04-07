# app/schemas/user_schema.py

from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    email: EmailStr

class UserOut(BaseModel):
    id: str
    email: str
    date_created: datetime
    is_active: bool

    class Config:
        from__attributes = True
