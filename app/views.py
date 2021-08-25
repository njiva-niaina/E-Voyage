from django.shortcuts import render, get_object_or_404, redirect
from .models import Lieux, Reservations, Voyages
from .forms import ReservationForm, CreateUserForm
from django.db.models import F, Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import random
import datetime

def home(request):
    latest_voyages = Voyages.objects.filter(date_voyage__lt=datetime.date.today())
    latest_voyages_sampling = random.sample(list(latest_voyages), k=4)
    voyages = Voyages.objects.filter(date_voyage__gt=datetime.date.today())
    voyages_sampling = random.sample(list(voyages), k=int(voyages.count()/2))
    context = {
        'latest_voyages': latest_voyages_sampling,
        'voyages':voyages_sampling,
    }
    return render(request, 'index.html', context)

def detail(request, slug):
    voyage = get_object_or_404(Voyages, slug=slug)
    other_voyages = Voyages.objects.filter(
        date_voyage__gt=datetime.date.today(), 
        place_voyage__gt=0
    ).exclude(id=voyage.id)
    other_voyages_sampling = random.sample(list(other_voyages), k=int(other_voyages.count()/2))
    form = ReservationForm()
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.client = request.user
            reservation.voyage = voyage
            reservation.save()
            return redirect('reservation')
    context = {
        'voyage':voyage,
        'form':form,
        'other_voyages':other_voyages_sampling
    }
    return render(request, 'detail.html', context)

def destination(request):
    voyages = Voyages.objects.filter(date_voyage__gt=datetime.date.today())
    context = {
        'voyages':voyages,
    }
    return render(request, 'destination.html', context)

def search(request):
    if request.method == "GET":
        search_term = request.GET['search_term']
        if search_term:
            search_result = Lieux.objects.filter(
                Q(nom_lieu__icontains=search_term),
            )
            voyages = Voyages.objects.filter(date_voyage__gt=datetime.date.today())
            context = {
                'search_term':search_term,
                'search_result':search_result,
                'voyages':voyages
            }
            return render(request, 'result.html', context)
        else:
            return redirect('destination')

@login_required
def reservation(request):
    if request.user.is_authenticated:
        reservations = Reservations.objects.filter(client=request.user)
        context = {
            'reservations':reservations
        }
        return render(request, 'reservation.html', context)

def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('signin')
        context = {
            'form':form
        }
    return render(request, 'signup.html', context)

def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, "Nom d\'utilisateur ou mot de passe incorrect")
    else:
        return redirect('home')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('home')