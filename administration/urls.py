from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='administration-home'),
    path('teachers/', teachers, name='administration-teachers'),
    path('schools/', schools, name='administration-schools'),
    path('teacher/<int:id>/', change_teacher_role, name='administration-change_teacher_role'),
]