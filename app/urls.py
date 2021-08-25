from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('<slug:slug>', views.detail, name="detail"),
    path('destination/', views.destination, name="destination"),
    path('recherche/', views.search, name="search"),
    path('reservation/', views.reservation, name="reservation"),
    path('inscription/', views.signup, name="signup"),
    path('connexion/', views.login_view, name="signin"),
    # path('deconnexion/', views.logout_view, name="logout"),
    path('accounts/',include('django.contrib.auth.urls')),
]
