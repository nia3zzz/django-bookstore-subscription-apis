from pydantic import BaseModel, UUID4
from datetime import datetime


class create_borrow_validators(BaseModel):
    book_id: UUID4
    user_id: UUID4
    to_return_at: datetime
