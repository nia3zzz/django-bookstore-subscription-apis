from django.db import models
import uuid
from django.utils import timezone

BOOK_CATEGORIES = [
    (category, category)
    for category in [
        "Non-Fiction",
        "Science",
        "Fantasy",
        "History",
        "Biography",
        "Mystery",
        "Romance",
        "Thriller",
        "Horror",
        "Self-Help",
        "Health",
        "Travel",
        "Children",
        "Religion",
        "Science Fiction",
        "Poetry",
        "Comics",
        "Art",
        "Business",
        "Cooking",
        "Education",
        "Technology",
        "Sports",
        "Music",
        "Drama",
        "Philosophy",
        "Psychology",
        "Politics",
        "Adventure",
        "Anthology",
        "Dystopian",
        "Young Adult",
        "Classic",
        "Memoir",
        "True Crime",
        "Parenting",
        "Spirituality",
        "Environmental",
        "Crafts",
        "Short Stories",
        "Graphic Novels",
    ]
]


class Book(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_name = models.CharField(max_length=50)
    author_name = models.CharField(max_length=50)
    category = models.CharField(max_length=30, choices=BOOK_CATEGORIES)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.book_name} by {self.author_name}"
