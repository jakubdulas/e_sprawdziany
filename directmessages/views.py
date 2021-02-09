from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from teacher.models import Teacher, Student
# Create your views here.


@login_required(login_url='login')
def new_message(request):
    user = request.user

    return render(request, 'directmessages/send_message.html')


def get_teachers(request):
    if Teacher.objects.filter(school=request.user):
        pass