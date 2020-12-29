from django.urls import path
from .views import *

urlpatterns = [
    path('<int:id>/', test, name='test'),
    path('<int:id>/save-answers', save_answers, name="save_answers"),
    path('<int:id>/tasks/', task_list, name='task_list'),
    path('<int:id>/activate/', activate_or_deactivate_test, name='activate_or_deactivate_test'),
    path('<int:id>/edit/', edit_test, name='edit_test'),
    path('<int:id>/threshold/', add_threshold, name='add_threshold'),
    path('<int:id>/threshold/edit/', edit_threshold, name='edit_threshold'),
    path('<int:id>/threshold/delete/', delete_entire_threshold, name='delete_entire_threshold'),
    path('<int:id>/threshold/<int:mark_id>/delete/', delete_threshold, name='delete_threshold'),
    path('<int:id>/delete/', delete_test, name='delete_test'),
    path('<int:id>/task/add/', create_task, name='create_task'),
    path('task/<int:id>/add-answer-option/', add_answer_option, name='add_answer_option'),
    path('task/<int:id>/delete_answer_option/<int:ans_opt_id>/', delete_answer_option, name='delete_answer_option'),
    path('task/<int:id>/delete/', delete_task, name='delete_task'),
    path('task/<int:id>/image/delete/', delete_image, name='delete_image'),
    path('task/<int:id>/add-correct-answer/', add_correct_answer_for_short_answer, name='add_correct_answer_for_short_answer'),
    path('create/', create_test, name='create_test'),
    path('<int:id>/answers/', show_students_answers, name='show_students_answers'),
    path('list/', test_list, name='test_list'),
    path('<int:id>/class/<int:class_id>/', class_tests, name='class_tests'),

    path('<int:id>/task/add/get-types-of-tasks/', get_json_type_of_task_data, name='get_json_type_of_task_data'),
    path('<int:id>/task/add/answer-option/', add_answer_option_ajax, name='add_answer_option_ajax'),
    path('<int:id>/task/add/correct-answer/', add_correct_answer_to_short_answer_ajax, name='add_correct_answer_to_short_answer_ajax'),
]

