from django import forms
from django.forms import SelectDateWidget, DateTimeInput

from .models import Flight, FlightClassInfo, Airport, Tickets


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


class FlightUpdateForm(forms.ModelForm):
    departure_time = forms.DateTimeField(label='Время отправления')
    arrival_time = forms.DateTimeField(label='Время прибытия')

    economy_ticket_price = forms.DecimalField(label='Цена билета')
    economy_luggage_price = forms.DecimalField(label='Цена багажа')

    comfort_ticket_price = forms.DecimalField(label='Цена билета')
    comfort_luggage_price = forms.DecimalField(label='Цена багажа')

    business_ticket_price = forms.DecimalField(label='Цена билета')
    business_luggage_price = forms.DecimalField(label='Цена багажа')

    first_class_ticket_price = forms.DecimalField(label='Цена билета')
    first_class_luggage_price = forms.DecimalField(label='Цена багажа')

    class Meta:
        model = Flight
        fields = ['departure_time', 'arrival_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            for service_class, _ in Tickets.CLASS_CHOICES:
                try:
                    flight_class_info = self.instance.flightclassinfo_set.get(service_class=service_class)
                    self.fields[f'{service_class}_ticket_price'].initial = flight_class_info.ticket_price
                    self.fields[f'{service_class}_luggage_price'].initial = flight_class_info.luggage_price
                except FlightClassInfo.DoesNotExist:
                    pass

    def save(self, commit=True):
        flight = super().save(commit=False)
        for service_class, _ in Tickets.CLASS_CHOICES:
            try:
                flight_class_info = flight.flightclassinfo_set.get(service_class=service_class)
                flight_class_info.ticket_price = self.cleaned_data[f'{service_class}_ticket_price']
                flight_class_info.luggage_price = self.cleaned_data[f'{service_class}_luggage_price']
                flight_class_info.save()
            except FlightClassInfo.DoesNotExist:
                FlightClassInfo.objects.create(
                    flight=flight,
                    service_class=service_class,
                    ticket_price=self.cleaned_data[f'{service_class}_ticket_price'],
                    luggage_price=self.cleaned_data[f'{service_class}_luggage_price']
                )
        if commit:
            flight.save()
        return flight
