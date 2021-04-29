from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from general.decorators import unauthenticated_user, members_only
from general.forms import RegisterForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .decorators import *
from tests.models import Test
from tests.decorators import *
from teacher.models import SchoolClass, Frequency, SchoolYear, RequestForExcuse, Parent
from .utils import SchoolClassCalendar
from django.utils.safestring import mark_safe
import datetime


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


#parents only
def send_excuse(request):
    absences = Frequency.objects.filter(
        student=request.user.parent.student,
        is_absent=True,
        term__school_year=SchoolYear.get_current_school_year(request.user.parent.student.school),
        requestforexcuse=None
    ).all()

    if request.method == 'POST':
        obj = RequestForExcuse.objects.create(
            parent=request.user.parent,
            teacher=request.user.parent.student.get_form_teacher(),
            school_year=SchoolYear.get_current_school_year(request.user.parent.student.school)
        )
        for absence_id in request.POST.getlist('absence'):
            obj.frequency.add(
                Frequency.objects.filter(id=absence_id).first()
            )
            obj.save()
        return redirect('send_excuse')
    context = {
        'absences': absences
    }

    return render(request, 'student/send_excuse.html', context)


def rejected_excuses(request):
    rejected_excuses_qs = RequestForExcuse.objects.filter(
        parent=request.user.parent,
        school_year=SchoolYear.get_current_school_year(request.user.parent.student.school),
        is_rejected=True
    ).all()
    context = {
        'rejected_excuses': rejected_excuses_qs
    }
    return render(request, 'student/rejected_excuses.html', context)


def students_diary(request):
    d = datetime.datetime.today().date()
    school_class = None
    if Parent.objects.filter(user=request.user):
        school_year = SchoolYear.get_current_school_year(request.user.parent.student.school)
        school_class = SchoolClass.objects.filter(students=request.user.parent.student, school_year=school_year).first()
    elif Student.objects.filter(user=request.user):
        school_year = SchoolYear.get_current_school_year(request.user.student.school)
        school_class = SchoolClass.objects.filter(students=request.user.student, school_year=school_year).first()
    cal = SchoolClassCalendar(d.year, d.month, school_class)
    html_cal = cal.formatmonth(withyear=True)
    context = {
        'calendar': mark_safe(html_cal)
    }
    return render(request, 'student/students_diary.html', context)