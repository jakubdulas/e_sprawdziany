from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .decorators import *
from .forms import *
from general.decorators import *
from general.forms import *
import random
from student.models import Student
from django.forms import inlineformset_factory
import datetime


@paid_subscription
@headmaster_only
def create_class(request):
    teacher = Teacher.objects.get(user=request.user)
    form = CreateClass()
    if request.POST:
        form = CreateClass(request.POST)
        form.instance.teacher = teacher
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'teacher/create_class.html', context=context)


@paid_subscription
@teacher_only
def teachers_class_list(request):
    school_year = SchoolYear.objects.filter(
        school=request.user.teacher.school,
        start__lte=datetime.datetime.today().date(),
        end__gte=datetime.datetime.today().date(),
    ).first()
    class_qs = Class.objects.filter(school_year=school_year, school=request.user.teacher.school)
    context = {
        'class_qs': class_qs
    }
    return render(request, 'teacher/classes.html', context=context)


@paid_subscription
@teacher_only
def teachers_class_details(request, id):
    class_room = get_object_or_404(Class, id=id)
    return render(request, "teacher/class_details.html", {"class": class_room})


@paid_subscription
@members_only
@teacher_only
def remove_student_from_class(request, id, student_id):
    class_room = get_object_or_404(Class, id=id)
    student = get_object_or_404(Student, id=student_id)
    student.school_class.remove(class_room)
    student.save()
    return redirect('teachers_class_details', id=id)


@headmaster_only
def edit_school_information(request):
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    if headmaster.school:
        school = headmaster.school
        form = CreateSchool(instance=school)
        if request.method == 'POST':
            form = CreateSchool(request.POST, instance=school)
            if form.is_valid():
                form.save()
                messages.success(request, 'Zapisano zmiany')
                return redirect('home')
            messages.error(request, 'cos poszlo nie tak')
            return render('edit_school_information')
        context = {
            'form': form
        }
        return render(request, 'teacher/edit_school_information.html', context=context)
    return redirect('home')


@headmaster_only
def headmaster_panel(request):
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    teachers_qs = Teacher.objects.filter(school=headmaster.school).all()
    school_year = SchoolYear.objects.filter(
        school=request.user.teacher.school,
        start__lte=datetime.datetime.today().date(),
        end__gte=datetime.datetime.today().date(),
    ).first()

    term1 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=1, school_year=school_year).first()
    term2 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=2, school_year=school_year).first()

    context = {
        'teachers_qs': teachers_qs,
        'school': headmaster.school,
        'term1': term1,
        'term2': term2,
        'school_year': school_year
    }
    return render(request, 'teacher/headmaster_panel.html', context=context)


@headmaster_only
def dismiss_teacher(request, id):
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    teacher = get_object_or_404(Teacher, id=id)
    if headmaster.school in teacher.school.all():
        teacher.school = ''
        teacher.is_paid = False
        teacher.save()
        return redirect('headmaster_panel')
    return redirect('home')


@headmaster_only
def students_view(request):
    students_qs = Student.objects.filter(school=request.user.teacher.headmaster.school).all()
    return render(request, 'teacher/headmaster_panel-students.html', {'students': students_qs})


@headmaster_only
def teachers_view(request):
    teachers_qs = Teacher.objects.filter(school=request.user.teacher.headmaster.school).all()
    return render(request, 'teacher/headmaster_panel-teachers.html', {'teachers': teachers_qs})


@teacher_only
@members_only
def class_grades_view(request, class_id):
    class_room = get_object_or_404(Class, id=class_id)
    qs = Student.objects.filter(school_class=class_room).all()

    context = {
        'qs': qs,
        'class': class_room
    }

    return render(request, 'teacher/class_grades.html', context=context)


@teacher_only
@members_only
def edit_class(request, class_id):
    class_room = get_object_or_404(Class, id=class_id)
    form = CreateClass(instance=class_room)
    if request.method == 'POST':
        form = CreateClass(request.POST, instance=class_room)
        if form.is_valid():
            form.save()
            messages.success(request, 'zapisano zmiany')
            return redirect('teachers_class_details', class_id)
    context = {
        'form': form,
        'class': class_room
    }
    return render(request, 'teacher/edit_class.html', context=context)


@headmaster_only
def bells_view(request):
    qs = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()
    context = {
        'qs': qs
    }
    return render(request, 'teacher/bells.html', context)


@headmaster_only
def add_edit_bells(request):
    BellFormSet = inlineformset_factory(School, Bell, fields='__all__')
    formset = BellFormSet(instance=request.user.teacher.school)
    if request.method == 'POST':
        formset = BellFormSet(request.POST, instance=request.user.teacher.school)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Zaktualizowano rozkład dzwonków')
        else:
            messages.success(request, 'Wystąpił błąd. Spróbuj ponowanie.')
        return redirect('edit_bells')
    context = {
        'formset': formset
    }
    return render(request, 'teacher/edit_bell_schedule.html', context)


@teacher_only
def teacher_details(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    context = {
        'teacher': teacher
    }
    return render(request, 'teacher/teacher_details.html', context)


@headmaster_only
def edit_term(request, number):
    number = int(number)
    form = SchoolTermForm(instance=SchoolTerm.objects.filter(school=request.user.teacher.school, number=number).first())
    if request.method == 'POST':
        form = SchoolTermForm(request.POST, instance=SchoolTerm.objects.filter(school=request.user.teacher.school, number=number).first())
        form.instance.number = number
        form.instance.school = request.user.teacher.school
        if form.is_valid():
            form.save()
            messages.success(request, f'Zaktualizowano semestr {number}.')
            return redirect('headmaster_panel')
        else:
            messages.success(request, f'Wystąpił błąd')
            return redirect('add_term', number)
    context = {
        'form': form
    }
    return render(request, 'teacher/add_term.html', context)


@headmaster_only
def school_year_details(request, school_year_id):
    school_year = get_object_or_404(SchoolYear, id=school_year_id)
    term1 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=1, school_year=school_year).first()
    term2 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=2, school_year=school_year).first()

    context = {
        'school_year': school_year,
        'term1': term1,
        'term2': term2
    }

    return render(request, 'teacher/school_year_details.html', context)