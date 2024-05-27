from celery import shared_task
from datetime import datetime, timedelta
from django.apps import apps
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def delete_expired_tickets():
    expiration_time = datetime.now() - timedelta(minutes=15)
    from main.models import Ticket, FlightClassInfo
    expired_tickets = Ticket.objects.filter(is_confirmed=False, booking_time__lte=expiration_time)

    for ticket in expired_tickets:
        flight_class_info = FlightClassInfo.objects.get(flight=ticket.flight, service_class=ticket.service_class)
        flight_class_info.seats_number += 1
        flight_class_info.save()
    expired_tickets.delete()


@shared_task
def send_flight_reminders():
    tomorrow = timezone.now() + timedelta(days=1)
    tomorrow_flights = apps.get_model('main', 'Flight').objects.filter(
        departure_time__gte=tomorrow,
        departure_time__lt=tomorrow + timedelta(days=1)
    )

    for flight in tomorrow_flights:
        flight_tickets = apps.get_model('main', 'Ticket').objects.filter(flight=flight)

        for ticket in flight_tickets:
            if ticket.reminder_sent:
                continue

            subject = f"Напоминание о рейсе из {flight.departure_airport.city} в {flight.arrival_airport.city}"
            message = f"Ваш рейс из {flight.departure_airport.city} в {flight.arrival_airport.city} вылетает завтра {flight.departure_time.date()} в {flight.departure_time.time()} по местному времени из аэропорта {flight.departure_airport.name}. Пожалуйста, не забудьте о своем билете и документах для полета."
            recipient_list = [ticket.passenger.users.all()[0].email]
            send_mail(
                subject=subject,
                message=message,
                from_email="no-reply@example.com",
                recipient_list=recipient_list,
            )

            ticket.reminder_sent = True
            ticket.save()


@shared_task
def send_update_notification(email, departure_city, arrival_city, departure_date, departure_time, service_class, changes):
    changes_str = ', '.join([f'{field}: {old} -> {new}' for field, (old, new) in changes.items()])
    message = f'Информация о рейсе {departure_city}-{arrival_city} на {departure_date} в {departure_time} была обновлена. Изменения цены билета и количества мест на класс обслуживания {service_class}: {changes_str}'

    send_mail(
        subject='Обновление информации о рейсе',
        message=message,
        from_email='noreply@example.com',
        recipient_list=[email],
        fail_silently=False,
    )