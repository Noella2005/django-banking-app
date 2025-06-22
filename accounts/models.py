from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    is_approved = models.BooleanField(default=False) # Approved by manager

    def __str__(self):
        return self.username
