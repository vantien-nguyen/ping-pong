from django.urls import path
from .views import pong    

urlpatterns = [
    path('pong/', pong, name='pong'),
]
