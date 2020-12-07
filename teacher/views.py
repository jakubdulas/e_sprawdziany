from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .decorators import *
from .forms import *
import random

def home(request):
    return render(request, 'index.html')

@unauthenticated_user
def loginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Zalogowano pomyślnie.')
            return redirect('home')
        messages.error(request, 'cos poszlo nie tak.')
    return render(request, 'login.html')

@login_required(login_url='login')
def logoutView(request):
    logout(request)
    messages.info(request, 'Zostales wylogowany.')
    return redirect('home')

@unauthenticated_user
def registerView(request):
    return render(request, 'register.html')

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
    return render(request, 'student.html', context)

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
    return render(request, 'teacher.html', context)

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
        return render(request, 'choose_school.html', context=context)
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
            return render(request, 'class_code.html', {'code': key})
    context = {'form': form}
    return render(request, 'create_class.html', context=context)

@login_required(login_url='login')
@student_only
def join_to_class(request):
    if request.POST:
        try:
            key = request.POST.get('access_key')
            if Class.objects.filter(access_key=key).exists() and not request.user.student.is_in_class(key) and (Class.objects.get(access_key=key).members_quantity+1) <= Class.objects.get(access_key=key).max_members:
                class_school = Class.objects.get(access_key=key)
                student = Student.objects.get(user=request.user)
                student.school_class.add(class_school)
                messages.success(request, f'Udalo ci sie dolaczyc do klasy: {Class.objects.get(access_key=key)}')
                return redirect('home')
            elif request.user.student.is_in_class(key):
                messages.info(request, 'Nalezysz juz do tej klasy')
            elif (Class.objects.get(access_key=key).members_quantity+1) > Class.objects.get(access_key=key).max_members:
                messages.info(request, 'klasa przekroczyla mozliwa ilosc uczniow')
            else:
                messages.error(request, 'klasa nie istnieje.')
        except:
            pass
    return render(request, 'join_to_class.html')

@members_only
def class_list(request, id):
    classlist = Class.objects.get(id=id).students
    return render(request, 'classlist.html', {'classlist': classlist})

@members_only
def leave_class(request, id):
    classlist = Class.objects.get(id=id)
    if request.POST:
        request.user.student.school_class.reverse(classlist)
    return render(request, 'classlist.html')

def classes(request):
    classes = Class.objects.filter(teacher=request.user.teacher).all()
    context = {
        'classes': classes
    }
    return render(request, 'classes.html', context=context)