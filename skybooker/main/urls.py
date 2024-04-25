from . import views
from django.urls import path
from .views import index, profile_view, delete_passenger_view, update_email

app_name = 'main'

urlpatterns = [
    path('profile/', profile_view, name='profile'),
    path('add_passenger/', views.add_passenger_view, name='add_passenger'),
    path('', index, name='index'),
    path('delete-passenger/<int:passenger_id>/', delete_passenger_view, name='delete_passenger'),
    path('update-email/', update_email, name='update_email'),
]