from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .decorators import *
from .forms import *
from general.decorators import *
from general.forms import *
import random
from django.forms import inlineformset_factory
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
    form = CreateClassTemplateForm()
    if request.method == 'POST':
        form = CreateClassTemplateForm(request.POST)
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
    bells = Bell.objects.filter(school=request.user.teacher.school).all()
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
    list = []
    for student in group.students.all():
        list.append(
            tuple(
                (
                    student.user.first_name,
                    student.user.last_name,
                    student.grade_set.filter(subject=group.subject).all()
                )
            )
        )

    context = {
        'group': group,
        'list': list
    }
    return render(request, 'teacher/group_details.html', context)


def start_lesson(request):
    if request.method == "POST":
        bell = Bell.objects.filter(
            start_time__lte=datetime.datetime.today().time(),
            end_time__gte=datetime.datetime.today().time(),
            school=request.user.teacher.school,
        ).first()

        if not bell:
            return redirect('home')

        schedule_element = ScheduleElement.objects.filter(
            bell=bell,
            day_of_week=datetime.datetime.today().weekday(),
            teacher=request.user.teacher
        ).first()

        if not schedule_element:
            return redirect('home')

        lesson = Lesson.objects.filter(
            schedule_element=schedule_element,
            date=datetime.datetime.today().date()
        ).first()

        if not lesson:
            lesson = Lesson.objects.create(
                schedule_element=schedule_element,
            )

        return redirect('lesson_details', lesson.id)
    return redirect('home')


def lesson_details(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    context = {
        'lesson': lesson
    }

    return render(request, 'teacher/lesson.html', context)

