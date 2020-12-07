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
        form = ChooseSchool(instance=teacher)
        if request.POST:
            form = ChooseSchool(request.POST, instance=teacher)
            if form.is_valid():
                form.save()
                return redirect('home')
        context = {'teacher': teacher, 'form': form}
        return render(request, 'teacher/choose_school.html', context=context)
    return redirect('home')


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


def classes(request):
    classes = Class.objects.filter(teacher=request.user.teacher).all()
    context = {
        'classes': classes
    }
    return render(request, 'teacher/classes.html', context=context)