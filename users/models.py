from django.db import models
import uuid
from django.utils import timezone


# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=50,
    )
    email = models.EmailField(
        unique=True,
    )
    phone_number = models.CharField(max_length=15)
    membership_paid = models.BooleanField(default=False)
    password = models.CharField(
        max_length=300,
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
