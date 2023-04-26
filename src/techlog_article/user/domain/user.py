from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    id: UUID
    username: str
    hashed_password: str = Field(description="Store the hashed value of the password")
    email: str

    deleted_at: Optional[datetime] = Field(
        description="This is for checking whether the user data is deleted(signed out)"
    )

    class Config:
        orm_mode = True