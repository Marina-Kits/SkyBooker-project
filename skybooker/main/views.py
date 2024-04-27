from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Passenger, Airport, Tickets
from .models import Flight
from .forms import FlightForm
from django.views.generic import ListView, CreateView
from django.shortcuts import render, redirect
from .forms import FlightForm, AirportForm
from .models import FlightClassInfo
from datetime import datetime

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

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


class FlightListView(ListView):
    model = Flight
    template_name = 'flight_list.html'


class FlightCreateView(CreateView):
    model = Flight
    form_class = FlightForm
    template_name = 'flight_create.html'
    success_url = '/flights/'


def create_flight_view(request):
    # Your view logic to render the flight creation form
    return render(request, 'main/flight_create.html')


def create_flight(request):
    if request.method == 'POST':
        flight_form = FlightForm(request.POST)
        if flight_form.is_valid():
            flight = flight_form.save()
            # Create FlightClassInfo instances for each service class
            for service_class, _ in Tickets.CLASS_CHOICES:
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


def create_airport(request):
    if request.method == 'POST':
        airport_form = AirportForm(request.POST)
        if airport_form.is_valid():
            airport_name = request.POST.get('name')
            existing_airport = Airport.objects.filter(name=airport_name).exists()
            if existing_airport:
                return render(request, 'main/airport_create.html', {'airport_form': airport_form, 'error_message': 'Airport with the same name already exists'})
            else:
                airport = airport_form.save()
                return redirect('main:create_flight')
    else:
        airport_form = AirportForm()
    return render(request, 'main/airport_create.html', {'airport_form': airport_form})
