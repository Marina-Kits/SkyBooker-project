from django.urls import path, include
from users.views import confirm_email
from users.views import Register

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('signup/', Register.as_view(), name='signup'),
    path('confirm_email/<str:token>/', confirm_email, name='confirm_email'),
]
