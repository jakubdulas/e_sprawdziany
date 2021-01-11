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
import base64
from django.core.files.base import ContentFile

# Create your views here.


#rozwiązywanie testu
@allowed_student
def test(request, test_id):
    # test = Test.objects.get(id=id)
    test = get_object_or_404(Test, id=test_id)
    #!!!!!!!!!! odkomentować gry doda sie frontend !!!!!!!!!!!
    end = datetime.datetime.now() + test.blank_test.countdown
    # test.is_active = False
    # test.is_done = False
    test.save()
    context = {
        'test': test,
        'tasks': test.tasks,
        'end_test': end.strftime("%m %d, %Y %H:%M:%S"),
    }

    return render(request, 'tests/test.html', context=context)


def save_answers(request, test_id):
    if request.method == "POST":
        test = get_object_or_404(Test, id=test_id)
        student = request.user.student
        test.is_active = False
        test.is_done = True
        test.save()
        earned_total = 0
        total = 0
        for task in test.tasks:
            answer = Answer.objects.create(
                student=student,
                task=task,
            )
            total += task.points
            if f"{task.id}" in request.POST.keys():
                if task.type.label == 'otwarte':
                    answer.textarea = request.POST[f"{task.id}"]
                elif task.type.label == 'zamkniete':
                    answer_option = AnswerOption.objects.get(id=int(request.POST[f"{task.id}"]))
                    answer.char_field = answer_option.label
                    answer.answer_option = answer_option
                    if answer_option.is_correct:
                        answer.is_correct = True
                        answer.earned_points = task.points
                        earned_total += answer.earned_points
                elif task.type.label == 'krotka odpowiedz':
                    answer.char_field = request.POST[f'{task.id}']
                    if task.correct_answer != '':
                        if test.blank_test.ignore_upper_case:
                            if answer.char_field.lower() == task.correct_answer.lower():
                                answer.is_correct = True
                                answer.earned_points = task.points
                                earned_total += answer.earned_points
                        else:
                            if answer.char_field == task.correct_answer:
                                answer.is_correct = True
                                answer.earned_points = task.points
                                earned_total += answer.earned_points
                elif task.type.label == 'tablica':
                    try:
                        data = request.POST[f'{task.id}']
                        format, imgstr = data.split(';base64,')
                        ext = format.split('/')[-1]
                        img = ContentFile(base64.b64decode(imgstr), name=f'board{task.id}.' + ext)
                        answer.board = img
                    except:
                        pass
            if task.type.label == 'prawda/fałsz':
                for option in task.truefalsetask_set.all():
                    answer_for_tf = AnswerForTF.objects.create(
                        answer=answer,
                        true_false=option,
                    )
                    if f"{option.id}_tf" in request.POST.keys():
                        if request.POST[f'{option.id}_tf'] == 'true':
                            answer_for_tf.checked = True
                            if option.is_correct:
                                answer_for_tf.is_correct = True
                                if option.points != 0:
                                    answer.earned_points += option.points
                                    earned_total += answer.earned_points
                        else:
                            answer_for_tf.checked = False
                            if not option.is_correct:
                                answer_for_tf.is_correct = True
                                if option.points != 0:
                                    answer.earned_points += option.points
                                    earned_total += answer.earned_points
                    answer.save()
                    answer_for_tf.save()

                if (AnswerForTF.objects.filter(is_correct=True, task=task).all().count() == task.truefalsetask_set.all().count()
                    and TrueFalseTask.objects.filter(task=task, points=0).all().count() == task.truefalsetask_set.all().count()):
                    earned_total += task.points
                else:
                    earned_total += 0
            answer.save()
        test.total_points = earned_total
        test.save()
        if total != 0:
            percent = round(earned_total * 100 / total)
            if test.blank_test.autocheck:
                for mark in test.blank_test.threshold:
                    if mark.to_percent >= percent >= mark.from_percent:
                        test.mark = mark.mark
                        Grade.objects.create(
                            teacher=test.blank_test.teacher,
                            test=test,
                            student=student,
                            mark=mark.mark,
                            category=test.label,
                            description=f"{earned_total}/{total}"
                        )
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
            test = BlankTest.objects.create(label=label, teacher=request.user.teacher,
                                            countdown=countdown)

            students = Class.objects.get(id=int(request.POST['class']))
            test.students = students
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
        task = Task.objects.create(
            test=test,
            content=request.POST['content'],
            type=TypeOfTask.objects.get(id=int(request.POST['type'])),
            points=request.POST['points']
        )

        tests = Test.objects.filter(blank_test=test).all()

        if request.FILES:
            if 'image' in request.FILES.keys():
                task.image = request.FILES['image']
            if 'file' in request.FILES.keys():
                task.file = request.FILES['file']

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
            answer = AnswerOption.objects.create(
                task=task,
                label=request.POST['label'],
                is_correct=is_correct
            )
            if request.FILES:
                answer.img = request.FILES['img']
            answer.save()
        except:
            messages.error(request, 'nie udalo sie dodac odpowiedzi')

    return render(request, 'tests/add_answer_option.html', context=context)


# @paid_subscription
# @allowed_teacher_to_blanktest
@allowed_teacher('blank_test')
def add_answer_option_ajax(request, blank_test_id):
    if request.is_ajax():
        data = {}
        if request.POST['is_correct'] == '1':
            is_correct = True
        else:
            is_correct = False
        obj = AnswerOption.objects.create(
            task=Task.objects.get(id=request.POST['task_id']),
            label=request.POST['text'],
            is_correct=is_correct
        )
        if request.FILES:
            obj.img = request.FILES['img']
            obj.save()
            data['imgUrl'] = obj.img.url
        data['ansOptionLabel'] = obj.label
        return JsonResponse(data)


@allowed_teacher('blank_test')
def add_answer_option_edit_task(request, blank_test_id, task_id):
    if request.is_ajax():
        data = {}
        if request.POST['is_correct'] == '1':
            is_correct = True
        else:
            is_correct = False
        obj = AnswerOption.objects.create(
            task=Task.objects.get(id=request.POST['task_id']),
            label=request.POST['text'],
            is_correct=is_correct
        )
        if request.FILES:
            obj.img = request.FILES['img']
            obj.save()
            data['imgUrl'] = obj.img.url
        data['ansOptionLabel'] = obj.label
        return JsonResponse(data)


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

        test.total_points = earned_total
        test.save()

        if total != 0:
            percent = earned_total * 100 / total

            for mark in test.blank_test.threshold:
                if mark.to_percent >= percent >= mark.from_percent:
                    obj, created = Grade.objects.get_or_create(
                        teacher=test.blank_test.teacher,
                        test=test,
                        student=test.student
                    )
                    obj.mark = mark.mark
                    obj.category = test.label,
                    obj.description = f"{earned_total}/{total}"

                    obj.save()
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
        test.label = request.POST['name']

        if 'are_exits_allowed' in request.POST.keys():
            if request.POST['are_exits_allowed'] == 'on':
                test.are_exists_allowed = False
                test.allowed_exits = request.POST['allowed_exits']
        else:
            test.are_exists_allowed = True

        print(request.POST)

        if 'ignore_upper' in request.POST.keys():
            if request.POST['ignore_upper'] == 'on':
                ignore_upper = True
        else:
            ignore_upper = False

        test.ignore_upper_case = ignore_upper

        test.countdown = parse_duration(request.POST['countdown'])

        test.save()
        students_test = Test.objects.get(blank_test=test)
        students_test.label = test.label
        students_test.save()

        return redirect('task_list', blank_test_id=test.id)
    return render(request, 'tests/edit_test.html', context=context)


@allowed_teacher('blank_test')
def edit_task(request, blank_test_id, task_id):
    task = get_object_or_404(Task, id=task_id)
    test = get_object_or_404(BlankTest, id=blank_test_id)

    if request.method == 'POST':
        task.content = request.POST['content']
        task.points = int(request.POST['points'])

        if request.FILES:
            if 'image' in request.FILES.keys():
                task.image = request.FILES['image']
            if 'file' in request.FILES.keys():
                task.file = request.FILES['file']

        if task.type.label == 'zamkniete':
            for option in task.answer_options:
                option.label = request.POST[f'{option.id}_label']
                if f'{option.id}_is_correct' in request.POST.keys():
                    if request.POST[f'{option.id}_is_correct'] == 'on':
                        option.is_correct = True
                else:
                    option.is_correct = False
                if request.FILES:
                    if f"{option.id}_image" in request.FILES.keys():
                        option.img = request.FILES[f'{option.id}_image']
                option.save()

        if task.type.label == 'krotka odpowiedz':
            task.correct_answer = request.POST['correct_answer']

        if task.type.label == 'prawda/fałsz':
            for option in task.truefalsetask_set.all():
                option.content = request.POST[f"{option.id}_content"]
                if request.POST[f'{option.id}_is_correct'] == 'true':
                    option.is_correct = True
                else:
                    option.is_correct = False

                option.points = request.POST[f"{option.id}_points"]
                option.save()

        task.save()
        return redirect('edit_task', test.id, task.id)

    return render(request, 'tests/edit_task.html', {"task": task, 'test': test})


@allowed_teacher('blank_test')
def get_answer_options(request, blank_test_id, task_id):
    if request.is_ajax():
        qs = list(Task.objects.filter(id=task_id).first().answer_options.values())
        return JsonResponse({'qs': qs})


@allowed_teacher('blank_test')
def get_true_false_sentences(request, blank_test_id, task_id):
    if request.is_ajax():
        task = get_object_or_404(Task, id=task_id)
        qs = list(task.truefalsetask_set.all().values())
        return JsonResponse({'qs': qs})


@allowed_teacher('blank_test')
def add_true_false_sentence(request, blank_test_id, task_id):
    if request.is_ajax():
        task = get_object_or_404(Task, id=task_id)
        if request.POST['is_correct'] == 'true':
            is_correct = True
        else:
            is_correct = False

        TrueFalseTask.objects.create(
            task=task,
            content=request.POST['content'],
            is_correct=is_correct,
            points=request.POST['points']
        )
        return JsonResponse({'data': 'sent'})


@allowed_teacher('blank_test')
def delete_answer_option_edit_task(request, blank_test_id, task_id, ans_opt_id):
    ans_opt = get_object_or_404(AnswerOption, id=ans_opt_id)
    ans_opt.delete()
    return redirect('edit_task', blank_test_id, task_id)


@allowed_teacher('blank_test')
def delete_true_false_sentence(request, blank_test_id, task_id, tf_id):
    tf = get_object_or_404(TrueFalseTask, id=tf_id)
    tf.delete()
    return redirect('edit_task', blank_test_id, task_id)

@allowed_teacher('blank_test')
def delete_img_from_answer_option(request, blank_test_id, task_id, ans_opt_id):
    ans_opt = get_object_or_404(AnswerOption, id=ans_opt_id)
    ans_opt.img = ''
    ans_opt.save()
    return redirect('edit_task', blank_test_id, task_id)


@allowed_teacher('task')
def delete_audio_file(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.file = ''
    task.save()
    return redirect('edit_task', task.test.id, task.id)


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
        return redirect('task_list', blank_test_id=task.test.id)
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
            Threshold.objects.create(
                mark=request.POST['mark'],
                from_percent=request.POST['from_percent'],
                to_percent=request.POST['to_percent'],
                blank_test=blank_test
            )
        except:
            messages.error(request, 'cos poszlo nie tak')
        return redirect('add_threshold', blank_test.id)
    return render(request, 'tests/threshold.html', context=context)


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
def delete_threshold(request, blank_test_id, threshold_id):
    if request.method == 'POST':
        blank_test = get_object_or_404(BlankTest, id=blank_test_id)
        mark = get_object_or_404(Threshold, id=threshold_id)
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
        return redirect('edit_task', task.test.id, task.id)
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


@allowed_student
def send_test_log(request, test_id):
    if request.is_ajax():
        TestLog.objects.create(
            test=Test.objects.get(id=test_id),
            context=request.POST['text']
        )
        return JsonResponse({'data': 'wyslano'})


@allowed_teacher('test')
def test_logs(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    qs = test.get_logs()
    return render(request, 'tests/test_logs.html', {'test': test, 'logs': qs})


@allowed_teacher('blank_test')
def add_truefalse_option_ajax(request, blank_test_id):
    if request.is_ajax():
        task = get_object_or_404(Task, id=request.POST['task_id'])
        data = {}
        if request.POST['isTrue'] == '1':
            is_correct = True
            data['is_correct'] = 'PRAWDA'
        else:
            is_correct = False
            data['is_correct'] = 'FAŁSZ'

        if int(task.points) != 0:
            points = 0
        else:
            points = int(request.POST['points'])

        if request.POST['points'] != 0:
            points = int(request.POST['points'])
            task.points += points
            task.save()

        TrueFalseTask.objects.create(
            task=task,
            content=request.POST['content'],
            is_correct=is_correct,
            points=points
        )

        data['content'] = request.POST['content']
        return JsonResponse(data)