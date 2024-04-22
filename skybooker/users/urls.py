from django.urls import path, include

from users.views import Register

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('signup/', Register.as_view(), name='signup'),
]
