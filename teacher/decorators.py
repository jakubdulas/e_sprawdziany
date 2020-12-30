from django.shortcuts import redirect, render
from django.contrib import messages
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


def paid_subscription(view_func):
    def wrapper_func(request, *args, **kwargs):
        if Teacher.objects.filter(user=request.user):
            if request.user.teacher.is_paid or request.user.teacher.free_trial:
                return view_func(request, *args, **kwargs)
        messages.info(request, 'nie masz dostępu do tej funkcji')
        return render(request, 'teacher/access_denied.html')
    return wrapper_func





