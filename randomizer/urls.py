from django.urls import path
from . import views

app_name = 'randomizer'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify, name='verify'),
] 