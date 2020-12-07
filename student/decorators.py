from django.shortcuts import redirect
from .models import *


def student_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if Student.objects.filter(user=request.user):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')
    return wrapper_func