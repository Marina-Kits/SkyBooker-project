from django.contrib.auth import authenticate, login
from django.views import View
from django.shortcuts import render, redirect
import uuid
from users.forms import UserCreationForm
from .models import EmailConfirmationToken
from django.core.mail import send_mail
from django.contrib.auth.models import User


class Register(View):
    template_name = 'registration/signup.html'

    def get(self, request):
        context = {
            'form': UserCreationForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)

        if form.is_valid():
            return self.form_valid(form)
        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        user.save()

        token = uuid.uuid4().hex
        EmailConfirmationToken.objects.create(user=user, token=token)

        subject = 'Подтверждение электронной почты'
        message = f'Для подтверждения электронной почты перейдите по ссылке: http://localhost:8000/confirm_email/{token}/'
        send_mail(
            subject,
            message,
            'from@example.com',
            [user.email],
            fail_silently=False,
        )

        return redirect('main:index')


def confirm_email(request, token):
    try:
        email_confirmation_token = EmailConfirmationToken.objects.get(token=token)
    except EmailConfirmationToken.DoesNotExist:
        return render(request, 'registration/confirm_email_failed.html')

    user = email_confirmation_token.user
    user.is_active = True
    user.save()
    email_confirmation_token.delete()

    user = authenticate(request, username=user.username, password=user.password)
    if user is not None:
        login(request, user)

    return render(request, 'registration/confirm_email_success.html')
