from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional

class create_borrow_validators(BaseModel):
    book_id: UUID4
    user_id: UUID4
    to_return_at: datetime

class get_borrows_validator(BaseModel):
    book_id: Optional[UUID4] = Field(default=None)
    user_id: Optional[UUID4] = Field(default=None)
    is_returned: Optional[bool] = Field(default=None)
    limit: Optional[int] = Field(default=10)
    offset: Optional[int] = Field(default=0)

class borrow_actions_validators(BaseModel):
    id: UUID4