from pydantic import BaseModel, EmailStr, Field


class create_user_validator(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone_number: str = Field(max_length=14)
    password: str = Field(min_length=6)
    membership_paid: bool
