from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from teacher.models import Teacher, Student, Parent
from django.contrib.auth import get_user_model
from .models import DirectMessage
from django.contrib import messages
import datetime

User = get_user_model()


def new_message(request):
    teacher_qs = Teacher.objects.filter(school=request.user.teacher.school).exclude(user=request.user).all()
    context = {}
    context['teacher_qs'] = teacher_qs
    if Teacher.objects.filter(user=request.user):
        student_qs = Student.objects.filter(school=request.user.teacher.school, is_graduate=False).exclude(user=request.user).all()
        parent_qs = Parent.objects.filter(student__school=request.user.teacher.school, student__is_graduate=False).exclude(user=request.user).all()
        context['student_qs'] = student_qs
        context['parent_qs'] = parent_qs

    if request.method == 'POST':
        try:
            if not request.POST['title']:
                messages.error(request, 'podaj tytul')
                return redirect('send_message')
            dm = DirectMessage.objects.create(
                sender=request.user,
                title=request.POST['title'],
                body=request.POST["body"],
            )
            for user_id in request.POST.getlist('to'):
                print(user_id)
                dm.to.add(User.objects.filter(id=user_id).first())
                dm.save()
            messages.success(request, 'wiadomosc zostala wyslana')
            return redirect('home')
        except:
            messages.error(request, 'cos poszlo nie tak')
            return redirect('send_message')

    return render(request, 'directmessages/send_message.html', context)


def messages_list(request):
    dms = DirectMessage.objects.filter(to=request.user).order_by('-date').all()
    context = {
        'dms': dms
    }
    return render(request, 'directmessages/messages_list.html', context)


def message_details(request, dm_slug):
    dm = get_object_or_404(DirectMessage, slug=dm_slug)
    dm.is_read = True
    dm.read_date = datetime.datetime.today()
    dm.save()
    context = {
        'dm': dm
    }
    return render(request, 'directmessages/message_details.html', context)


def respond_to_message(request, user_id, dm_slug):
    user = get_object_or_404(User, id=user_id)
    dm = get_object_or_404(DirectMessage, slug=dm_slug)

    context = {
        'user': user,
        'dm': dm
    }

    return render(request, 'directmessages/respond_to_message.html', context)


def sent_messages(request):
    dms = DirectMessage.objects.filter(sender=request.user).all()
    context = {
        'dms': dms
    }
    return render(request, 'directmessages/sent_messages_list.html', context)
