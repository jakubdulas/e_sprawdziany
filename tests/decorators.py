from student.models import Student
from .models import Test
from django.shortcuts import redirect


def is_student_allowed(view_func):
    def wrapper_func(request, id, *args, **kwargs):
        try:
            test = Test.objects.get(id=id)
            if request.user.student in test.students.students:
                return view_func(request, id, *args, **kwargs)
            else:
                return redirect('home')
        except:
            pass
        return redirect('home')
    return wrapper_func
