from django.shortcuts import render, redirect
from .models import *
from teacher.decorators import teacher_only
from django.contrib import messages
import random

# Create your views here.


def test(request, id):
    test = Test.objects.get(id=id)

    context = {
        'test': test,
        'tasks': test.tasks
    }
    if request.method == "POST":
        for task in test.tasks:
            answer = Answer.objects.create(
                student=request.user.student,
                task=task,
            )
            if task.type.label == 'otwarte':
                answer.textarea = request.POST[f"{task.id}"]
            elif task.type.label == 'zamkniete':
                answer.char_field = request.POST[f"{task.id}"]
                if task.answer_options.filter(is_correct=True):
                    if answer.char_field == task.answer_options.filter(is_correct=True).first():
                        answer.is_correct = True
            answer.save()

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


def show_students_answers(request, id):
    student = request.user.student
    test = Test.objects.get(id=id)
    tasks_answers = []
    for task in test.tasks:
        tasks_answers.append(tuple((task, task.students_answer(student))))

    context = {
        'test': test,
        'tasks_answers': tasks_answers,
    }
    return render(request, 'show_students_answers.html', context=context)

