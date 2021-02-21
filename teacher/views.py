from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.forms import inlineformset_factory
from django.utils.dateparse import parse_date
from django.db.models import Q
from .models import *
from .decorators import *
from .forms import *
from tests.forms import GiveGradeForm, FinalGradeForm
from general.decorators import *
from general.forms import *
import random
import datetime


@paid_subscription
@teacher_only
def teachers_class_list(request):
    school_year = SchoolYear.objects.filter(
        school=request.user.teacher.school,
        start__lte=datetime.datetime.today().date(),
        end__gte=datetime.datetime.today().date(),
    ).first()
    class_qs = SchoolClass.objects.filter(school_year=school_year, class_template__school=request.user.teacher.school).all()
    context = {
        'class_qs': class_qs
    }
    return render(request, 'teacher/classes.html', context=context)


@paid_subscription
@teacher_only
def teachers_class_details(request, id):
    class_room = get_object_or_404(SchoolClass, id=id)
    return render(request, "teacher/class_details.html", {"class": class_room})


@headmaster_only
def edit_school_information(request):
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    if headmaster.school:
        school = headmaster.school
        form = CreateSchool(instance=school)
        if request.method == 'POST':
            form = CreateSchool(request.POST, instance=school)
            if form.is_valid():
                form.save()
                messages.success(request, 'Zapisano zmiany')
                return redirect('home')
            messages.error(request, 'cos poszlo nie tak')
            return render('edit_school_information')
        context = {
            'form': form
        }
        return render(request, 'teacher/edit_school_information.html', context=context)
    return redirect('home')


@headmaster_only
def headmaster_panel(request):
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    teachers_qs = Teacher.objects.filter(school=headmaster.school).all()
    school_year = SchoolYear.objects.filter(
        school=request.user.teacher.school,
        start__lte=datetime.datetime.today().date(),
        end__gte=datetime.datetime.today().date(),
    ).first()

    term1 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=1, school_year=school_year).first()
    term2 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=2, school_year=school_year).first()

    context = {
        'teachers_qs': teachers_qs,
        'school': headmaster.school,
        'term1': term1,
        'term2': term2,
        'school_year': school_year
    }
    return render(request, 'teacher/headmaster_panel.html', context=context)


@headmaster_only
def dismiss_teacher(request, id):
    headmaster = Headmaster.objects.filter(teacher=request.user.teacher).first()
    teacher = get_object_or_404(Teacher, id=id)
    if headmaster.school in teacher.school.all():
        teacher.school = ''
        teacher.is_paid = False
        teacher.save()
        return redirect('headmaster_panel')
    return redirect('home')


@headmaster_only
def students_view(request):
    students_qs = Student.objects.filter(school=request.user.teacher.headmaster.school).all()
    return render(request, 'teacher/headmaster_panel-students.html', {'students': students_qs})


@headmaster_only
def teachers_view(request):
    teachers_qs = Teacher.objects.filter(school=request.user.teacher.headmaster.school).all()
    return render(request, 'teacher/headmaster_panel-teachers.html', {'teachers': teachers_qs})


@teacher_only
def class_grades_view(request, class_id):
    class_room = get_object_or_404(SchoolClass, id=class_id)
    qs = class_room.students.all()

    context = {
        'qs': qs,
        'class': class_room
    }

    return render(request, 'teacher/class_grades.html', context=context)


@teacher_only
def edit_class(request, class_id):
    class_room = get_object_or_404(SchoolClass, id=class_id)
    form = CreateClass(instance=class_room)
    if request.method == 'POST':
        form = CreateClass(request.POST, instance=class_room)
        if form.is_valid():
            form.save()
            messages.success(request, 'zapisano zmiany')
            return redirect('teachers_class_details', class_id)
    context = {
        'form': form,
        'class': class_room
    }
    return render(request, 'teacher/edit_class.html', context=context)


@headmaster_only
def bells_view(request):
    qs = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()
    context = {
        'qs': qs
    }
    return render(request, 'teacher/bells.html', context)


@headmaster_only
def add_edit_bells(request):
    BellFormSet = inlineformset_factory(School, Bell, fields='__all__')
    formset = BellFormSet(instance=request.user.teacher.school)
    if request.method == 'POST':
        formset = BellFormSet(request.POST, instance=request.user.teacher.school)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Zaktualizowano rozkład dzwonków')
        else:
            messages.success(request, 'Wystąpił błąd. Spróbuj ponowanie.')
        return redirect('edit_bells')
    context = {
        'formset': formset
    }
    return render(request, 'teacher/edit_bell_schedule.html', context)


@teacher_only
def teacher_details(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    context = {
        'teacher': teacher
    }
    return render(request, 'teacher/teacher_details.html', context)


@headmaster_only
def edit_term(request, number):
    number = int(number)
    form = SchoolTermForm(instance=SchoolTerm.objects.filter(school=request.user.teacher.school, number=number).first())
    if request.method == 'POST':
        form = SchoolTermForm(request.POST, instance=SchoolTerm.objects.filter(school=request.user.teacher.school, number=number).first())
        form.instance.number = number
        form.instance.school = request.user.teacher.school
        if form.is_valid():
            form.save()
            messages.success(request, f'Zaktualizowano semestr {number}.')
            return redirect('headmaster_panel')
        else:
            messages.success(request, f'Wystąpił błąd')
            return redirect('add_term', number)
    context = {
        'form': form
    }
    return render(request, 'teacher/add_term.html', context)


@headmaster_only
def school_year_details(request, school_year_id):
    school_year = get_object_or_404(SchoolYear, id=school_year_id)
    term1 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=1, school_year=school_year).first()
    term2 = SchoolTerm.objects.filter(school=request.user.teacher.school, number=2, school_year=school_year).first()

    context = {
        'school_year': school_year,
        'term1': term1,
        'term2': term2
    }

    return render(request, 'teacher/school_year_details.html', context)


def add_class_template(request):
    form = CreateClassTemplateForm(school=request.user.teacher.school)
    if request.method == 'POST':
        form = CreateClassTemplateForm(request.user.teacher.school, request.POST)
        form.instance.school = request.user.teacher.school
        if form.is_valid():
            form.save()

            for i in range(4):
                obj = SchoolClass.objects.create(
                    number=i + 1,
                    school_year=SchoolYear.objects.filter(
                        school=form.instance.school,
                        start__lte=datetime.datetime.today().date(),
                        end__gte=datetime.datetime.today().date(),
                    ).first(),
                    class_template=form.instance
                )

                if i+1 == 1:
                    for sub in form.instance.subjects_1.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()
                elif i+1 == 2:
                    for sub in form.instance.subjects_2.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()
                elif i+1 == 3:
                    for sub in form.instance.subjects_3.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()
                elif i+1 == 4:
                    for sub in form.instance.subjects_4.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()
                elif i+1 == 5:
                    for sub in form.instance.subjects_5.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()
                elif i+1 == 6:
                    for sub in form.instance.subjects_6.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()
                elif i+1 == 7:
                    for sub in form.instance.subjects_7.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()
                elif i+1 == 8:
                    for sub in form.instance.subjects_8.all():
                        group = Group.objects.create(
                            subject=sub,
                            name=f"{obj.number} {obj.class_template.name} {sub.name}",
                        )
                        group.related_classes.add(obj)
                        group.students.set(obj.students.all())
                        group.save()

            messages.success(request, 'Dodano szblon klasy')
            return redirect('headmaster_panel')
    context = {
        'form': form
    }
    return render(request, 'teacher/add_class_template.html', context)


def class_groups(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    groups = school_class.group_set.all()
    context = {
        'groups': groups,
        'class': school_class
    }
    return render(request, 'teacher/class_groups.html', context)


def edit_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    form = GroupForm(instance=group)
    if request.method == "POST":
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('teachers_class_list')
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'teacher/group_edit.html', context)


def add_group(request, class_id):
    school_class = get_object_or_404(SchoolClass, id=class_id)
    form = GroupForm()
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grupa została utworzona')
            return redirect('teachers_class_list', class_id)
    context = {
        'form': form,
        'class': school_class,
    }
    return render(request, 'teacher/group_edit.html', context)


def teachers_schedule(request):
    bells = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()
    list = []
    for bell in bells:
        list.append(
            tuple(
                (
                    bell.number_of_lesson,
                    ScheduleElement.objects.filter(teacher=request.user.teacher, day_of_week=0, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, day_of_week=1, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, day_of_week=2, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, day_of_week=3, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, day_of_week=4, bell=bell).first(),
                )
            )
        )

    context = {
        'list': list
    }
    return render(request, 'teacher/teachers_schedule.html', context)


def add_schedule_element(request, day_of_week, bell):
    bell = Bell.objects.filter(school=request.user.teacher.school, number_of_lesson=bell).first()
    obj = ScheduleElement.objects.filter(teacher=request.user.teacher, bell=bell, day_of_week=day_of_week).first()
    form = ScheduleElementForm(teacher=request.user.teacher, instance=obj)
    if request.method == 'POST':
        form = ScheduleElementForm(request.user.teacher, request.POST, instance=obj)
        form.instance.day_of_week = int(day_of_week)
        form.instance.bell = bell
        form.instance.teacher = request.user.teacher
        if form.is_valid():
            form.save()
            return redirect('teachers_schedule')
    context = {
        'form': form,
        'obj': obj
    }
    return render(request, 'teacher/add_schedule_element.html', context)


def delete_schedule_element(request, schedule_element_id):
    if request.method == "POST":
        obj = get_object_or_404(ScheduleElement, id=schedule_element_id)
        obj.delete()
    return redirect('teachers_schedule')


def group_detail_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    students_qs = group.students.all().order_by('user__last_name')
    subject = group.subject

    term1_grades = []
    term2_grades = []

    term1 = SchoolTerm.objects.filter(
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
        number=1,
    ).first()
    term2 = SchoolTerm.objects.filter(
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
        number=2,
    ).first()

    term_1_sum = 0
    term_2_sum = 0
    term_1_weight = 0
    term_2_weight = 0
    term_1_mean = 0
    term_2_mean = 0

    for student in students_qs:
        for grade in Grade.objects.filter(student=student, subject=subject, school_term=term1, include_in_mean=True).all():
            term_1_sum += grade.mark.value*grade.weight
            term_1_weight += grade.weight

        if term_1_weight != 0:
            term_1_mean = term_1_sum/term_1_weight

        term1_grades.append(
            tuple(
                (
                    student,
                    Grade.objects.filter(
                        student=student,
                        subject=subject,
                        school_term=SchoolTerm.objects.filter(
                            school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
                            number=1,
                        ).first()
                    ).all(),
                    round(term_1_mean, 2),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term1, is_predicted=True,
                                              is_annual=False).first(),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term1, is_predicted=False,
                                              is_annual=False).first(),
                )
            )
        )

        for grade in Grade.objects.filter(student=student, subject=subject, school_term=term2, include_in_mean=True).all():
            term_2_sum += grade.mark.value*grade.weight
            term_2_weight += grade.weight

        if term_2_weight != 0:
            term_2_mean = term_2_sum/term_2_weight

        term2_grades.append(
            tuple(
                (
                    student,
                    Grade.objects.filter(
                        student=student,
                        subject=subject,
                        school_term=SchoolTerm.objects.filter(
                            school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
                            number=2
                        ).first()
                    ).all(),
                    round(term_2_mean, 2),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term2, is_predicted=True,
                                              is_annual=False).first(),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term2, is_predicted=False,
                                              is_annual=False).first(),
                    FinalGrade.objects.filter(subject=subject, student=student, term=None, is_annual=True).first(),
                )
            )
        )

    if request.user.teacher == group.teacher:
        is_form_teacher = True
    else:
        is_form_teacher = False

    context = {
        'group': group,
        'term1_grades': term1_grades,
        'term2_grades': term2_grades,
        'term1': term1,
        'term2': term2,
        'is_form_teacher': is_form_teacher
    }
    return render(request, 'teacher/group_details.html', context)


def start_next_lesson(request, schedule_element_id):
    if request.method == "POST":
        next_lesson = get_object_or_404(ScheduleElement, id=schedule_element_id)

        replacement = Replacement.objects.filter(
            date=datetime.datetime.today().date(),
            schedule_element=next_lesson,
        ).first()

        lesson = Lesson.objects.filter(
            schedule_element=next_lesson,
            date=datetime.datetime.today().date(),
            replacement=replacement
        ).first()

        if not lesson:
            lesson = Lesson.objects.create(
                schedule_element=next_lesson,
                replacement=replacement
            )

        return redirect('lesson_details', lesson_slug=lesson.slug)
    return redirect('home')


def lesson_details(request, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug)
    students_qs = lesson.schedule_element.group.students.all().order_by('user__last_name')
    if lesson.replacement:
        subject = lesson.replacement.subject
    else:
        subject = lesson.schedule_element.group.subject
    term1_grades = []
    term2_grades = []

    term1 = SchoolTerm.objects.filter(
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
        number=1,
    ).first()
    term2 = SchoolTerm.objects.filter(
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
        number=2,
    ).first()

    term_1_sum = 0
    term_2_sum = 0
    term_1_weight = 0
    term_2_weight = 0
    term_1_mean = 0
    term_2_mean = 0

    for student in students_qs:
        for grade in Grade.objects.filter(student=student, subject=subject, school_term=term1, include_in_mean=True).all():
            term_1_sum += grade.mark.value*grade.weight
            term_1_weight += grade.weight

        if term_1_weight != 0:
            term_1_mean = term_1_sum/term_1_weight

        term1_grades.append(
            tuple(
                (
                    student,
                    Frequency.objects.filter(lesson=lesson, student=student).first(),
                    Grade.objects.filter(
                        student=student,
                        subject=lesson.replacement.subject if lesson.replacement else lesson.schedule_element.group.subject,
                        school_term=SchoolTerm.objects.filter(
                            school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
                            number=1,
                        ).first()
                    ).all(),
                    round(term_1_mean, 2),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term1, is_predicted=True,
                                              is_annual=False).first(),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term1, is_predicted=False,
                                              is_annual=False).first(),
                )
            )
        )

        for grade in Grade.objects.filter(student=student, subject=subject, school_term=term2, include_in_mean=True).all():
            term_2_sum += grade.mark.value*grade.weight
            term_2_weight += grade.weight

        if term_2_weight != 0:
            term_2_mean = term_2_sum/term_2_weight

        term2_grades.append(
            tuple(
                (
                    student,
                    Frequency.objects.filter(lesson=lesson, student=student).first(),
                    Grade.objects.filter(
                        student=student,
                        subject=lesson.replacement.subject if lesson.replacement else lesson.schedule_element.group.subject,
                        school_term=SchoolTerm.objects.filter(
                            school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
                            number=2
                        ).first()
                    ).all(),
                    round(term_2_mean, 2),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term2, is_predicted=True,
                                              is_annual=False).first(),
                    FinalGrade.objects.filter(subject=subject, student=student, term=term2, is_predicted=False,
                                              is_annual=False).first(),
                    FinalGrade.objects.filter(subject=subject, student=student, term=None, is_annual=True).first(),
                )
            )
        )

    if request.method == 'POST':
        try:
            lesson.topic = request.POST['topic']
            lesson.notes = request.POST['notes']
            lesson.homework = request.POST['homework']
            lesson.save()
            return redirect('lesson_details', lesson_slug)
        except:
            messages.error(request, 'error')
            return redirect('lesson_details', lesson_slug)

    context = {
        'lesson': lesson,
        'term1_grades': term1_grades,
        'term2_grades': term2_grades,
        'term1': term1,
        'term2': term2,
        'subject': subject
    }

    return render(request, 'teacher/lesson.html', context)


def teachers_diary(request):

    return render(request, 'teacher/teachers_diary.html')


def schedule_replacement(request):
    classes = SchoolClass.objects.filter(
        class_template__school=request.user.teacher.school,
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school)
    ).all()
    bells = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()
    teachers = Teacher.objects.filter(school=request.user.teacher.school).all()
    subjects = request.user.teacher.school.subjects.all()

    if request.method == 'POST':
        try:
            schedule_element = ScheduleElement.objects.filter(
                day_of_week=datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').weekday(),
                group__related_classes=SchoolClass.objects.get(id=int(request.POST['class'])),
                teacher=Teacher.objects.get(id=int(request.POST['teacher'])),
                bell=Bell.objects.get(id=int(request.POST['bell']))
            ).first()

            if not schedule_element:
                messages.error(request, 'Ta klasa nie ma w tym czasie lekcji')
                return redirect('schedule_replacement')

            Replacement.objects.create(
                date=datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date(),
                schedule_element=schedule_element,
                teacher=Teacher.objects.get(id=int(request.POST['proxy'])),
                subject=Subject.objects.get(id=int(request.POST['subject']))
            )

            # Lesson.objects.create(
            #     schedule_element=schedule_element,
            #     date=
            # )
            messages.success(request, 'Zaplanowano zastępstwo')
            return redirect('teachers_diary')
        except:
            messages.error(request, 'Zastępstwo nie zostało utworzone. Spróbuj ponownie')
            return redirect('schedule_replacement')

    context = {
        'classes': classes,
        'bells': bells,
        'teachers': teachers,
        'subjects': subjects
    }
    return render(request, 'teacher/schedule_replacement.html', context)


def cancel_lesson(request):
    classes = SchoolClass.objects.filter(
        class_template__school=request.user.teacher.school,
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school)
    ).all()
    bells = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()

    if request.method == "POST":
        try:
            schedule_element = ScheduleElement.objects.filter(
                day_of_week=datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').weekday(),
                group=Group.objects.get(id=int(request.POST['group'])),
                bell=Bell.objects.get(id=int(request.POST['bell']))
            ).first()

            if not schedule_element:
                messages.error(request, 'Klasa nie ma wtedy lekcji')
                return redirect('cancel_lesson')

            Lesson.objects.create(
                schedule_element=schedule_element,
                date=datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').date(),
                is_canceled=True
            )
            return redirect('teachers_diary')
        except:
            messages.error(request, 'Coś poszło nie tak')
            return redirect('cancel_lesson')

    context = {
        'classes': classes,
        'bells': bells
    }

    return render(request, 'teacher/cancel_lesson.html', context)


def get_groups_ajax(request, schoolclass_id):
    if request.is_ajax():
        schoolclass = SchoolClass.objects.get(id=schoolclass_id)
        groups = list(schoolclass.group_set.values('name', 'id'))
        return JsonResponse({'groups': groups})
    return redirect('home')


def lesson_list(request):
    lessons = Lesson.objects.filter(
        Q(schedule_element__teacher=request.user.teacher) | Q(replacement__teacher=request.user.teacher)
    ).order_by('-date', '-schedule_element__bell__number_of_lesson').all()

    context = {
        'lessons': lessons
    }

    return render(request, 'teacher/lesson_list.html', context)


#sprawdzanie obecnosci
def take_the_register(request, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug)
    students_qs = lesson.schedule_element.group.students.all().order_by('user__last_name')
    students = []
    for student in students_qs:
        students.append(
            tuple(
                (
                    student,
                    Frequency.objects.filter(lesson=lesson, student=student).first()
                )
            )
        )
    context = {
        'students': students,
        'lesson': lesson
    }

    if request.method == 'POST':
        for student, frequency in students:
            if frequency:
                frequency.is_absent = False
                frequency.is_late = False
                frequency.is_exempt = False

                if f"frequency_{student.id}" in request.POST.keys():
                    if request.POST[f"frequency_{student.id}"] == 'present':
                        frequency.delete()
                    elif request.POST[f"frequency_{student.id}"] == 'absent':
                        frequency.is_absent = True
                        frequency.save()
                    elif request.POST[f"frequency_{student.id}"] == 'late':
                        frequency.is_late = True
                        frequency.save()
                    elif request.POST[f"frequency_{student.id}"] == 'exempt':
                        frequency.is_exempt = True
                        frequency.save()
            else:
                if f"frequency_{student.id}" in request.POST.keys():
                    if request.POST[f"frequency_{student.id}"] == 'absent':
                        Frequency.objects.create(
                            lesson=lesson,
                            student=student,
                            term=SchoolTerm.get_current_school_term(request.user.teacher.school),
                            is_absent=True
                        )
                    elif request.POST[f"frequency_{student.id}"] == 'late':
                        Frequency.objects.create(
                            lesson=lesson,
                            student=student,
                            term=SchoolTerm.get_current_school_term(request.user.teacher.school),
                            is_late=True
                        )
                    elif request.POST[f"frequency_{student.id}"] == 'exempt':
                        Frequency.objects.create(
                            lesson=lesson,
                            student=student,
                            term=SchoolTerm.get_current_school_term(request.user.teacher.school),
                            is_exempt=True
                        )
        return redirect('lesson_details', lesson_slug)
    return render(request, 'teacher/take_the_register.html', context)


def add_grade(request, student_id, subject_id, school_term_id):
    subject = get_object_or_404(Subject, id=subject_id)
    student = get_object_or_404(Student, id=student_id)
    school_term = get_object_or_404(SchoolTerm, id=school_term_id)
    form = GiveGradeForm()
    context = {
        'form': form
    }
    if request.method == 'POST':
        form = GiveGradeForm(request.POST)
        form.instance.teacher = request.user.teacher
        form.instance.subject = subject
        form.instance.student = student
        form.instance.school_term = school_term
        if form.is_valid():
            form.save()
            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
            # return redirect('lesson_details', lesson_slug)
        else:
            messages.error(request, 'Wystapil blad')
    return render(request, 'teacher/give_grade.html', context)


def add_final_grade(request, student_id, school_term_id, subject_id, is_predicted, is_annual):
    form = FinalGradeForm
    context = {
        'form': form
    }
    if request.method == 'POST':
        form = FinalGradeForm(request.POST)
        form.instance.term = SchoolTerm.objects.filter(id=school_term_id).first()
        form.instance.is_predicted = True if is_predicted == 1 else False
        form.instance.is_annual = True if is_annual == 1 else False
        form.instance.subject = Subject.objects.filter(id=subject_id).first()
        form.instance.student = Student.objects.filter(id=student_id).first()
        form.instance.teacher = request.user.teacher
        if form.is_valid():
            form.save()
            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
    return render(request, 'teacher/add_final_grade.html', context)


def edit_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    form = GiveGradeForm(instance=grade)
    context = {
        'form': form,
        'grade': grade
    }
    if request.method == 'POST':
        form = GiveGradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
    return render(request, 'teacher/give_grade.html', context)


def delete_grade(request, grade_id):
    grade = get_object_or_404(Grade, id=grade_id)
    if request.method == 'POST':
        grade.delete()
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
    return redirect('home')


def edit_final_grade(request, final_grade_id):
    grade = get_object_or_404(FinalGrade, id=final_grade_id)
    form = FinalGradeForm(instance=grade)
    context = {
        'form': form,
        'grade': grade
    }
    if request.method == 'POST':
        form = FinalGradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
    return render(request, 'teacher/add_final_grade.html', context)


def delete_final_grade(request, final_grade_id):
    grade = get_object_or_404(FinalGrade, id=final_grade_id)
    if request.method == 'POST':
        grade.delete()
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
    return redirect('home')


def add_grades_to_all_students(request, group_id, term_id, subject_id):
    group = get_object_or_404(Group, id=group_id)
    term = get_object_or_404(SchoolTerm, id=term_id)
    subject = get_object_or_404(Subject, id=subject_id)
    grades = request.user.teacher.school.grades.all()

    if request.method == 'POST':
        try:
            for student in group.students.all():
                print(request.POST['category'])
                print()
                print()
                print()
                if f"{student.id}_grade" in request.POST.keys():
                    if request.POST[f"{student.id}_grade"] != '-1':
                        Grade.objects.create(
                            mark=GradeTemplate.objects.filter(id=request.POST.get(f"{student.id}_grade")).first(),
                            teacher=request.user.teacher,
                            subject=subject,
                            student=student,
                            category=request.POST['category'],
                            description=request.POST['description'],
                            weight=int(request.POST['weight']),
                            school_term=term,
                            include_in_mean=True if request.POST['include_in_mean'] else False
                        )
            next = request.POST.get('next', '/')
            return HttpResponseRedirect(next)
        except:
            messages.error(request, 'cos poszlo nie tak')
            return redirect('add_grades_to_all_students', group_id, term_id, subject_id)
    context = {
        'grades': grades,
        'students': group.students.order_by('user__last_name').all(),
    }

    return render(request, 'teacher/add_grades_to_all_students.html', context)