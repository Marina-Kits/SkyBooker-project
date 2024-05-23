from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    passengers = models.ManyToManyField('main.Passenger', related_name='users', blank=True)


class EmailConfirmationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


