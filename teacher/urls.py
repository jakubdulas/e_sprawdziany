from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('teacher/choose_school/', choose_school, name="choose_school"),
    path('create_class/', create_class, name='create_class'),
    path('join_to_class/', join_to_class, name='join_to_class'),
    path('class/<int:id>/', class_list, name='class_list'),
    path('class/<int:id>/remove/', leave_class, name='leave_class'),
    path('login/', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('register/', registerView, name='register'),
    path('register/teacher', registerTeacherPage, name='register_as_a_teacher'),
    path('register/student', registerStudentPage, name='register_as_a_student'),
]