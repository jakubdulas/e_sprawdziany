from django.urls import path
from .views import *

urlpatterns = [
    path('choose-school/', choose_school, name="choose_school"),
    path('create-class/', create_class, name='create_class'),
    path('class/list/', teachers_class_list, name='teachers_class_list'),
    path('class/<int:id>/', teachers_class_details, name='teachers_class_details'),
    path('class/<int:id>/student/<int:student_id>/remove/', remove_student_from_class, name='remove_student_from_class'),
    path('class/<int:id>/delete/', delete_class, name='delete_class'),
    path('register/', registerTeacherPage, name='register_as_a_teacher'),
    path('create-school/', create_school, name='create_school'),
    path('headmaster-panel/', headmaster_panel, name='headmaster_panel'),
    path('headmaster-panel/students/', students_view, name='students_view'),
    path('edit-school-information/', edit_school_information, name='edit_school_information'),
    path('school/accept/<int:id>/', accept_teacher, name='accept_teacher'),
    path('school/reject/<int:id>/', reject_teacher, name='reject_teacher'),
    path('<int:id>/dismiss/', dismiss_teacher, name='dismiss_teacher'),
]