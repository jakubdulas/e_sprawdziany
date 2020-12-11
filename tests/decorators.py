from student.models import Student
from teacher.models import Teacher
from .models import Test, BlankTest, Task
from django.shortcuts import redirect, get_object_or_404


def allowed_student(view_func):
    def wrapper_func(request, id, *args, **kwargs):
        test = get_object_or_404(Test, id=id)
        if Student.objects.filter(user=request.user):
            if request.user.student == test.student and test.is_active:
                return view_func(request, id, *args, **kwargs)
            else:
                return redirect('home')
        return redirect('home')
    return wrapper_func


def allowed_teacher_to_test(view_func):
    def wrapper_func(request, id, *args, **kwargs):
        test = get_object_or_404(Test, id=id)
        if Teacher.objects.filter(user=request.user):
            if test.blank_test.teacher == request.user.teacher:
                return view_func(request, id, *args, **kwargs)
        return redirect('home')
    return wrapper_func


def allowed_teacher_to_blanktest(view_func):
    def wrapper_func(request, id, *args, **kwargs):
        test = get_object_or_404(BlankTest, id=id)
        if Teacher.objects.filter(user=request.user):
            if test.teacher == request.user.teacher:
                return view_func(request, id, *args, **kwargs)
        return redirect('home')
    return wrapper_func


def allowed_teacher_to_tests_task(view_func):
    def wrapper_func(request, id, *args, **kwargs):
        try:
            task = Task.objects.get(id=id)
            if Teacher.objects.filter(user=request.user):
                if task.test.teacher == request.user.teacher:
                    return view_func(request, id, *args, **kwargs)
            return redirect('home')
        except:
            return redirect('home')
    return wrapper_func

