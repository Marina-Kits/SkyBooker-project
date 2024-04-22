from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    contacts = models.CharField(max_length=250, blank=False, default='похоже, тут ничего нет...')

