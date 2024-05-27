from django.db import models
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model
from .tasks import send_update_notification

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
    subscribers = models.ManyToManyField(get_user_model(), related_name='flight_subscriptions')
    notified_subscribers = models.ManyToManyField(
        get_user_model(),
        related_name='notified_flight_subscriptions',
        blank=True
    )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_flight = Flight.objects.get(pk=self.pk)
            fields_to_check = ['departure_time', 'arrival_time']
            changes = {}
            for field in fields_to_check:
                old_value = getattr(old_flight, field)
                new_value = getattr(self, field)
                if old_value != new_value:
                    changes[field] = (old_value, new_value)

            super().save(*args, **kwargs)

            if changes:
                self.notify_subscribers(changes)
        else:
            super().save(*args, **kwargs)

    def notify_subscribers(self, changes):
        subscribers = self.subscribers.all().exclude(
            pk__in=self.notified_subscribers.all()
        )
        for subscriber in subscribers:
            send_update_notification.delay(subscriber.email, self.name, changes)
            self.notified_subscribers.add(subscriber)
        self.save()

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
    reminder_sent = models.BooleanField(default=False)

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

    def save(self, *args, **kwargs):
        if self.pk:
            original = FlightClassInfo.objects.get(pk=self.pk)
            if original.ticket_price != self.ticket_price or original.seats_number != self.seats_number:
                changes = {
                    'цена билета': (original.ticket_price, self.ticket_price),
                    'количество мест': (original.seats_number, self.seats_number),
                }
                subscribers = self.flight.subscribers.all()
                for subscriber in subscribers:
                    send_update_notification.delay(subscriber.email, self.flight.departure_airport.city, self.flight.arrival_airport.city, self.flight.departure_time.date(), self.flight.departure_time.time(), original.service_class, changes)
                self.flight.save()
        super().save(*args, **kwargs)