from django.urls import path
from .views import *

urlpatterns = [
    path('<int:id>/', test, name='test'),
    path('create/', create_test, name='create_test'),
]

