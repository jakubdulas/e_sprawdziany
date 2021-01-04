from student.models import Student
from teacher.models import Teacher
from .models import Test, BlankTest, Task
from django.shortcuts import redirect, get_object_or_404


def allowed_student(view_func):
    def wrapper_func(request, test_id, *args, **kwargs):
        if request.user.is_authenticated:
            test = get_object_or_404(Test, id=test_id)
            if Student.objects.filter(user=request.user):
                if request.user.student == test.student and test.is_active:
                    return view_func(request, test_id, *args, **kwargs)
        return redirect('home')
    return wrapper_func


def allowed_teacher(name):
    def inner(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                if Teacher.objects.filter(user=request.user):
                    teacher = Teacher.objects.filter(user=request.user).first()
                    if teacher.is_paid or teacher.free_trial:
                        if name == 'blank_test':
                            if BlankTest.objects.filter(teacher=teacher, id=kwargs['blank_test_id']):
                                return view_func(request, *args, **kwargs)
                        if name == 'task':
                            if Task.objects.filter(id=kwargs['task_id']):
                                if Task.objects.filter(id=kwargs['task_id']).first().test.teacher == teacher:
                                    return view_func(request, *args, **kwargs)
                        if name == 'test':
                            if Test.objects.filter(id=kwargs['test_id']):
                                if Test.objects.filter(id=kwargs['test_id']).first().blank_test.teacher == teacher:
                                    return view_func(request, *args, **kwargs)
            return redirect('home')
        return wrapper_func
    return inner