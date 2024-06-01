from celery import shared_task, current_app
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


@shared_task
def send_flight_change_notification(flight_id, old_departure_time, old_arrival_time, new_departure_time, new_arrival_time):
    from main.models import Flight, Ticket
    flight = Flight.objects.get(id=flight_id)
    departure_city = flight.departure_airport.city
    arrival_city = flight.arrival_airport.city

    tickets = Ticket.objects.filter(flight_id=flight_id)

    for ticket in tickets:
        subject = f"Изменение времени рейса {departure_city} - {arrival_city}"
        message = f"Время рейса {departure_city} - {arrival_city} изменено. Новое время отправления: {new_departure_time}, время прибытия: {new_arrival_time}."
        recipient_list = [ticket.passenger.users.all()[0].email]
        send_mail(
            subject=subject,
            message=message,
            from_email="no-reply@example.com",
            recipient_list=recipient_list,
        )


'''@shared_task
def generate_flights(departure_airport_id):
    from main.models import Flight, Airport, FlightClassInfo, Ticket

    # Получить выбранный аэропорт отправления
    departure_airport = Airport.objects.get(id=departure_airport_id)

    # Получить список всех аэропортов, кроме выбранного аэропорта отправления
    arrival_airports = [a for a in Airport.objects.all() if a != departure_airport]

    for arrival_airport in arrival_airports:
        departure_time = timezone.now() + timezone.timedelta(hours=1)
        arrival_time = departure_time + timezone.timedelta(hours=3)

        flight = Flight.objects.create(
            airline='Unknown Airline',
            departure_airport=departure_airport,
            arrival_airport=arrival_airport,
            departure_time=departure_time,
            arrival_time=arrival_time,
        )

        for service_class in Ticket.CLASS_CHOICES:
            FlightClassInfo.objects.create(
                flight=flight,
                service_class=service_class[0],
                seats_number=100,
                luggage_price=100,
                ticket_price=1000,
            )'''

