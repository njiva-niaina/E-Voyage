from django import forms
from django.forms import ModelForm
from .models import Reservations
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ReservationForm(ModelForm):
    class Meta:
        model = Reservations
        fields = ['nombre_place']

class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username','email','password1','password2']