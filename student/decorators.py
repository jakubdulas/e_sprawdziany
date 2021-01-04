from django.shortcuts import redirect
from .models import *


def student_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if Student.objects.filter(user=request.user):
                return view_func(request, *args, **kwargs)
        return redirect('home')
    return wrapper_func
