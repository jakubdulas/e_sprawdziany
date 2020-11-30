from django.urls import path
from .views import *

urlpatterns = [
    path('<int:id>/', test, name='test'),
    path('<int:id>/add_task', add_task, name='add_task'),
    path('create/', create_test, name='create_test'),
]

