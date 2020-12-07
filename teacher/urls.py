from django.urls import path
from .views import *

urlpatterns = [
    path('choose_school/', choose_school, name="choose_school"),
    path('create_class/', create_class, name='create_class'),
    path('classes/', classes, name='classes'),
    path('register/', registerTeacherPage, name='register_as_a_teacher'),
]