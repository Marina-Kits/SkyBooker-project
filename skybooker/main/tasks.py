from celery import shared_task
from datetime import datetime, timedelta
from .models import Ticket, FlightClassInfo


@shared_task
def delete_expired_tickets():
    print('aaaaaa')
    expiration_time = datetime.now() - timedelta(minutes=1)

    expired_tickets = Ticket.objects.filter(is_confirmed=False, booking_time__lte=expiration_time)

    for ticket in expired_tickets:
        print('i deleted smth')
        flight_class_info = FlightClassInfo.objects.get(flight=ticket.flight, service_class=ticket.service_class)
        flight_class_info.seats_number += 1
        flight_class_info.save()
    expired_tickets.delete()
