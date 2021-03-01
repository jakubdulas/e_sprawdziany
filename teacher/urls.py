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
    path('start-next-lesson/<int:schedule_element_id>/', start_next_lesson, name='start_next_lesson'),
    path('lesson/<slug:lesson_slug>/', lesson_details, name='lesson_details'),
    path('diary/', teachers_diary, name='teachers_diary'),
    path('diary/replacement/', schedule_replacement, name='schedule_replacement'),
    path('diary/cancel-lesson/', cancel_lesson, name='cancel_lesson'),
    path('diary/cancel-lesson/get_groups/<int:schoolclass_id>/', get_groups_ajax),
    path('lessons/', lesson_list, name='lesson_list'),
    path('lesson/<slug:lesson_slug>/take-the-register/', take_the_register, name='take_the_register'),
    path('add-grade/<int:student_id>/<int:subject_id>/<int:school_term_id>/',
         add_grade, name='add_grade'),
    path('add-grade/<int:student_id>/<int:school_term_id>/<int:subject_id>/<int:is_predicted>/<int:is_annual>/',
         add_final_grade, name='add_final_grade'),
    path('edit-grade/<int:grade_id>/', edit_grade, name='edit_grade'),
    path('edit-final-grade/<int:final_grade_id>/', edit_final_grade, name='edit_final_grade'),
    path('delete-grade/<int:grade_id>/', delete_grade, name='delete_grade'),
    path('delete-final-grade/<int:final_grade_id>/', delete_final_grade, name='delete_final_grade'),
    path('add-grades/<int:group_id>/<int:term_id>/<subject_id>/', add_grades_to_all_students, name='add_grades_to_all_students'),
    path('ogloszenia/', announcement_list, name='announcement_list'),
    path('dodaj-ogloszenie/', add_announcement, name='add_announcement'),
    path('edytuj-ogloszenie/<int:announcement_id>/', edit_announcement, name='edit_announcement'),
    path('usun-ogloszenie/<int:announcement_id>/', delete_announcement, name='delete_announcement'),
    path('usprawiedliwienia/', requests_for_excuse, name='requests_for_excuse'),
    path('accept_request_for_excuse/<int:request_for_excuse_id>/', accept_request_for_excuse, name='accept_request_for_excuse'),
    path('reject_request_for_excuse/<int:request_for_excuse_id>/', reject_request_for_excuse, name='reject_request_for_excuse'),
]