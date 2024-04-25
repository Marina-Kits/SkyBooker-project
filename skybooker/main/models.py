from django.db import models


class Passenger(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name



class Tickets(models.Model):
    CLASS_CHOICES = (
        ('Э', 'Эконом'),
        ('К', 'Комфорт'),
        ('Б', 'Бизнес'),
        ('П', 'Первый класс'),
    )

    class_of_service = models.CharField(max_length=1, choices=CLASS_CHOICES)
    luggage = models.BooleanField(default=False)
