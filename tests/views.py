from django.shortcuts import render, redirect
from .models import *
from teacher.decorators import teacher_only
from django.contrib import messages
import random

# Create your views here.

def test(request, id):
    context = {

    }

    return render(request, 'test.html', context=context)

@teacher_only
def create_test(request):
    classes = Teacher.objects.get(user=request.user).class_set.all()
    if request.method == "POST":
        try:
            label = request.POST['label']
            if label == '':
                label = '(bez nazwy)'
            class_room = request.POST['class']
            students = Class.objects.get(name=class_room)
            test = Test(label=label, students=students, teacher=request.user.teacher)
            test.save()
            messages.success(request, "test zostal stworzony")
        except:
            messages.error(request, "cos poszlo nie tak")
    context = {
        'classes': classes
    }
    return render(request, 'create_test.html', context=context)

@teacher_only
def add_task(request, id):
    test = Test.objects.get(id=id)

