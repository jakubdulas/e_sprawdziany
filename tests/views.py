from django.shortcuts import render, redirect
from .models import *
from teacher.decorators import teacher_only
from django.contrib import messages
from .decorators import *
import random

# Create your views here.


@is_student_allowed
def test(request, id):
    test = Test.objects.get(id=id)
    student = Student.objects.get(user=request.user)

    test.is_active = False
    test.save()

    context = {
        'test': test,
        'tasks': test.tasks
    }
    if request.method == "POST":
        for task in test.tasks:
            answer = Answer.objects.create(
                student=student,
                task=task,
            )
            if task.type.label == 'otwarte':
                answer.textarea = request.POST[f"{task.id}"]
            elif task.type.label == 'zamkniete':
                answer.char_field = request.POST[f"{task.id}"]
                if task.answer_options.filter(is_correct=True):
                    if answer.char_field == task.answer_options.filter(is_correct=True).first().label:
                        answer.is_correct = True
            answer.save()

        return redirect('home')

    return render(request, 'tests/test.html', context=context)


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
            test = BlankTest(label=label, students=students, teacher=request.user.teacher)
            test.save()

            for student in students.students:
                Test.objects.create(
                    label=label,
                    student=student,
                    blank_test=test
                )

            messages.success(request, "test zostal stworzony")
            return redirect('create_task', id=test.id)
        except:
            messages.error(request, "cos poszlo nie tak")
    context = {
        'classes': classes
    }
    return render(request, 'tests/create_test.html', context=context)


@teacher_only
def create_task(request, id):
    test = BlankTest.objects.get(id=id)
    types_of_task = TypeOfTask.objects.all()

    if request.method == "POST":
        task = Task.objects.create(
            test=test,
            content=request.POST['content'],
            type=TypeOfTask.objects.get(label=request.POST['type'])
        )

        tests = Test.objects.filter(blank_test=test).all()

        for t in tests:
            task.students_test.add(t)

        task.save()

        return redirect('task_list', test_id=test.id)

    context = {
        'test': test,
        'types_of_task': types_of_task
    }
    return render(request, 'tests/add_task.html', context=context)


@teacher_only
def task_list(request, test_id):
    test = BlankTest.objects.get(id=test_id)
    context = {
        'test': test,
        'tasks': test.tasks
    }
    return render(request, 'tests/task_list.html', context=context)


@teacher_only
def add_answer_option(request, task_id):
    task = Task.objects.get(id=task_id)
    context = {
        'task': task
    }

    if request.method == 'POST':
        print(request.POST)
        if request.POST['is_correct'] == 'tak':
            is_correct = True
        else:
            is_correct = False
        AnswerOption.objects.create(
            task=task,
            label=request.POST['label'],
            is_correct=is_correct
        )


    return render(request, 'tests/add_answer_option.html', context=context)


def show_students_answers(request, test_id):
    test = Test.objects.get(id=test_id)
    tasks_answers = []
    for task in test.tasks:
        tasks_answers.append(tuple((task, task.students_answer(test.student))))
    print(tasks_answers)
    context = {
        'test': test,
        'tasks_answers': tasks_answers,
        'student': test.student
    }
    return render(request, 'tests/show_students_answers.html', context=context)


@teacher_only
def test_list(request):
    tests = BlankTest.objects.filter(teacher=request.user.teacher).all()
    return render(request, 'tests/tests.html', {'tests': tests})


@teacher_only
def test_students(request, id):
    tests = BlankTest.objects.get(id=id).students_tests
    return render(request, 'tests/students.html', {'tests': tests})


