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
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from .utils import TeachersCalendar
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
    if headmaster.school == teacher.school:
        teacher.school = ''
        teacher.is_paid = False
        teacher.save()
        return redirect('headmaster_panel')
    return redirect('home')


@headmaster_only
def students_view(request):
    students_qs = Student.objects.filter(school=request.user.teacher.headmaster.school, is_graduate=False).all()
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
def add_term(request, school_year_id, number):
    if SchoolTerm.objects.filter(school=request.user.teacher.school,
                                 number=number,
                                 school_year=SchoolYear.objects.filter(id=school_year_id).first()).first() or  number > 2 or number < 1:
        return redirect('home')

    if request.method == 'POST':
        obj = SchoolTerm.objects.create(
            school=request.user.teacher.school,
            number=number,
            school_year=SchoolYear.objects.filter(id=school_year_id).first(),
            start=datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d'),
            end=datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d'),
        )
        return redirect('school_year_details', obj.school_year.id)
    return render(request, 'teacher/add_term.html')


@headmaster_only
def edit_term(request, term_id):
    school_term = get_object_or_404(SchoolTerm, id=term_id)
    if request.method == 'POST':
        school_term.start = datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d')
        school_term.end = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d')
        school_term.save()
        return redirect('school_year_details', school_term.school_year.id)
    context = {
        'school_term': school_term
    }
    return render(request, 'teacher/edit_term.html', context)


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
    date = datetime.date.today()
    list = []
    for bell in bells:
        list.append(
            tuple(
                (
                    bell.number_of_lesson,
                    ScheduleElement.objects.filter(teacher=request.user.teacher, start_date__lte=date, end_date__gte=date, day_of_week=0, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, start_date__lte=date, end_date__gte=date, day_of_week=1, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, start_date__lte=date, end_date__gte=date, day_of_week=2, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, start_date__lte=date, end_date__gte=date, day_of_week=3, bell=bell).first(),
                    ScheduleElement.objects.filter(teacher=request.user.teacher, start_date__lte=date, end_date__gte=date, day_of_week=4, bell=bell).first(),
                )
            )
        )

    context = {
        'list': list
    }
    return render(request, 'teacher/teachers_schedule.html', context)


def add_schedule_element(request, day_of_week, bell):
    bell = Bell.objects.filter(school=request.user.teacher.school, number_of_lesson=bell).first()
    date = datetime.datetime.now()
    obj = ScheduleElement.objects.filter(teacher=request.user.teacher, start_date__lte=date, end_date__gte=date, bell=bell, day_of_week=day_of_week).first()
    school_year = datetime.datetime.strptime(str(SchoolYear.get_current_school_year(request.user.teacher.school).end), '%Y-%m-%d')
    form = ScheduleElementForm(teacher=request.user.teacher)
    if request.method == 'POST':
        form = ScheduleElementForm(request.user.teacher, request.POST)
        form.instance.day_of_week = int(day_of_week)
        form.instance.bell = bell
        form.instance.teacher = request.user.teacher
        form.instance.start_date = datetime.date.today()
        form.instance.end_date = datetime.date(
            school_year.year,
            school_year.month,
            school_year.day)
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
        if Replacement.objects.filter(schedule_element=obj) or Lesson.objects.filter(schedule_element=obj) or Event.objects.filter(schedule_element=obj):
            obj.end_date = datetime.datetime.now()
            obj.save()
        else:
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


def start_lesson(request, schedule_element_id, year, month, day):
    schedule_element = get_object_or_404(ScheduleElement, id=schedule_element_id)
    date = datetime.date(year, month, day)

    replacement = Replacement.objects.filter(
        schedule_element=schedule_element,
        date=date,
        teacher=request.user.teacher
    ).first()

    if not Lesson.objects.filter(
        schedule_element=schedule_element,
        date=date):
        obj = Lesson.objects.create(
            schedule_element=schedule_element,
            date=date,
            replacement=replacement,
        )
    else:
        obj = Lesson.objects.filter(
                schedule_element=schedule_element,
                date=date).first()

    return redirect('lesson_details', lesson_slug=obj.slug)


def lesson_details(request, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug)
    students_qs = lesson.schedule_element.group.students.all().order_by('user__last_name')

    events = Event.objects.filter(
        date=lesson.date,
        schedule_element=lesson.schedule_element,
        teacher=request.user.teacher
    ).all()

    if lesson.replacement:
        subject = lesson.replacement.subject
    else:
        subject = lesson.schedule_element.group.subject

    last_lesson = None
    date = lesson.date
    for _ in range(Lesson.objects.filter(Q(replacement__subject=subject) | Q(schedule_element__group__subject=subject),
            schedule_element__group=lesson.schedule_element.group, is_canceled=False).count()):
        if date == lesson.date:
            last_lesson = Lesson.objects.filter(
                Q(replacement__subject=subject) | Q(schedule_element__group__subject=subject),
                schedule_element__group=lesson.schedule_element.group,
                is_canceled=False,
                date=date,
                schedule_element__bell__number_of_lesson__lt=lesson.schedule_element.bell.number_of_lesson
            ).exclude(id=lesson.id).order_by('-schedule_element__bell__number_of_lesson').first()
        else:
            last_lesson = Lesson.objects.filter(
                Q(replacement__subject=subject) | Q(schedule_element__group__subject=subject),
                schedule_element__group=lesson.schedule_element.group,
                is_canceled=False,
                date=date,
            ).exclude(id=lesson.id).order_by('-schedule_element__bell__number_of_lesson').first()
        if last_lesson:
            break
        date -= datetime.timedelta(1)

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
        'subject': subject,
        'last_lesson': last_lesson,
        'events': events,
    }

    return render(request, 'teacher/lesson.html', context)


def teachers_diary(request):
    d = datetime.datetime.today().date()
    cal = TeachersCalendar(d.year, d.month, request.user.teacher)
    html_cal = cal.formatmonth(withyear=True)
    context = {
        'calendar': mark_safe(html_cal)
    }
    return render(request, 'teacher/teachers_diary.html', context)


def schedule_replacement(request):
    classes = SchoolClass.objects.filter(
        class_template__school=request.user.teacher.school,
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school)
    ).all()
    bells = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()
    teachers = Teacher.objects.filter(school=request.user.teacher.school).all()
    subjects = request.user.teacher.school.subjects.all()
    date = datetime.datetime.now()

    if request.method == 'POST':
        try:
            schedule_element = ScheduleElement.objects.filter(
                day_of_week=datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').weekday(),
                group__related_classes=SchoolClass.objects.get(id=int(request.POST['class'])),
                teacher=Teacher.objects.get(id=int(request.POST['teacher'])),
                bell=Bell.objects.get(id=int(request.POST['bell'])),
                end_date__gte=date,
                start_date__lte=date
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
    date = datetime.datetime.now()

    if request.method == "POST":
        try:
            schedule_element = ScheduleElement.objects.filter(
                day_of_week=datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d').weekday(),
                group=Group.objects.get(id=int(request.POST['group'])),
                bell=Bell.objects.get(id=int(request.POST['bell'])),
                end_date__gte=date,
                start_date__lte=date
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


def get_groups_ajax(request, schoolclass_id, bell_id, day_of_week):
    date = datetime.datetime.now()
    if request.is_ajax():
        groups = []
        schedule_elements = ScheduleElement.objects.filter(
            group__related_classes=SchoolClass.objects.filter(id=schoolclass_id).first(),
            bell=Bell.objects.filter(id=bell_id).first(),
            day_of_week=day_of_week,
            end_date__gte=date,
            start_date__lte=date
        ).all()
        for schedule_element in schedule_elements:
            groups.append({
                'id': schedule_element.group.id,
                'name': schedule_element.group.name
            })
        return JsonResponse({'groups': groups})
    return redirect('home')


def lesson_list(request):
    bells = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()
    if request.is_ajax():
        start = datetime.datetime.strptime(request.POST['start'], '%Y-%m-%d')
        end = datetime.datetime.strptime(request.POST['end'], '%Y-%m-%d')
        delta = (end - start).days + 1
        week_day_name = ''

        print(start)
        print(end)

        data = {
            "mon": [],
            "tues": [],
            "wed": [],
            "thur": [],
            "fri": [],
            "number_of_lessons": bells.count()
        }

        for date in (start + datetime.timedelta(n) for n in range(delta)):
            week_day = date.weekday()
            for bell in bells:
                schedule_element = ScheduleElement.objects.filter(
                    teacher=request.user.teacher,
                    day_of_week=week_day,
                    start_date__lte=date.date(),
                    end_date__gte=date.date(),
                    bell=bell
                ).first()

                replacement = Replacement.objects.filter(
                    date=date.date(),
                    schedule_element__bell=bell,
                    teacher=request.user.teacher
                ).first()

                lesson = Lesson.objects.filter(
                    schedule_element=schedule_element,
                    date=date.date(),
                ).first()

                replacement_lesson = Lesson.objects.filter(
                    replacement=replacement
                ).first()

                if week_day == 0:
                    week_day_name = "mon"
                elif week_day == 1:
                    week_day_name = "tues"
                elif week_day == 2:
                    week_day_name = "wed"
                elif week_day == 3:
                    week_day_name = "thur"
                elif week_day == 4:
                    week_day_name = "fri"

                if replacement:
                    data[week_day_name].append(
                        {
                            "group": replacement.schedule_element.group.name,
                            "schedule_element": replacement.schedule_element.id,
                            "number_of_lesson": replacement.schedule_element.bell.number_of_lesson,
                            "is_replacement": True,
                            "is_accoplished": True if replacement_lesson else False,
                            "day_of_week": week_day,
                            "day": date.day,
                            "month": date.month,
                            "year": date.year,
                        }
                    )
                else:
                    if schedule_element:
                        data[week_day_name].append(
                            {
                                "group": schedule_element.group.name,
                                "schedule_element": schedule_element.id,
                                "number_of_lesson": schedule_element.bell.number_of_lesson,
                                "is_replacement": False,
                                "is_accoplished": True if lesson else False,
                                "is_canceled": lesson.is_canceled if lesson else False,
                                "day_of_week": week_day,
                                "day": date.day,
                                "month": date.month,
                                "year": date.year,
                            }
                        )
                    else:
                        data[week_day_name].append(None)

        return JsonResponse(data)
    context = {
        'bells': bells
    }
    return render(request, 'teacher/lesson_list.html', context)


#sprawdzanie obecnosci
def take_the_register(request, lesson_slug):
    lesson = get_object_or_404(Lesson, slug=lesson_slug)
    students_qs = lesson.schedule_element.group.students.all().order_by('user__last_name')
    students = []

    if lesson.replacement:
        subject = lesson.replacement.subject
    else:
        subject = lesson.schedule_element.group.subject

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
                    elif request.POST[f"frequency_{student.id}"] == 'unprepared':
                        frequency.delete()
                        Grade.objects.create(
                            teacher=request.user.teacher,
                            mark=GradeTemplate.objects.filter(sign='np').first(),
                            subject=subject,
                            student=student,
                            school_term=SchoolTerm.get_current_school_term(request.user.teacher.school),
                            include_in_mean=False,
                        )
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
                    elif request.POST[f"frequency_{student.id}"] == 'unprepared':
                        Grade.objects.create(
                            teacher=request.user.teacher,
                            mark=GradeTemplate.objects.filter(sign='np').first(),
                            subject=subject,
                            student=student,
                            school_term=SchoolTerm.get_current_school_term(request.user.teacher.school),
                            include_in_mean=False,
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
    form = GiveGradeForm(school=request.user.teacher.school)
    context = {
        'form': form
    }
    if request.method == 'POST':
        form = GiveGradeForm(request.POST, school=request.user.teacher.school)
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


def announcement_list(request):
    announcement_qs = Announcement.objects.filter(
        school=request.user.teacher.school,
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school)
    ).order_by('-date').all()

    context = {
        'announcement_qs': announcement_qs
    }

    return render(request, 'teacher/announcement_list.html', context)


def add_announcement(request):
    form = AnnouncementForm

    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        form.instance.teacher = request.user.teacher
        form.instance.school = request.user.teacher.school
        form.instance.school_year=SchoolYear.get_current_school_year(request.user.teacher.school)
        if form.is_valid():
            form.save()
            return redirect('announcement_list')
        else:
            messages.error(request, 'cos poszlo nie tak')
            return redirect('add_announcement')

    context = {
        'form': form
    }
    return render(request, 'teacher/add_announcement.html', context)


def edit_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    form = AnnouncementForm(instance=announcement)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            return redirect('announcement_list')
        else:
            messages.error(request, 'cos poszlo nie tak')
            return redirect('add_announcement')

    context = {
        'form': form,
        'announcement': announcement
    }
    return render(request, 'teacher/add_announcement.html', context)


def delete_announcement(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        announcement.delete()
        return redirect('announcement_list')
    return redirect('announcement_list')


def requests_for_excuse(request):
    qs = RequestForExcuse.objects.filter(
        teacher=request.user.teacher,
        school_year=SchoolYear.get_current_school_year(request.user.teacher.school),
        is_rejected=False
    ).order_by('-date').all()

    context = {
        'qs': qs
    }

    return render(request, 'teacher/requests_for_excuses.html', context)


def reject_request_for_excuse(request, request_for_excuse_id):
    if request.method == 'POST':
        obj = get_object_or_404(RequestForExcuse, id=request_for_excuse_id)
        obj.is_rejected = True
        obj.comment = request.POST['comment']
        obj.save()
        return redirect('requests_for_excuse')
    return render(request, 'teacher/reject_request_for_excuse.html')


def accept_request_for_excuse(request, request_for_excuse_id):
    if request.method == 'POST':
        obj = get_object_or_404(RequestForExcuse, id=request_for_excuse_id)
        for frequency in obj.frequency.all():
            frequency.is_absent = False
            frequency.excuse = True
            frequency.save()
        obj.delete()
        return redirect('requests_for_excuse')
    return redirect('home')


def schedule_event(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    date = datetime.datetime.now()
    schedule_elements = ScheduleElement.objects.filter(
        teacher=request.user.teacher,
        group=group,
        end_date__gte=date,
        start_date__lte=date,
        day_of_week=date.weekday()
    ).order_by('bell__number_of_lesson').all()

    if request.method == 'POST':
        Event.objects.create(
            teacher=request.user.teacher,
            date=request.POST['date'],
            schedule_element=ScheduleElement.objects.filter(id=request.POST['schedule_element']).first(),
            type=request.POST['type'],
            description=request.POST['description'],
            color=request.POST['color'],
        )
        return redirect('home')

    context = {
        'schedule_elements': schedule_elements,
        'date': date,
        'group_id': group_id,
    }
    return render(request, 'teacher/schedule_event.html', context)


def get_schedule_elements_ajax(request, group_id, day_of_week):
    date = datetime.datetime.now()
    if request.is_ajax():
        schedule_elements = list(ScheduleElement.objects.filter(
            teacher=request.user.teacher,
            group=Group.objects.filter(id=group_id).first(),
            day_of_week=day_of_week,
            end_date__gte=date,
            start_date__lte=date,
        ).order_by('bell__number_of_lesson').values('id', 'bell__number_of_lesson'))
        return JsonResponse({'schedule_elements': schedule_elements})
    return redirect('home')


def schedule_teachers_absence(request):
    teachers = Teacher.objects.filter(school=request.user.teacher.school).all()
    bells = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()

    if request.method == "POST":
        date_start = None
        date_end = None
        bell_from = None
        bell_to = None

        if request.POST['date_from']:
            date_start = datetime.datetime.strptime(request.POST['date_from'], '%Y-%m-%d')
        if request.POST['date_to']:
            date_end = datetime.datetime.strptime(request.POST['date_to'], '%Y-%m-%d')

        if request.POST['bell_from']:
            bell_from = Bell.objects.filter(id=request.POST['bell_from']).first()
        if request.POST['bell_to']:
            bell_to = Bell.objects.filter(id=request.POST['bell_to']).first()

        if (date_start and date_end) and (date_start != date_end):
            delta = datetime.timedelta(days=1)

            while date_start <= date_end:
                if datetime.datetime.strptime(request.POST['date_from'], '%Y-%m-%d') == date_start:
                    TeachersAbsence.objects.create(
                        date=date_start,
                        teacher=Teacher.objects.filter(id=request.POST['teacher']).first(),
                        from_bell=bell_from
                    )
                elif date_start == date_end:
                    TeachersAbsence.objects.create(
                        date=date_start,
                        teacher=Teacher.objects.filter(id=request.POST['teacher']).first(),
                        to_bell=bell_to
                    )
                else:
                    TeachersAbsence.objects.create(
                        date=date_start,
                        teacher=Teacher.objects.filter(id=request.POST['teacher']).first(),
                    )
                date_start += delta
        elif (date_start and not date_end) or (date_start == date_end):
            TeachersAbsence.objects.create(
                date=date_start,
                teacher=Teacher.objects.filter(id=request.POST['teacher']).first(),
                from_bell=bell_from,
                to_bell=bell_to
            )

        return redirect('teachers_diary')

    context = {
        'teachers': teachers,
        'bells': bells,
    }
    return render(request, 'teacher/schedule_teachers_absence.html', context)


def teachers_absence_details(request, teachers_absence_id):
    teachers_absence = get_object_or_404(TeachersAbsence, id=teachers_absence_id)
    context = {
        'teachers_absence': teachers_absence
    }
    return render(request, 'teacher/teachers_absence_details.html', context)


def canceled_lesson_details(request, lesson_slug):
    canceled_lesson = get_object_or_404(Lesson, slug=lesson_slug)
    context = {
        'canceled_lesson': canceled_lesson
    }
    return render(request, 'teacher/canceled_lesson_details.html', context)


def replacement_details(request, replacement_id):
    replacement = get_object_or_404(Replacement, id=replacement_id)
    context = {
        'replacement': replacement
    }
    return render(request, 'teacher/replacement_details.html', context)


def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    context = {
        'event': event
    }
    return render(request, 'teacher/event_details.html', context)


def teachers_absence_edit(request, teachers_absence_id):
    teachers_absence = get_object_or_404(TeachersAbsence, id=teachers_absence_id)
    bells = Bell.objects.filter(school=request.user.teacher.school).order_by('number_of_lesson').all()
    if request.method == 'POST':
        teachers_absence.date = datetime.datetime.strptime(request.POST['date'], '%Y-%m-%d')
        teachers_absence.from_bell = Bell.objects.filter(id=request.POST['from_bell']).first()
        teachers_absence.to_bell = Bell.objects.filter(id=request.POST['to_bell']).first()
        teachers_absence.save()
        return redirect('teachers_diary')
    context = {
        'teachers_absence': teachers_absence,
        'bells': bells
    }
    return render(request, 'teacher/teachers_absence_edit.html', context)


def teachers_absence_delete(request, teachers_absence_id):
    teachers_absence = get_object_or_404(TeachersAbsence, id=teachers_absence_id)
    if request.method == 'POST':
        teachers_absence.delete()
    return redirect('teachers_diary')


def canceled_lesson_delete(request, lesson_slug):
    canceled_lesson = get_object_or_404(Lesson, slug=lesson_slug)
    if request.method == 'POST':
        canceled_lesson.is_canceled = False
        canceled_lesson.save()
    return redirect('teachers_diary')


def replacement_edit(request, replacement_id):
    replacement = get_object_or_404(Replacement, id=replacement_id)
    context = {
        'replacement': replacement
    }
    return render(request, 'teacher/replacement_details.html', context)


def replacement_delete(request, replacement_id):
    replacement = get_object_or_404(Replacement, id=replacement_id)
    if request.method == 'POST':
        replacement.delete()
    return redirect('teachers_diary')


def event_edit(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    date = datetime.datetime.now()
    schedule_elements = ScheduleElement.objects.filter(
            teacher=request.user.teacher,
            group=event.schedule_element.group,
            end_date__gte=date,
            start_date__lte=date,
            day_of_week=event.date.weekday()
        ).order_by('bell__number_of_lesson').all()

    if request.method == 'POST':
        event.date = request.POST['date']
        event.schedule_element = ScheduleElement.objects.filter(id=request.POST['schedule_element']).first()
        event.type = request.POST['type']
        event.description = request.POST['description']
        event.color = request.POST['color']
        event.save()
        return redirect('home')

    context = {
        'event': event,
        'group_id': event.schedule_element.group.id,
        'schedule_elements': schedule_elements,
    }
    return render(request, 'teacher/schedule_event.html', context)


def end_school_year(request):
    school_year = SchoolYear.get_current_school_year(school=request.user.teacher.school)
    school_class = SchoolClass.objects.filter(teacher=request.user.teacher, school_year=school_year).first()
    students = []
    subjects = None
    i = 0

    if school_class.number == 1:
        subjects = school_class.class_template.subjects_1.order_by('name').all()
    elif school_class.number == 2:
        subjects = school_class.class_template.subjects_2.order_by('name').all()
    elif school_class.number == 3:
        subjects = school_class.class_template.subjects_3.order_by('name').all()
    elif school_class.number == 4:
        subjects = school_class.class_template.subjects_4.order_by('name').all()
    elif school_class.number == 5:
        subjects = school_class.class_template.subjects_5.order_by('name').all()
    elif school_class.number == 6:
        subjects = school_class.class_template.subjects_6.order_by('name').all()
    elif school_class.number == 7:
        subjects = school_class.class_template.subjects_7.order_by('name').all()
    elif school_class.number == 8:
        subjects = school_class.class_template.subjects_8.order_by('name').all()

    for student in school_class.students.order_by('user__last_name').all():
        students.append([])
        students[i].append(f"{student.user.first_name} {student.user.last_name}")
        for subject in subjects:
            students[i].append(
                FinalGrade.objects.filter(
                    is_predicted=False,
                    is_annual=True,
                    subject=subject,
                    student=student,
                    date__lte=school_year.end,
                    date__gte=school_year.start,
                ).first().mark if FinalGrade.objects.filter(
                    is_predicted=False,
                    is_annual=True,
                    subject=subject,
                    student=student,
                    date__lte=school_year.end,
                    date__gte=school_year.start,
                ).first() else None
            )
        students[i].append(student.id)
        i += 1

    context = {
        'subjects': subjects,
        'students': students,
    }
    return render(request, 'teacher/end_school_year.html', context)


def create_student_accounts(request, school_class_id):
    school_class = get_object_or_404(SchoolClass, id=school_class_id)
    if request.method == "POST":
        signs = "1234567890"
        username = ""
        for _ in range(9):
            username += signs[random.randint(0, len(signs) - 1)]

        while User.objects.filter(username=username):
            username = ""
            for _ in range(30):
                username += signs[random.randint(0, len(signs) - 1)]

        signs = "1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"
        password = ""
        for _ in range(30):
            password += signs[random.randint(0, len(signs) - 1)]

        us = User.objects.create(
            username=username,
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
        )
        us.set_password(password)
        us.save()

        up = User.objects.create(
            username=username+'r',
            email=request.POST['email']
        )
        up.set_password(password)
        up.save()

        s = Student.objects.create(
            user=us,
            school=request.user.teacher.school
        )

        school_class.students.add(s)

        p = Parent.objects.create(
            user=up,
            student=s
        )

        print(f"""
            nazwa użytkownika rodzica: {up.username}
            nazwa użytkownika ucznia: {us.username}
            hasło do obu kont: {password}
            """)

        send_mail(
            'Rejestracja ucznia',
            f"""
            nazwa użytkownika rodzica: {up.username}
            nazwa użytkownika ucznia: {us.username}
            hasło do obu kont: {password}
            """,
            'flask.myapp@gmail.com',
            [request.POST['email'],]
        )
        messages.error(request, 'uzytkownik zostal stworzony')

    return render(request, 'teacher/create_student_accounts.html')