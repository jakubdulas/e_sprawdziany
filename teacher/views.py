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


@unauthenticated_user
def registerTeacherPage(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],)
            login(request, new_user)
            Teacher.objects.create(user=new_user)
            messages.success(request, 'Zalogowano pomyślnie.')
            return redirect('choose_school')
        messages.error(request, 'cos poszlo nie tak.')
    context = {'form': form}
    return render(request, 'teacher/teacher.html', context)


@teacher_only
def choose_school(request):
    teacher = Teacher.objects.get(user=request.user)
    if not teacher.school:
        form = SendRequestForJoiningToSchool
        if request.POST:
            form = SendRequestForJoiningToSchool(request.POST)
            form.instance.teacher = teacher
            if form.is_valid():
                form.save()
                return redirect('home')
        context = {'teacher': teacher, 'form': form}
        return render(request, 'teacher/choose_school.html', context=context)
    return redirect('home')


@paid_subscription
@teacher_only
def create_class(request):
    teacher = Teacher.objects.get(user=request.user)
    form = CreateClass()
    if request.POST:
        form = CreateClass(request.POST)
        key = ''
        for i in range(6):
            key += str(random.randint(0, 9))
        while Class.objects.filter(access_key=key):
            key = ''
            for i in range(6):
                key += str(random.randint(0, 9))
        form.instance.access_key = key
        form.instance.teacher = teacher
        if form.is_valid():
            form.save()
            return render(request, 'teacher/class_code.html', {'code': key})
    context = {'form': form}
    return render(request, 'teacher/create_class.html', context=context)


@paid_subscription
@teacher_only
def teachers_class_list(request):
    classes = Class.objects.filter(teacher=request.user.teacher).all()
    context = {
        'classes': classes
    }
    return render(request, 'teacher/classes.html', context=context)


@paid_subscription
@teacher_only
@members_only
def teachers_class_details(request, id):
    class_room = Class.objects.get(id=id)
    return render(request, "teacher/class_details.html", {"class": class_room})


@paid_subscription
@teacher_only
@members_only
def delete_class(request, id):
    class_room = Class.objects.get(id=id)
    if request.method == "POST":
        class_room.delete()
        return redirect('home')
    return render(request, 'teacher/delete_class.html', {"class": class_room})


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
def create_school(request):
    if not request.user.teacher.school:
        form = CreateSchool
        context = {
            'form': form
        }
        if request.method == 'POST':
            form = CreateSchool(request.POST)
            if form.is_valid():
                form.save()
                request.user.teacher.school = form.instance
                request.user.teacher.save()
                messages.success(request, 'Udało ci się dodać szkołe')
                return redirect('home')
            else:
                messages.error(request, 'Nie udało ci się dodać szkoły')
            return redirect('create_school')
        return render(request, 'teacher/create_school.html', context=context)
    return render('home')


@headmaster_only
def edit_school_information(request):
    if request.user.teacher.school:
        school = request.user.teacher.school
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
def accept_teacher(request, id):
    request_for_joining = get_object_or_404(RequestForJoiningToSchool, id=id)
    request_for_joining.teacher.school = request.user.teacher.school
    request_for_joining.teacher.save()
    request_for_joining.delete()
    return redirect('headmaster_panel')


@headmaster_only
def reject_teacher(request, id):
    request_for_joining = get_object_or_404(RequestForJoiningToSchool, id=id)
    request_for_joining.delete()
    return redirect('headmaster_panel')


@headmaster_only
def headmaster_panel(request):
    requests_qs = RequestForJoiningToSchool.objects.filter(school=request.user.teacher.school).all()
    teachers_qs = Teacher.objects.filter(school=request.user.teacher.school, is_headmaster=False).all()
    context = {
        'requests_qs': requests_qs,
        'teachers_qs': teachers_qs,
    }
    return render(request, 'teacher/headmaster_panel.html', context=context)


@headmaster_only
def dismiss_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    if request.user.teacher.school == teacher.school:
        teacher.school = None
        teacher.save()
        return redirect('headmaster_panel')
    return redirect('home')

