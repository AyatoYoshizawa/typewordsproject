from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import *
# Create your views here.

class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('index')

class CustomLoginView(LoginView):
    template_name = 'registraion/login.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['username'].widget.attrs['class'] = 'form-control bg-dark text-light'
        form.fields['password'].widget.attrs['class'] = 'form-control bg-dark text-light'