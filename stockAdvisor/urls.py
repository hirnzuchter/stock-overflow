from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("login", views.signin, name="login"),
    path('create', views.create, name='create'),
    path('signout', views.signout, name='signout'),
    path('profile', views.profile, name='profile'),
    path('rebalancer', views.rebalancer, name='rebalancer'),
]