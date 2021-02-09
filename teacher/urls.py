from django.urls import path
from .views import *

urlpatterns = [
    path('add-class-template/', add_class_template, name='add_class_template'),
    path('class/list/', teachers_class_list, name='teachers_class_list'),
    path('class/group/<int:group_id>/', group_detail_view, name='group_detail_view'),
    path('class/<int:id>/', teachers_class_details, name='teachers_class_details'),
    path('class/<int:class_id>/grades/', class_grades_view, name='class_grades_view'),
    path('class/<int:class_id>/groups/', class_groups, name='class_groups'),
    path('class/group/<int:group_id>/edit/', edit_group, name='edit_group'),
    path('class/<int:class_id>/groups/add/', add_group, name='add_group'),
    path('class/<int:class_id>/edit/', edit_class, name='edit_class'),
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
    path('my-schedule/add/<int:day_of_week>/<int:bell>/', add_schedule_element, name='add_schedule_element'),
    path('my-schedule/', teachers_schedule, name='teachers_schedule'),
    path('my-schedule/delete/<int:schedule_element_id>/', delete_schedule_element, name='delete_schedule_element'),
    path('start-lesson/', start_lesson, name='start_lesson'),
    path('lesson/<int:lesson_id>/', lesson_details, name='lesson_details'),
]