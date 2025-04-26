from django.db import models
from django.utils import timezone
import uuid
from books.models import Book
from users.models import User


# Create your models here.
class Borrow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(default=timezone.now)
    to_return_at = models.DateTimeField()

    def __str__(self):
        return self.to_return_at
