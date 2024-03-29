from django.shortcuts import render ,get_object_or_404
from django.http import HttpResponse
from .decorators import *
from teacher.models import Teacher, School, Headmaster
from .filters import SchoolFilter, TeacherFilter


@superuser_only
def home(request):
    return render(request, 'administration/home.html')


@superuser_only
def teachers(request):
    teachers_qs = Teacher.objects.all()
    filter = TeacherFilter(request.GET, queryset=teachers_qs)
    teachers_qs = filter.qs

    context = {
        'teacher_qs': teachers_qs,
        'filter': filter,
    }
    return render(request, 'administration/teachers.html', context=context)


@superuser_only
def schools(request):
    schools_qs = School.objects.all()
    filter = SchoolFilter(request.GET, queryset=schools_qs)
    schools_qs = filter.qs

    context = {
        'schools_qs': schools_qs,
        'filter': filter,
    }
    return render(request, 'administration/schools.html', context=context)


@superuser_only
def teacher_details(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    return render(request, 'administration/teacher_detail.html', {'teacher': teacher})


@superuser_only
def change_teacher_role(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if Headmaster.objects.filter(teacher=teacher):
        hm = Headmaster.objects.get(teacher=teacher)
        hm.delete()
    else:
        Headmaster.objects.create(
            teacher=teacher,
        )
    return redirect('administration-teachers')