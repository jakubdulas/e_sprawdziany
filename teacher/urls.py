from django.urls import path
from .views import *

urlpatterns = [
    path('create-class/', create_class, name='create_class'),
    path('class/list/', teachers_class_list, name='teachers_class_list'),
    path('class/<int:id>/', teachers_class_details, name='teachers_class_details'),
    path('class/<int:id>/grades/', class_grades_view, name='class_grades_view'),
    path('class/<int:id>/student/<int:student_id>/remove/', remove_student_from_class, name='remove_student_from_class'),
    path('class/<int:id>/edit/', edit_class, name='edit_class'),
    path('administraion/', headmaster_panel, name='headmaster_panel'),
    path('students/', students_view, name='students_view'),
    path('teachers/', teachers_view, name='teachers_view'),
    path('edit-school-information/', edit_school_information, name='edit_school_information'),
    path('<int:id>/dismiss/', dismiss_teacher, name='dismiss_teacher'),
    path('bells/', bells_view, name='bells'),
    path('bells/edit/', add_edit_bells, name='edit_bells'),
    path('teacher/<teacher_id>/', teacher_details, name='teacher_details'),
    path('term/<int:number>/', edit_term, name='add_term'),
    path('year/<int:school_year_id>/', school_year_details, name='school_year_details'),
]