from django.urls import path
from .views import *


urlpatterns = [
    path('new/', new_message, name='send_message'),
]