from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import Optional


class BookCategory(str, Enum):
    NON_FICTION = "Non-Fiction"
    SCIENCE = "Science"
    FANTASY = "Fantasy"
    HISTORY = "History"
    BIOGRAPHY = "Biography"
    MYSTERY = "Mystery"
    ROMANCE = "Romance"
    THRILLER = "Thriller"
    HORROR = "Horror"
    SELF_HELP = "Self-Help"
    HEALTH = "Health"
    TRAVEL = "Travel"
    CHILDREN = "Children"
    RELIGION = "Religion"
    SCIENCE_FICTION = "Science Fiction"
    POETRY = "Poetry"
    COMICS = "Comics"
    ART = "Art"
    BUSINESS = "Business"
    COOKING = "Cooking"
    EDUCATION = "Education"
    TECHNOLOGY = "Technology"
    SPORTS = "Sports"
    MUSIC = "Music"
    DRAMA = "Drama"
    PHILOSOPHY = "Philosophy"
    PSYCHOLOGY = "Psychology"
    POLITICS = "Politics"
    ADVENTURE = "Adventure"
    ANTHOLOGY = "Anthology"
    DYSTOPIAN = "Dystopian"
    YOUNG_ADULT = "Young Adult"
    CLASSIC = "Classic"
    MEMOIR = "Memoir"
    TRUE_CRIME = "True Crime"
    PARENTING = "Parenting"
    SPIRITUALITY = "Spirituality"
    ENVIRONMENTAL = "Environmental"
    CRAFTS = "Crafts"
    SHORT_STORIES = "Short Stories"
    GRAPHIC_NOVELS = "Graphic Novels"


class create_book_validator(BaseModel):
    book_name: str = Field(max_length=50)
    author_name: str = Field(max_length=50)
    category: BookCategory
    quantity: int = Field(default=1)


class get_books_query_validators(BaseModel):
    category: Optional[BookCategory] = Field(default=None)
    author_name: Optional[str] = Field(default=None)
    limit: Optional[int] = Field(default=10)
    offset: Optional[int] = Field(default=0)
