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

# Create your views here.
def index(request):
    flights_temp = Flight.objects.all()
    return render(request, 'main/index.html', {'flights_temp': flights_temp})

@login_required
def profile_view(request):
    return render(request, 'main/profile.html')


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
        number_of_passengers = request.GET.get('number_of_passengers')
        service_class = request.GET.get('service_class')
        flights = Flight.objects.filter(
            departure_airport__city=departure_city,
            arrival_airport__city=arrival_city,
            departure_time__date=departure_date
        ).prefetch_related('flightclassinfo_set')
        request.session['service_class'] = service_class

        filtered_flights = []
        for flight in flights:
            flight_class_info = flight.flightclassinfo_set.filter(
                service_class=service_class,
                seats_number__gte=number_of_passengers
            ).first()
            if flight_class_info:
                filtered_flights.append((flight, flight_class_info))

        context = {
            'flights': filtered_flights,
            'departure_city': departure_city,
            'arrival_city': arrival_city,
            'departure_date': departure_date,
            'number_of_passengers': number_of_passengers,
            'service_class': service_class,
        }

        return render(request, 'main/index.html', context)


def flight_view(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    service_class = request.session.get('service_class', 'economy')
    flight_class_info = get_object_or_404(FlightClassInfo, flight=flight, service_class=service_class)

    context = {
        'flight': flight,
        'flight_class_info': flight_class_info,
    }

    return render(request, 'main/ticket.html', context)

register = template.Library()

@register.filter
def service_class(queryset, service_class):
    return queryset.filter(service_class=service_class)

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
