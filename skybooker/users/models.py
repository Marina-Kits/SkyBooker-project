from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    passengers = models.ManyToManyField('main.Passenger', related_name='users', blank=True)




