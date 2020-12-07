from .views import *
from django.urls import path

urlpatterns = [
    path('register/', registerStudentPage, name='register_as_a_student'),
    path('class/join/', join_to_class, name='join_to_class'),
    path('class/<int:id>/', class_list, name='class_list'),
    path('class/<int:id>/leave/', leave_class, name='leave_class'),
]
