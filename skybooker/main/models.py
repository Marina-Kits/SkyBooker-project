from django.db import models


class Passenger(models.Model):
    GENDER_CHOICES = (
        ('M', 'Мужчина'),
        ('F', 'Женщина'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=255)

    def __str__(self):
        return self.full_name


class Tickets(models.Model):
    CLASS_CHOICES = (
        ('economy', 'Эконом'),
        ('comfort', 'Комфорт'),
        ('business', 'Бизнес'),
        ('first_class', 'Первый класс'),
    )

    service_class = models.CharField(max_length=20, choices=CLASS_CHOICES, default='economy')
    luggage = models.BooleanField(default=False)


class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, {self.city}"


class Flight(models.Model):
    departure_airport = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE)
    arrival_airport = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"Flight from {self.departure_airport} to {self.arrival_airport}"


class FlightClassInfo(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    service_class = models.CharField(max_length=20, choices=Tickets.CLASS_CHOICES)
    seats_number = models.IntegerField()
    luggage_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.flight} - {self.service_class}"
