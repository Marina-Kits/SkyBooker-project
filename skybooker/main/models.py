from django.db import models
from django.utils import timezone
from datetime import datetime


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


class Airport(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, {self.city}"


class Flight(models.Model):
    airline = models.CharField(max_length=100, default='Unknown Airline')
    departure_airport = models.ForeignKey(Airport, related_name='departures', on_delete=models.CASCADE)
    arrival_airport = models.ForeignKey(Airport, related_name='arrivals', on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"Flight from {self.departure_airport} to {self.arrival_airport}"


class Ticket(models.Model):
    CLASS_CHOICES = (
        ('economy', 'Эконом'),
        ('comfort', 'Комфорт'),
        ('business', 'Бизнес'),
        ('first_class', 'Первый класс'),
    )

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='tickets')
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='tickets')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    luggage_price = models.DecimalField(max_digits=10, decimal_places=2)
    luggage = models.BooleanField(default=False)
    service_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    booking_time = models.DateTimeField(default=timezone.now)
    is_confirmed = models.BooleanField(default=False)

    def calculate_price(self):
        flight_class_info = FlightClassInfo.objects.get(flight=self.flight, service_class=self.flight_class)
        return flight_class_info.ticket_price, flight_class_info.luggage_price

    def save(self, *args, **kwargs):
        if not self.price or not self.luggage_price:
            self.price, self.luggage_price = self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Билет до {self.flight} - {self.passenger}'


class FlightClassInfo(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    service_class = models.CharField(max_length=20, choices=Ticket.CLASS_CHOICES)
    seats_number = models.IntegerField(default=0)
    luggage_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.flight} - {self.service_class}"