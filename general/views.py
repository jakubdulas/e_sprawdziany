from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from .decorators import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from teacher.models import *
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse


def home(request):
    context = {}
    if request.user.is_authenticated:
        if Teacher.objects.filter(user=request.user):
            context['teacher'] = request.user.teacher

            present_lesson = ScheduleElement.objects.filter(
                teacher=request.user.teacher,
                bell__end_time__gte=datetime.datetime.today().time(),
                bell__start_time__lte=datetime.datetime.today().time(),
                day_of_week=datetime.datetime.today().weekday()
            ).order_by('bell__number_of_lesson').first()

            context['present_lesson'] = present_lesson

            next_lesson = ScheduleElement.objects.filter(
                teacher=request.user.teacher,
                bell__start_time__gt=datetime.datetime.today().time(),
                day_of_week=datetime.datetime.today().weekday()
            ).order_by('bell__number_of_lesson').first()

            # if not next_lesson:
            #     next_lesson = ScheduleElement.objects.filter(
            #         teacher=request.user.teacher,
            #         bell__start_time__gt=datetime.time(0, 0, 0),
            #         day_of_week=datetime.datetime.today().weekday()+1 if datetime.datetime.today().weekday()+1 != 7 else 0
            #     ).order_by('day_of_week', 'bell__number_of_lesson').first()
            #     i = datetime.datetime.today().weekday()
            #     while not next_lesson:
            #         i += 1
            #         if i == 7:
            #             i = 0
            #         next_lesson = ScheduleElement.objects.filter(
            #             teacher=request.user.teacher,
            #             bell__start_time__gt=datetime.time(0, 0, 0),
            #             day_of_week=i
            #         ).order_by('day_of_week', 'bell__number_of_lesson').first()

            context['next_lesson'] = next_lesson

            return render(request, 'general/index_teacher.html', context=context)
        elif Student.objects.filter(user=request.user):
            context['student'] = request.user.student
            return render(request, 'general/index_student.html', context=context)
    return render(request, 'general/index.html', context=context)


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
    return render(request, 'general/login.html')


@login_required(login_url='login')
def logoutView(request):
    logout(request)
    messages.info(request, 'Zostales wylogowany.')
    return redirect('home')


@unauthenticated_user
def registerView(request):
    return render(request, 'general/register.html')


@login_required(login_url='login')
def profile_view(request):
    user = request.user
    if Teacher.objects.filter(user=user):
        profile = Teacher.objects.get(user=user)
    elif Student.objects.filter(user=user):
        profile = Student.objects.get(user=user)

    return render(request, 'general/profile_view.html', context={'profile': profile})


def edit_profile(request):
    form = UpdateUserForm(instance=request.user)
    context = {
        'form': form
    }

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zaktualizowano profil')
            return redirect('profile')

    return render(request, 'general/edit_profile.html', context=context)


def change_password(request):
    form = PasswordChangeForm(user=request.user)
    context = {
        'form': form
    }

    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('profile')

    return render(request, 'general/change_password.html', context)