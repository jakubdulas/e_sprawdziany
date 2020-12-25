from django.shortcuts import redirect
from .models import *


def teacher_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if Teacher.objects.filter(user=request.user):
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper_func


def headmaster_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if Teacher.objects.filter(user=request.user):
            if request.user.teacher.is_headmaster:
                return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper_func