from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('login/', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('register/', registerView, name='register'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/change-password/', change_password, name='change_password'),
]