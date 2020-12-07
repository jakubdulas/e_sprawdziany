from django.urls import path
from .views import *

urlpatterns = [
    path('<int:id>/', test, name='test'),
    path('<int:test_id>/tasks/', task_list, name='task_list'),
    path('<int:id>/task/create/', create_task, name='create_task'),
    path('task/<int:task_id>/add-answer/', add_answer_option, name='add_answer_option'),
    path('create/', create_test, name='create_test'),
    path('<int:test_id>/answers/', show_students_answers, name='show_students_answers'),
    path('list/', test_list, name='test_list'),
    path('<int:id>/students/', test_students, name='test_students'),
]

