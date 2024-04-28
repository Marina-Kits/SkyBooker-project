from django import forms
from django.forms import SelectDateWidget, DateTimeInput

from .models import Flight, FlightClassInfo, Airport


class FlightForm(forms.ModelForm):
    departure_airport = forms.ModelChoiceField(queryset=Airport.objects.all(), label='Аэропорт отправления')
    arrival_airport = forms.ModelChoiceField(queryset=Airport.objects.all(), label='Аэропорт прибытия')
    departure_time = forms.DateTimeField(label='Время отправления', input_formats=['%d-%m-%Y %H:%M'], widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    arrival_time = forms.DateTimeField(label='Время прибытия', input_formats=['%d-%m-%Y %H:%M'], widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    economy_seats = forms.IntegerField(label='Number of Economy Seats')
    economy_ticket_price = forms.DecimalField(label='Economy Ticket Price')
    economy_luggage_price = forms.DecimalField(label='Economy Luggage Price')
    comfort_seats = forms.IntegerField(label='Number of Comfort Seats')
    comfort_ticket_price = forms.DecimalField(label='Comfort Ticket Price')
    comfort_luggage_price = forms.DecimalField(label='Comfort Luggage Price')
    business_seats = forms.IntegerField(label='Number of Business Seats')
    business_ticket_price = forms.DecimalField(label='Business Ticket Price')
    business_luggage_price = forms.DecimalField(label='Business Luggage Price')
    first_class_seats = forms.IntegerField(label='Number of First Class Seats')
    first_class_ticket_price = forms.DecimalField(label='First Class Ticket Price')
    first_class_luggage_price = forms.DecimalField(label='First Class Luggage Price')

    class Meta:
        model = Flight
        fields = ['departure_airport', 'arrival_airport', 'departure_time', 'arrival_time']


class AirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = ['name', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Название'
        self.fields['city'].label = 'Город'