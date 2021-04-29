from .views import *
from django.urls import path

urlpatterns = [
    path('register/', registerStudentPage, name='register_as_a_student'),
    path('class/<int:id>/', class_details, name='class_details'),
    path('class/all/', class_list, name='class_list'),
    path('active-tests/', active_tests, name='active_tests'),
    path('my-tests/', my_tests, name='my_tests'),
    path('my_test/<int:id>', my_test, name='my_test'),
    path('napisz-usprawiedliwienie/', send_excuse, name='send_excuse'),
    path('odrzucone-usprawiedliwienia/', rejected_excuses, name='rejected_excuses'),
    path('terminarz/', students_diary, name='students_diary'),
]
