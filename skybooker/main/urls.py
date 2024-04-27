from . import views
from django.urls import path
from .views import index, profile_view, delete_passenger_view, update_email, FlightListView, FlightCreateView, \
    create_flight, create_airport

app_name = 'main'

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('add_passenger/', views.add_passenger_view, name='add_passenger'),
    path('', index, name='index'),
    path('delete-passenger/<int:passenger_id>/', delete_passenger_view, name='delete_passenger'),
    path('update-email/', update_email, name='update_email'),
    path('create-flight/', create_flight, name='create_flight'),
    path('create-airport/', create_airport, name='create_airport'),
    path('flights/', FlightListView.as_view(), name='flight_list'),
]