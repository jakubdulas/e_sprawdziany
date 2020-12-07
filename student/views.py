from django.shortcuts import render, redirect
from django.contrib import messages
from general.decorators import unauthenticated_user, members_only
from general.forms import RegisterForm
from django.contrib.auth import authenticate, login
from teacher.models import Class
from .models import *
from django.contrib.auth.decorators import login_required
from .decorators import *


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
    return render(request, 'student/join_to_class.html')


@members_only
def class_list(request, id):
    classlist = Class.objects.get(id=id).students
    return render(request, 'student/classlist.html', {'classlist': classlist})


@members_only
def leave_class(request, id):
    classlist = Class.objects.get(id=id)
    if request.POST:
        request.user.student.school_class.reverse(classlist)
    return render(request, 'general/index.html')