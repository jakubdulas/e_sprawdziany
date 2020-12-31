from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from general.decorators import members_only
from .models import *
from teacher.decorators import teacher_only, paid_subscription
from django.contrib import messages
from .decorators import *
from .forms import *
from django.utils.dateparse import parse_duration
from django.http import JsonResponse
import random
import datetime

# Create your views here.


#rozwiązywanie testu
@allowed_student
def test(request, test_id):
    # test = Test.objects.get(id=id)
    test = get_object_or_404(Test, id=test_id)
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


def save_answers(request, test_id):
    if request.method == "POST":
        test = get_object_or_404(Test, id=test_id)
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
                elif task.type.label == 'krotka odpowiedz':
                    answer.char_field = request.POST[f'{task.id}']
                    if task.correct_answer != '':
                        if answer.char_field == task.correct_answer:
                            answer.is_correct = True
            answer.save()

        # sprawdzanie testu
        earned_total = 0
        total = 0
        for task in test.tasks:
            answer = Answer.objects.get(task=task, student=student)
            total += task.points
            if answer.is_correct:
                answer.earned_points = task.points
                earned_total += answer.earned_points
            answer.save()

        if total != 0:
            percent = round(earned_total * 100 / total)
            if test.blank_test.autocheck:
                for mark in test.blank_test.threshold:
                    if mark.to_percent >= percent >= mark.from_percent:
                        test.mark = mark.mark
                        test.save()

        if test.blank_test.autocheck and test.mark:
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
            countdown = parse_duration(request.POST['countdown'])
            test = BlankTest.objects.create(label=label, teacher=request.user.teacher, countdown=countdown)
            for classroom in request.POST.getlist('classes'):
                students = Class.objects.get(id=int(classroom))
                test.students.add(students)
                for student in students.students:
                    Test.objects.create(
                        label=label,
                        student=student,
                        blank_test=test
                    )

            if 'are_exits_allowed' in request.POST.keys():
                if request.POST['are_exits_allowed'] == 'on':
                    test.are_exists_allowed = False
                    test.allowed_exits = request.POST['allowed_exits']
            else:
                test.are_exists_allowed = True

            test.save()

            messages.success(request, "test zostal stworzony")
            return redirect('add_threshold', blank_test_id=test.id)
            # return redirect('create_task', id=test.id)
        except:
            messages.error(request, "cos poszlo nie tak")
    context = {
        'classes': classes
    }
    return render(request, 'tests/create_test.html', context=context)


#stworzenie zadania do testu i dodanie go
# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def create_task(request, blank_test_id):
    test = get_object_or_404(BlankTest, id=blank_test_id)
    types_of_task = TypeOfTask.objects.all()

    data = {}
    if request.is_ajax():
        print(request.POST)
        task = Task.objects.create(
            test=test,
            content=request.POST['content'],
            type=TypeOfTask.objects.get(id=int(request.POST['type'])),
            points=request.POST['points']
        )

        tests = Test.objects.filter(blank_test=test).all()

        if request.FILES:
            task.image = request.FILES['image']

        for t in tests:
            task.students_test.add(t)

        task.save()

        data['task_id'] = task.id
        return JsonResponse({'data': data})

    context = {
        'test': test,
        'types_of_task': types_of_task,
    }
    return render(request, 'tests/add_task.html', context=context)


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def get_json_type_of_task_data(request, blank_test_id):
    qs = list(TypeOfTask.objects.values())
    return JsonResponse({'data': qs})


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def delete_answer_option(request, blank_test_id, ans_opt_id):
    answer_option = get_object_or_404(AnswerOption, id=ans_opt_id)
    answer_option.delete()
    return redirect('edit_test', blank_test_id=blank_test_id)


#lista zadan do testu, widok nauczyciela
# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def task_list(request, blank_test_id):
    test = get_object_or_404(BlankTest, id=blank_test_id)
    # test = BlankTest.objects.get(id=test_id)

    context = {
        'test': test,
        'tasks': test.tasks
    }
    return render(request, 'tests/task_list.html', context=context)


# dodawanie poprwanej odpowiedzi do krótkiej odpwowiedzi
# @paid_subscription
# @allowed_teacher_to_tests_task
@allowed_teacher('task')
def add_correct_answer_for_short_answer(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    context = {
        'task': task
    }

    if request.method == 'POST':
        if f"{task.id}" in request.POST.keys():
            task.correct_answer = request.POST[f"{task.id}"]
            task.save()
            return redirect('task_list', blank_test_id=task.test.id)

    return render(request, 'tests/answer_for_short_answer.html', context=context)


# dodanie do zadania opcji odpowiedzi, widok nauczyciela
# @paid_subscription
# @allowed_teacher_to_tests_task
@allowed_teacher('task')
def add_answer_option(request, task_id):
    task = get_object_or_404(Task, id=task_id)
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


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def add_answer_option_ajax(request, blank_test_id):
    if request.is_ajax():
        if request.POST['is_correct'] == '1':
            is_correct = True
        else:
            is_correct = False
        obj = AnswerOption.objects.create(
            task=Task.objects.get(id=request.POST['task_id']),
            label=request.POST['text'],
            is_correct=is_correct
        )

        return JsonResponse({'ansOptionLabel': obj.label})


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def add_correct_answer_to_short_answer_ajax(request, blank_test_id):
    if request.is_ajax():
        task = Task.objects.get(id=request.POST['task_id'])
        task.correct_answer = request.POST["correct_answer"]
        task.save()

        return JsonResponse({'correct_answer': task.correct_answer})


#rozwiązany sprawdzian ucznia
# @paid_subscription
# @allowed_teacher_to_test
@allowed_teacher('test')
def show_students_answers(request, test_id):
    test = get_object_or_404(Test, id=test_id)
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

        return redirect('show_students_answers', test_id=test.id)

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


#edytuj test
# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def edit_test(request, blank_test_id):
    test = get_object_or_404(BlankTest, id=blank_test_id)
    context = {
        'test': test,
        'tasks': test.tasks
    }
    if request.method == 'POST':
        test.label = request.POST['nazwa']

        if 'are_exits_allowed' in request.POST.keys():
            if request.POST['are_exits_allowed'] == 'on':
                test.are_exists_allowed = False
                test.allowed_exits = request.POST['allowed_exits']
        else:
            test.are_exists_allowed = True

        for task in test.tasks:
            task.content = request.POST[f'{task.id}_polecenie']
            if request.FILES:
                if f"image_{task.id}" in request.FILES.keys():
                    task.image = request.FILES[f'image_{task.id}']
                    task.save()

            if task.type.label == 'zamkniete':
                for option in task.answer_options:
                    option.label = request.POST[f'{option.id}_label']
                    if f'{option.id}_is_correct' in request.POST.keys():
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

        return redirect('task_list', blank_test_id=test.id)
    return render(request, 'tests/edit_test.html', context=context)


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def delete_test(request, blank_test_id):
    test = get_object_or_404(BlankTest, id=blank_test_id)
    if request.method == 'POST':
        test.delete()
        return redirect('test_list')
    return render(request, 'tests/delete_test.html', {'test': test})


# @paid_subscription
# @allowed_teacher_to_tests_task
@allowed_teacher('task')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()
        return redirect('edit_test', blank_test_id=task.test.id)
    return render(request, 'tests/delete_task.html', {'task': task})


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def activate_or_deactivate_test(request, blank_test_id):
    if request.method == 'POST':
        blanktest = get_object_or_404(BlankTest, id=blank_test_id)
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
        return redirect('task_list', blank_test_id=blank_test_id)
    return redirect('task_list', blank_test_id=blank_test_id)


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def add_threshold(request, blank_test_id):
    blank_test = get_object_or_404(BlankTest, id=blank_test_id)
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


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def edit_threshold(request, blank_test_id):
    blank_test = get_object_or_404(BlankTest, id=blank_test_id)
    context = {
        'blanktest': blank_test
    }
    if request.method == 'POST':
        for mark in blank_test.threshold:
            mark.mark = request.POST[f'{mark.id}_mark']
            mark.from_percent = request.POST[f'{mark.id}_from_percent']
            mark.to_percent = request.POST[f'{mark.id}_to_percent']
            mark.save()
        return redirect('task_list', blank_test_id=blank_test.id)
    return render(request, 'tests/edit_threshold.html',context=context)


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def delete_entire_threshold(request, blank_test_id):
    blank_test = get_object_or_404(BlankTest, id=blank_test_id)
    context = {
        'blanktest': blank_test
    }
    if request.method == 'POST':
        blank_test.threshold.delete()
        return redirect('task_list', blank_test_id=blank_test.id)
    return render(request, 'tests/delete_all_thresholds.html', context=context)


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def delete_threshold(request, blank_test_id, mark_id):
    if request.method == 'POST':
        blank_test = get_object_or_404(BlankTest, id=blank_test_id)
        mark = get_object_or_404(Mark, id=mark_id)
        mark.delete()
        return redirect('add_threshold', blank_test_id=blank_test.id)
    return render(request, 'tests/edit_threshold.html')


# @paid_subscription
# @allowed_teacher_to_tests_task
@allowed_teacher('task')
def delete_image(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, id=task_id)
        task.image = ''
        task.save()
        return redirect('edit_test', blank_test_id=task.test.id)
    return redirect('home')


# @paid_subscription
@allowed_teacher('blank_test')
def class_tests(request, blank_test_id, class_id):
    tests = []
    classroom = get_object_or_404(Class, id=class_id)
    blank_test = get_object_or_404(BlankTest, id=blank_test_id)
    for student in classroom.students:
        tests.append(student.test_set.filter(blank_test=blank_test).first())
    return render(request, 'tests/class_tests.html', {'tests': tests})


@allowed_teacher('blank_test')
def get_answer_options_ajax(request, blank_test_id, task_id):
    if request.is_ajax():
        qs = list(Task.objects.filter(id=task_id).first().answer_options.values())
        JsonResponse({'data': qs})


@allowed_student
def student_left_test(request, test_id):
    test = Test.objects.get(id=test_id)
    data = {}
    if not test.blank_test.are_exists_allowed:
        test.exits += 1
        test.save()
        if test.exits > test.blank_test.allowed_exits:
            data['msg'] = 'end'
            return JsonResponse({'data': data})
        data['msg'] = 'Nie wychodź z testu!'
        return JsonResponse({'data': data})
    data['msg'] = ''
    return JsonResponse({'data': data})