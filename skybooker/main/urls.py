from . import views
from django.urls import path
from .views import index, profile_view

app_name = 'main'

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('add_passenger/', views.add_passenger_view, name='add_passenger'),
    path('', index, name='index'),
]