from django.shortcuts import redirect, get_object_or_404
from teacher.models import Class

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def members_only(view_func):
    def wrapper_func(request, id, *args, **kwargs):
        classroom = get_object_or_404(Class, id=id)
        # classroom = Class.objects.get(id=id)
        try:
            if request.user.teacher.is_in_class(key=classroom.access_key):
                return view_func(request, id, *args, **kwargs)
        except:
            pass
        try:
            if request.user.student.is_in_class(key=classroom.access_key):
                return view_func(request, id, *args, **kwargs)
        except:
            pass
        return redirect('home')
    return wrapper_func