from django.shortcuts import render, redirect, get_object_or_404
from general.decorators import members_only
from .models import *
from teacher.decorators import teacher_only, paid_subscription
from django.contrib import messages
from .decorators import *
from .forms import *
from django.utils.dateparse import parse_duration
import random
import datetime

# Create your views here.


#rozwiązywanie testu
@allowed_student
def test(request, id):
    # test = Test.objects.get(id=id)
    test = get_object_or_404(Test, id=id)
    #!!!!!!!!!! odkomentować gry doda sie frontend !!!!!!!!!!!
    end = datetime.datetime.now() + test.blank_test.countdown
    # test.is_active = False
    test.save()
    context = {
        'test': test,
        'tasks': test.tasks,
        'end_test': end.strftime("%m %d, %Y %H:%M:%S")
    }

    return render(request, 'tests/test.html', context=context)


def save_answers(request, id):
    if request.method == "POST":
        test = get_object_or_404(Test, id=id)
        student = request.user.student
        test.is_active = False
        test.is_done = True
        test.save()
        for task in test.tasks:
            answer = Answer.objects.create(
                student=student,
                task=task,
            )
            if f"{task.id}" in request.POST.keys():
                if task.type.label == 'otwarte':
                    answer.textarea = request.POST[f"{task.id}"]
                elif task.type.label == 'zamkniete':
                    answer.char_field = request.POST[f"{task.id}"]
                    if task.answer_options.filter(is_correct=True):
                        if answer.char_field == task.answer_options.filter(is_correct=True).first().label:
                            answer.is_correct = True
                elif task.type.label == 'krotka_odpowiedz':
                    answer.char_field = request.POST[f'{task.id}']
                    if task.correct_answer != '':
                        if answer.char_field == task.correct_answer:
                            answer.is_correct = True
            answer.save()

        # sprawdzanie testu
        earned_total = 0
        total = 0
        for task in test.tasks:
            answer = Answer.objects.get(task=task)
            total += task.points
            if answer.is_correct:
                answer.earned_points = task.points
                earned_total += answer.earned_points
            answer.save()

        if total != 0:
            percent = earned_total * 100 / total
            if test.blank_test.autocheck:
                for mark in test.blank_test.threshold:
                    if mark.to_percent >= percent >= mark.from_percent:
                        test.mark = mark.mark
                        test.save()

        if test.blank_test.autocheck:
            return render(request, 'tests/show_mark.html', {'mark': test.mark})
        return redirect('home')
    return redirect('home')


#tworzenie testu przez nauczyciela
@paid_subscription
@teacher_only
def create_test(request):
    classes = get_object_or_404(Teacher, user=request.user).class_set.all()
    # classes = Teacher.objects.get(user=request.user).class_set.all()
    if request.method == "POST":
        try:
            label = request.POST['label']
            if label == '':
                label = '(bez nazwy)'
            class_room = request.POST['class']
            students = Class.objects.get(name=class_room)
            countdown = parse_duration(request.POST['countdown'])
            test = BlankTest(label=label, students=students, teacher=request.user.teacher, countdown=countdown)
            test.save()

            for student in students.students:
                Test.objects.create(
                    label=label,
                    student=student,
                    blank_test=test
                )

            messages.success(request, "test zostal stworzony")
            return redirect('add_threshold', id=test.id)
            # return redirect('create_task', id=test.id)
        except:
            messages.error(request, "cos poszlo nie tak")
    context = {
        'classes': classes
    }
    return render(request, 'tests/create_test.html', context=context)


#stworzenie zadania do testu i dodanie go
@paid_subscription
@allowed_teacher_to_blanktest
def create_task(request, id):
    test = get_object_or_404(BlankTest, id=id)
    types_of_task = TypeOfTask.objects.all()
    if request.method == "POST":

        try:
            task = Task.objects.create(
                test=test,
                content=request.POST['content'],
                type=TypeOfTask.objects.get(label=request.POST['type']),
                points=request.POST['points']
            )

            tests = Test.objects.filter(blank_test=test).all()

            if request.FILES:
                task.image = request.FILES['image']

            for t in tests:
                task.students_test.add(t)

            task.save()

            if task.type.label == 'krotka_odpowiedz':
                return redirect('add_correct_answer_for_short_answer', id=task.id)
            elif task.type.label == 'zamkniete':
                return redirect('add_answer_option', id=task.id)
            return redirect('task_list', id=id)
        except:
            messages.error(request, 'wystąpił błąd podczas tworzenia zadania')

    context = {
        'test': test,
        'types_of_task': types_of_task,
    }
    return render(request, 'tests/add_task.html', context=context)


#lista zadan do testu, widok nauczyciela
@paid_subscription
@allowed_teacher_to_blanktest
def task_list(request, id):
    test = get_object_or_404(BlankTest, id=id)
    # test = BlankTest.objects.get(id=test_id)
    context = {
        'test': test,
        'tasks': test.tasks
    }
    return render(request, 'tests/task_list.html', context=context)


# dodawanie poprwanej odpowiedzi do krótkiej odpwowiedzi
@paid_subscription
@allowed_teacher_to_tests_task
def add_correct_answer_for_short_answer(request, id):
    task = get_object_or_404(Task, id=id)
    context = {
        'task': task
    }

    if request.method == 'POST':
        if f"{task.id}" in request.POST.keys():
            task.correct_answer = request.POST[f"{task.id}"]
            task.save()
            return redirect('task_list', id=task.test.id)

    return render(request, 'tests/answer_for_short_answer.html', context=context)


#dodanie do zadania opcji odpowiedzi, widok nauczyciela
@paid_subscription
@allowed_teacher_to_tests_task
def add_answer_option(request, id):
    task = get_object_or_404(Task, id=id)
    # task = Task.objects.get(id=task_id)
    context = {
        'task': task
    }
    if request.method == 'POST':
        try:
            if request.POST['is_correct'] == 'tak':
                is_correct = True
            else:
                is_correct = False
            AnswerOption.objects.create(
                task=task,
                label=request.POST['label'],
                is_correct=is_correct
            )
        except:
            messages.error(request, 'nie udalo sie dodac odpowiedzi')

    return render(request, 'tests/add_answer_option.html', context=context)


#rozwiązany sprawdzian ucznia
@paid_subscription
@allowed_teacher_to_test
def show_students_answers(request, id):
    test = get_object_or_404(Test, id=id)
    # test = Test.objects.get(id=test_id)
    tasks_answers = []
    for task in test.tasks:
        tasks_answers.append(tuple((task, task.students_answer(test.student))))

    if request.method == 'POST':
        total = test.blank_test.total_points
        earned_total = 0

        for task in test.tasks:
            answer = task.students_answer(test.student)
            if task.points >= int(request.POST[f'{task.id}']):
                answer.earned_points = int(request.POST[f'{task.id}'])
            answer.save()
            earned_total += answer.earned_points

        percent = earned_total * 100 / total

        for mark in test.blank_test.threshold:
            if mark.to_percent >= percent >= mark.from_percent:
                test.mark = mark.mark
                test.save()

        return redirect('show_students_answers', id=test.id)

    context = {
        'test': test,
        'tasks_answers': tasks_answers,
        'student': test.student
    }
    return render(request, 'tests/show_students_answers.html', context=context)


#lista testow stworzonych przez nauczyciea, widok nauczyciela
@paid_subscription
@teacher_only
def test_list(request):
    tests = BlankTest.objects.filter(teacher=request.user.teacher).all()
    return render(request, 'tests/tests.html', {'tests': tests})


#po wybraniu testu wyswietla sie uczniow ktorzy rozwiazali ten test
@paid_subscription
@allowed_teacher_to_blanktest
def test_students(request, id):
    tests = get_object_or_404(BlankTest, id=id).students_tests
    # tests = BlankTest.objects.get(id=id).students_tests
    return render(request, 'tests/students.html', {'tests': tests})


#edytuj test
@paid_subscription
@allowed_teacher_to_blanktest
def edit_test(request, id):
    test = get_object_or_404(BlankTest, id=id)
    context = {
        'test': test,
        'tasks': test.tasks
    }
    if request.method == 'POST':
        test.label = request.POST['nazwa']
        for task in test.tasks:
            task.content = request.POST[f'{task.id}_polecenie']
            if request.FILES:
                if f"image_{task.id}" in request.FILES.keys():
                    task.image = request.FILES[f'image_{task.id}']
                    task.save()

            if task.type.label == 'zamkniete':
                for option in task.answer_options:
                    option.label = request.POST[f'{option.id}_label']
                    if request.POST[f'{option.id}_is_correct'] == 'tak':
                        option.is_correct = True
                    else:
                        option.is_correct = False

                    option.save()

            if task.correct_answer:
                task.correct_answer = request.POST[f'{task.id}_poprawnaodpowiedz']
            task.points = request.POST[f'{task.id}_points']
            task.save()
        test.save()
        students_test = Test.objects.get(blank_test=test)
        students_test.label = test.label
        students_test.save()

        return redirect('task_list', id=test.id)
    return render(request, 'tests/edit_test.html', context=context)


@paid_subscription
@allowed_teacher_to_blanktest
def delete_test(request, id):
    test = get_object_or_404(BlankTest, id=id)
    if request.method == 'POST':
        test.delete()
        return redirect('test_list')
    return render(request, 'tests/delete_test.html', {'test': test})


@paid_subscription
@allowed_teacher_to_tests_task
def delete_task(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        task.delete()
        return redirect('edit_test', id=task.test.id)
    return render(request, 'tests/delete_task.html', {'task': task})


@paid_subscription
@allowed_teacher_to_blanktest
def activate_or_deactivate_test(request, id):
    if request.method == 'POST':
        blanktest = get_object_or_404(BlankTest, id=id)
        if blanktest.is_active:
            blanktest.is_active = False
        else:
            blanktest.is_active = True
        blanktest.save()

        for test in blanktest.tests:
            if test.is_active:
                test.is_active = False
            else:
                test.is_active = True
            test.save()
        return redirect('task_list', id=id)
    return redirect('task_list', id=id)


@paid_subscription
@allowed_teacher_to_blanktest
def add_threshold(request, id):
    blank_test = get_object_or_404(BlankTest, id=id)
    context = {
        'blanktest': blank_test
    }
    if request.method == 'POST':
        try:
            Mark.objects.create(
                mark=request.POST['mark'],
                from_percent=request.POST['from_percent'],
                to_percent=request.POST['to_percent'],
                blank_test=blank_test
            )
        except:
            messages.error(request, 'cos poszlo nie tak')
        return redirect('add_threshold', blank_test.id)
    return render(request, 'tests/threshold.html',context=context)


@paid_subscription
@allowed_teacher_to_blanktest
def edit_threshold(request, id):
    blank_test = get_object_or_404(BlankTest, id=id)
    context = {
        'blanktest': blank_test
    }
    if request.method == 'POST':
        for mark in blank_test.threshold:
            mark.mark = request.POST[f'{mark.id}_mark']
            mark.from_percent = request.POST[f'{mark.id}_from_percent']
            mark.to_percent = request.POST[f'{mark.id}_to_percent']
            mark.save()
        return redirect('task_list', id=blank_test.id)
    return render(request, 'tests/edit_threshold.html',context=context)


@paid_subscription
@allowed_teacher_to_blanktest
def delete_entire_threshold(request, id):
    blank_test = get_object_or_404(BlankTest, id=id)
    context = {
        'blanktest': blank_test
    }
    if request.method == 'POST':
        blank_test.threshold.delete()
        return redirect('task_list', id=blank_test.id)
    return render(request, 'tests/delete_all_thresholds.html', context=context)


@paid_subscription
@allowed_teacher_to_blanktest
def delete_threshold(request, id, mark_id):
    if request.method == 'POST':
        blank_test = get_object_or_404(BlankTest, id=id)
        mark = get_object_or_404(Mark, id=mark_id)
        mark.delete()
        return redirect('edit_threshold', id=blank_test.id)
    return render(request, 'tests/edit_threshold.html')


@paid_subscription
@allowed_teacher_to_tests_task
def delete_image(request, id):
    if request.method == "POST":
        task = get_object_or_404(Task, id=id)
        task.image = ''
        task.save()
        return redirect('edit_test', id=task.test.id)
    return redirect('home')
