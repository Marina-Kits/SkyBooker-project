from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import Ticket


class Command(BaseCommand):
    help = 'Check bookings and revert if not confirmed within 15 minutes'

    def handle(self, *args, **options):
        fifteen_minutes_ago = timezone.now() - timezone.timedelta(minutes=1)
        unconfirmed_tickets = Ticket.objects.filter(is_confirmed=False, booking_time__lte=fifteen_minutes_ago)

        for ticket in unconfirmed_tickets:
            flight_class_info = ticket.flight.flightclassinfo_set.get(service_class=ticket.class_choice)
            flight_class_info.seats_number += 1
            flight_class_info.save()
            ticket.delete()

        self.stdout.write(self.style.SUCCESS('Bookings checked successfully.'))
