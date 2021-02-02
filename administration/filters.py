import django_filters
from teacher.models import Teacher, School


class TeacherFilter(django_filters.FilterSet):
     class Meta:
        model = Teacher
        fields = ['id', 'user__first_name', 'user__last_name']


class SchoolFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Nazwa:')

    class Meta:
        model = School
        fields = '__all__'