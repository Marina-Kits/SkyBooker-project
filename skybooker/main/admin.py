from django.contrib import admin
from .models import Flight, FlightClassInfo, Airport

admin.site.register(Flight)
admin.site.register(FlightClassInfo)
admin.site.register(Airport)
