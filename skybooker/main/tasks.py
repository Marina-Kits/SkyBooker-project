from celery import shared_task
from datetime import datetime, timedelta
from .models import Ticket, FlightClassInfo, Flight
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def delete_expired_tickets():
    expiration_time = datetime.now() - timedelta(minutes=15)

    expired_tickets = Ticket.objects.filter(is_confirmed=False, booking_time__lte=expiration_time)

    for ticket in expired_tickets:
        flight_class_info = FlightClassInfo.objects.get(flight=ticket.flight, service_class=ticket.service_class)
        flight_class_info.seats_number += 1
        flight_class_info.save()
    expired_tickets.delete()


@shared_task
def send_flight_reminders():
    # Получить список всех рейсов, вылет которых завтра
    tomorrow = timezone.now() + timedelta(days=1)
    tomorrow_flights = Flight.objects.filter(
        departure_time__gte=tomorrow,
        departure_time__lt=tomorrow + timedelta(days=1)
    )

    # Отправить напоминание о каждом рейсе
    for flight in tomorrow_flights:
        # Получить список всех билетов, приобретенных на этот рейс
        flight_tickets = Ticket.objects.filter(flight=flight)

        # Отправить напоминание каждому пользователю, который приобрел билет на этот рейс
        for ticket in flight_tickets:
            # Проверить, было ли уже отправлено напоминание об этом рейсе
            if ticket.reminder_sent:
                continue

            subject = f"Напоминание о рейсе из {flight.departure_airport.city} в {flight.arrival_airport.city}"
            message = f"Ваш рейс из {flight.departure_airport.city} в {flight.arrival_airport.city} вылетает завтра {flight.departure_time} в {flight.departure_time.time()} по местному времени из аэропорта {flight.departure_airport.name}. Пожалуйста, не забудьте о своем билете и документах для полета."
            recipient_list = [ticket.passenger.users.all()[0].email]
            send_mail(
                subject=subject,
                message=message,
                from_email="no-reply@example.com",
                recipient_list=recipient_list,
            )

            # Отметить, что напоминание об этом рейсе было отправлено
            ticket.reminder_sent = True
            ticket.save()
