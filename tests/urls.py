from django.urls import path
from .views import *

urlpatterns = [
    path('<int:id>/', test, name='test'),
    path('<int:id>/add_task', add_task, name='add_task'),
    path('create/', create_test, name='create_test'),
    path('<int:test_id>/<int:students_id>/', show_students_answers, name='show_students_answers'),
    path('list/', test_list, name='test_list'),
    path('<int:id>/students/', test_students, name='test_students')
]

