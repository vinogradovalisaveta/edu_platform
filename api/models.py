import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z/-]+$")


class TunedModel(BaseModel):
    class Config:
        orm_mode = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    first_name: str
    last_name: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

    @validator("first_name")
    def validate_first_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="name should contain only letters"
            )
        return value

    @validator("last_name")
    def validate_last_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=422, detail="name can contain letters only")
        return value
