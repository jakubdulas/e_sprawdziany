from django.urls import path
from .views import *

urlpatterns = [
    path('<int:id>/', test, name='test'),
    path('<int:id>/save-answers', save_answers, name="save_answers"),
    path('<int:id>/tasks/', task_list, name='task_list'),
    path('<int:id>/activate/', activate_or_deactivate_test, name='activate_or_deactivate_test'),
    path('<int:id>/edit/', edit_test, name='edit_test'),
    path('<int:id>/delete/', delete_test, name='delete_test'),
    path('<int:id>/task/create/', create_task, name='create_task'),
    path('task/<int:id>/add-answer-option/', add_answer_option, name='add_answer_option'),
    path('task/<int:id>/delete/', delete_task, name='delete_task'),
    path('task/<int:id>/add-correct-answer/', add_correct_answer_for_short_answer, name='add_correct_answer_for_short_answer'),
    path('create/', create_test, name='create_test'),
    path('<int:id>/answers/', show_students_answers, name='show_students_answers'),
    path('list/', test_list, name='test_list'),
    path('<int:id>/students/', test_students, name='test_students'),
]

