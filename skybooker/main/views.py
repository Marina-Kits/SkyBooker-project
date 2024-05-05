from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Passenger, Flight, FlightClassInfo, Airport
from django import template
from django.utils.decorators import method_decorator
from .models import Passenger, Airport, Ticket
from .models import Flight
from .forms import FlightForm, FlightUpdateForm
from django.views.generic import ListView, CreateView
from django.shortcuts import render, redirect
from .forms import FlightForm, AirportForm
from .models import FlightClassInfo
from datetime import datetime


def index(request):
    flights_temp = Flight.objects.all()
    cities = Airport.objects.all().values_list('city', flat=True).distinct()

    context = {
        'flights_temp': Flight.objects.all(),
        'cities': cities,
    }

    return render(request, 'main/index.html', context)


@login_required
def profile_view(request):
    user = request.user
    passengers = user.passengers.all()
    passenger_tickets = {}

    for passenger in passengers:
        tickets = Ticket.objects.filter(passenger=passenger)
        passenger_tickets[passenger] = tickets
    return render(request, 'main/profile.html', {'passenger_tickets': passenger_tickets})


def add_passenger_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        passport_number = request.POST.get('passport_number')
        current_user = request.user
        passenger = Passenger.objects.create(
            full_name=full_name,
            gender=gender,
            date_of_birth=date_of_birth,
            passport_number=passport_number
        )
        current_user.passengers.add(passenger)
    return render(request, 'main/profile.html')


def delete_passenger_view(request, passenger_id):
    if request.method == 'POST':
        try:
            passenger = Passenger.objects.get(pk=passenger_id)
            passenger.delete()
            return JsonResponse({'success': True, 'message': 'Passenger deleted successfully'})
        except Passenger.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Passenger does not exist'})
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def update_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')
        request.user.email = new_email
        request.user.save()
        return JsonResponse({'success': True, 'message': 'Email updated successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


def flight_search(request):
    if request.method=='GET':
        departure_city = request.GET.get('departure_city')
        arrival_city = request.GET.get('arrival_city')
        departure_date = request.GET.get('departure_date')
        number_of_passengers = request.GET.get('number_of_passengers', 1)
        service_class = request.GET.get('service_class')
        flights = Flight.objects.filter(
            departure_airport__city=departure_city,
            arrival_airport__city=arrival_city,
            departure_time__date=departure_date
        ).prefetch_related('flightclassinfo_set')
        request.session['service_class'] = service_class

        cities = Airport.objects.all().values_list('city', flat=True).distinct()

        filtered_flights = []
        for flight in flights:
            flight_class_info = flight.flightclassinfo_set.filter(
                service_class=service_class,
                seats_number__gte=number_of_passengers
            ).first()
            if flight_class_info:
                filtered_flights.append((flight))

        context = {
            'flights': filtered_flights,
            'departure_city': departure_city,
            'arrival_city': arrival_city,
            'departure_date': departure_date,
            'number_of_passengers': number_of_passengers,
            'service_class': service_class,
            'cities': cities,
        }

        return render(request, 'main/index.html', context)


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@method_decorator(admin_required, name='dispatch')
class FlightListView(ListView):
    model = Flight
    template_name = 'flight_list.html'


@method_decorator(admin_required, name='dispatch')
class FlightCreateView(CreateView):
    model = Flight
    form_class = FlightForm
    template_name = 'flight_create.html'
    success_url = '/flights/'


@admin_required
def create_flight_view(request):
    return render(request, 'main/flight_create.html')


@admin_required
def create_flight(request):
    if request.method == 'POST':
        flight_form = FlightForm(request.POST)
        if flight_form.is_valid():
            flight = flight_form.save()
            for service_class, _ in Ticket.CLASS_CHOICES:
                FlightClassInfo.objects.create(
                    flight=flight,
                    service_class=service_class,
                    seats_number=request.POST.get(f'{service_class}_seats'),
                    luggage_price=request.POST.get(f'{service_class}_luggage_price'),
                    ticket_price=request.POST.get(f'{service_class}_ticket_price'),
                )
            return redirect('main:flight_list')
    else:
        flight_form = FlightForm()
    return render(request, 'main/flight_create.html', {'flight_form': flight_form})


@admin_required
def create_airport(request):
    if request.method == 'POST':
        airport_form = AirportForm(request.POST)
        if airport_form.is_valid():
            airport_name = request.POST.get('name')
            existing_airport = Airport.objects.filter(name=airport_name).exists()
            if existing_airport:
                return render(request, 'main/airport_create.html', {'airport_form': airport_form, 'error_message': 'Аэропорт с таким названием уже существует'})
            else:
                airport = airport_form.save()
                return redirect('main:create_flight')
    else:
        airport_form = AirportForm()
    return render(request, 'main/airport_create.html', {'airport_form': airport_form})


@admin_required
def flight_info_and_edit(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        form = FlightUpdateForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            return redirect('main:flight_list')
    else:
        form = FlightUpdateForm(instance=flight)
    return render(request, 'main/flight_info_edit.html', {'flight': flight, 'form': form})


def book_ticket(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        passengers_selected = request.POST.getlist('passengers')
        class_choice = request.POST.get('class_choice')
        luggage = request.POST.get('luggage', False) == 'on'

        if not passengers_selected:
            passengers = request.user.passengers.all()
            class_choices = Ticket.CLASS_CHOICES
            error_message = "Выберите хотя бы одного пассажира."
            return render(request, 'main/book_ticket.html',
                          {'flight': flight, 'passengers': passengers, 'class_choices': class_choices,
                           'error_message': error_message})

        flight_class_info = FlightClassInfo.objects.get(flight=flight, service_class=class_choice)
        if flight_class_info.seats_number < len(passengers_selected):
            passengers = request.user.passengers.all()
            class_choices = Ticket.CLASS_CHOICES
            error_message = "Недостаточно мест"
            return render(request, 'main/book_ticket.html',
                          {'flight': flight, 'passengers': passengers, 'class_choices': class_choices,
                           'error_message': error_message})

        created_tickets = []
        for passenger_id in passengers_selected:
            passenger = Passenger.objects.get(id=passenger_id)
            flight_class_info = FlightClassInfo.objects.get(flight=flight, service_class=class_choice)
            ticket_price = flight_class_info.ticket_price
            luggage_price = flight_class_info.luggage_price
            if not luggage:
                luggage_price = 0

            ticket = Ticket.objects.create(
                flight=flight,
                passenger=passenger,
                service_class=class_choice,
                luggage=luggage,
                price=ticket_price,
                luggage_price=luggage_price,
            )

            created_tickets.append(ticket)
            flight_class_info.seats_number -= 1
            flight_class_info.save()

        return redirect('main:confirmation', ticket_ids=','.join([str(ticket.id) for ticket in created_tickets]))

    else:
        passengers = request.user.passengers.all()
        class_choices = Ticket.CLASS_CHOICES
        return render(request, 'main/book_ticket.html',
                      {'flight': flight, 'passengers': passengers, 'class_choices': class_choices})


def confirmation(request, ticket_ids):
    ticket_id_list = [int(id) for id in ticket_ids.split(',')]

    if request.method == 'POST':
        for ticket_id in ticket_id_list:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket.is_confirmed = True
            ticket.save()

        return redirect('main:index')
    else:
        return render(request, 'main/confirmation.html', {'ticket_ids': ticket_ids})