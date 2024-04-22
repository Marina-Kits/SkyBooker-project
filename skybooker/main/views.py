from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

@login_required
def profile_view(request):
    return render(request, 'main/profile.html')
