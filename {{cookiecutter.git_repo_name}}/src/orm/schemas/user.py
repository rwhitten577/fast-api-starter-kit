import pytz
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, validator

from src.orm.schemas.db_base import DBBase


# Shared properties
class UserBase(BaseModel):
    full_name: Optional[str]
    given_name: Optional[str]
    email: Optional[EmailStr]
    age: Optional[int]
    gender: Optional[int]
    timezone: Optional[str]
    notifications_enabled: Optional[bool] = True
    email_enabled: Optional[bool] = True
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    sub: str
    full_name: str
    given_name: str
    email: EmailStr
    timezone: str

    @validator('timezone')
    def valid_timezone(cls, v):
        try:
            pytz.timezone(v)
        except pytz.UnknownTimeZoneError:
            raise ValueError('Invalid timezone')
        return v


# Properties to receive via API on update
class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase, DBBase):
    pass


# Additional properties to return via API
class User(UserInDBBase):
    sub: UUID
