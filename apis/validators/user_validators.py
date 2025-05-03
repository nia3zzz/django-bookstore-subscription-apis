from pydantic import BaseModel, EmailStr, Field, UUID4, model_validator
from enum import Enum
from typing import Optional


class FilterEnum(str, Enum):
    first_to_add = "first_to_add"
    last_to_add = "last_to_add"
    unpaid_member = "unpaid_member"


class create_user_validator(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=14)
    password: str = Field(min_length=6)
    membership_paid: bool


class update_membership_validator(BaseModel):
    id: UUID4


class get_users(BaseModel):
    filter_by: Optional[FilterEnum] = Field(default=None)
    limit: int = Field(default=10)
    offset: int = Field(default=0)


class UpdateUser(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=14)
