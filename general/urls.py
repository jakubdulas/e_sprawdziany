from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('login/', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('register/', registerView, name='register'),
]