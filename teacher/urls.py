from django.urls import path
from .views import *

urlpatterns = [
    path('choose_school/', choose_school, name="choose_school"),
    path('create_class/', create_class, name='create_class'),
    path('class/list/', teachers_class_list, name='teachers_class_list'),
    path('class/<int:id>/', teachers_class_details, name='teachers_class_details'),
    path('class/<int:id>/delete/', delete_class, name='delete_class'),
    path('register/', registerTeacherPage, name='register_as_a_teacher'),
]