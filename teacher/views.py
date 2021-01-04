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
    form = SendRequestForJoiningToSchool
    if request.POST:
        form = SendRequestForJoiningToSchool(request.POST)
        if School.objects.filter(id=form.data.get('school')).first() not in request.user.teacher.school.all():
            form.instance.teacher = teacher
            if form.is_valid():
                form.save()
        return redirect('home')
    context = {'teacher': teacher, 'form': form}
    return render(request, 'teacher/choose_school.html', context=context)


@paid_subscription
@teacher_only
def create_class(request):
    teacher = Teacher.objects.get(user=request.user)
    form = CreateClass()
    if request.POST:
        form = CreateClass(request.POST)
        keys = 'abcdefghijklmnoprstuwyzABCDEFGHIJKLMNOPRSTUWYZ123456789'
        key = ''
        for i in range(6):
            key += str(keys[random.randint(0, len(keys))])
        while Class.objects.filter(access_key=key):
            key = ''
            for i in range(6):
                key += str(keys[random.randint(0, len(keys))])
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
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    if not headmaster.school:
        form = CreateSchool
        context = {
            'form': form
        }
        if request.method == 'POST':
            form = CreateSchool(request.POST)
            if form.is_valid():
                keys = 'abcdefghijklmnoprstuwyzABCDEFGHIJKLMNOPRSTUWYZ123456789'
                key = ''
                for i in range(8):
                    key += str(keys[random.randint(0, len(keys)-1)])
                    if i == 7:
                        key += 'szk'
                while Class.objects.filter(access_key=key):
                    key = ''
                    for i in range(8):
                        key += str(keys[random.randint(0, len(keys)-1)])
                        if i == 7:
                            key += 'szk'
                form.instance.key = key
                form.save()
                headmaster.school = form.instance
                headmaster.save()
                request.user.teacher.school.add(form.instance)
                request.user.teacher.save()
                messages.success(request, 'Udało ci się dodać szkołe')
                return render(request, 'teacher/school_code.html', {'code': key})
            else:
                messages.error(request, 'Nie udało ci się dodać szkoły')
            return redirect('create_school')
        return render(request, 'teacher/create_school.html', context=context)
    return render('home')


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
def accept_teacher(request, id):
    headmaster = Headmaster.objects.get(teacher=request.user.teacher)
    request_for_joining = get_object_or_404(RequestForJoiningToSchool, id=id)
    request_for_joining.teacher.school.add(headmaster.school)
    request_for_joining.teacher.is_paid = headmaster.school.is_paid
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
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    requests_qs = RequestForJoiningToSchool.objects.filter(school=headmaster.school).all()
    teachers_qs = Teacher.objects.filter(school=headmaster.school).all()
    context = {
        'requests_qs': requests_qs,
        'teachers_qs': teachers_qs,
        'school': headmaster.school
    }
    return render(request, 'teacher/headmaster_panel.html', context=context)


@headmaster_only
def dismiss_teacher(request, id):
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    teacher = get_object_or_404(Teacher, id=id)
    if headmaster.school in teacher.school.all():
        teacher.school.remove(headmaster.school)
        teacher.is_paid = False
        teacher.save()
        return redirect('headmaster_panel')
    return redirect('home')


@headmaster_only
def students_view(request):
    students_qs = Student.objects.filter(school=request.user.teacher.headmaster.school).all()
    return render(request, 'teacher/headmaster_panel-students.html', {'students': students_qs})


def view_profile(request, username):
    user = get_object_or_404(User, username=username)

