from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from general.decorators import unauthenticated_user, members_only
from general.forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .decorators import *
from tests.models import Test
from tests.decorators import *
from teacher.models import SchoolClass


@unauthenticated_user
def registerStudentPage(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'], )
            login(request, new_user)
            Student.objects.create(user=new_user)
            messages.success(request, 'Zalogowano pomyślnie.')
            return redirect('home')
        messages.error(request, 'cos poszlo nie tak.')
    context = {'form': form}
    return render(request, 'student/student.html', context)


@student_only
def class_list(request):
    student = Student.objects.get(user=request.user)
    classlist = student.school_class.all()
    return render(request, 'student/classlist.html', {'classlist': classlist})


@members_only
@student_only
def class_details(request, id):
    class_room = SchoolClass.objects.get(id=id)
    return render(request, "student/class_details.html", {"class": class_room})


@student_only
def active_tests(request):
    tests = Test.objects.filter(student=request.user.student, is_active=True, is_done=False).all()
    return render(request, 'student/active_tests.html', {'tests': tests})


@student_only
def my_tests(request):
    tests = Test.objects.filter(student=request.user.student, is_done=True).all()
    return render(request, 'student/my_tests.html', {'tests': tests})


#rozwiązany sprawdzian ucznia
@student_only
def my_test(request, id):
    test = get_object_or_404(Test, id=id, student=request.user.student, is_done=True)
    # test = Test.objects.get(id=test_id)
    tasks_answers = []
    for task in test.tasks:
        tasks_answers.append(tuple((task, task.students_answer(test.student))))
    context = {
        'test': test,
        'tasks_answers': tasks_answers,
        'student': test.student
    }
    return render(request, 'student/my_test.html', context=context)