from datetime import datetime, timedelta
from django.shortcuts import reverse
from calendar import HTMLCalendar
from django.db.models import Q
from .models import *


class TeachersCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, teacher=None):
        self.year = year
        self.month = month
        self.teacher = teacher
        super(TeachersCalendar, self).__init__()

    def formatday(self, day, teachers_absences, events, canceled_lessons, replacements):
        teachers_absences_per_day = teachers_absences.filter(
            date__day=day
        ).all()
        events_per_day = events.filter(
            date__day=day
        ).all()
        canceled_lessons_per_day = canceled_lessons.filter(
            date__day=day
        ).all()
        replacements_per_day = replacements.filter(
            date__day=day
        ).all()
        d = ''
        for teachers_absence in teachers_absences_per_day:
            d += f"<a href='{reverse('teachers_absence_details', kwargs={'teachers_absence_id': teachers_absence.id})}'><div>Nieobecność nauczyciela: " \
                 f"{teachers_absence.teacher.user.first_name} {teachers_absence.teacher.user.last_name}</div><br>"

        for canceled_lesson in canceled_lessons_per_day:
            d += f"<div>Odwołana lekcja: {canceled_lesson.schedule_element.group.subject.name}</div><br>"

        for event in events_per_day:
            d += f"<div>{event.type} na lekcji: {event.schedule_element.group.subject.name}</div><br>"
        for replacement in replacements_per_day:
            d += f"<div>Zastępstwo na lekcji: {replacement.schedule_element.group.subject.name} z klasa</div><br>"
        if day != 0:
            return f"<td><span>{day}</span>{d}</td>"
        return "<td></td>"

    def formatweek(self, theweek, teachers_absences, events, canceled_lessons, replacements):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, teachers_absences, events, canceled_lessons, replacements)
        return f"<tr>{week}</tr>"

    def formatmonth(self, withyear=True):
        teachers_absences = TeachersAbsence.objects.filter(
            date__year=self.year,
            date__month=self.month,
            teacher__school=self.teacher.school
        ).all()
        events = Event.objects.filter(
            date__year=self.year,
            date__month=self.month,
            schedule_element__teacher=self.teacher
        ).all()
        canceled_lessons = Lesson.objects.filter(
            is_canceled=True,
            date__year=self.year,
            date__month=self.month,
            schedule_element__teacher=self.teacher
        ).all()
        replacements = Replacement.objects.filter(
            Q(teacher=self.teacher) | Q(schedule_element__teacher=self.teacher),
            date__year=self.year,
            date__month=self.month,
        )

        cal = f"<table border='1'>{self.formatmonthname(self.year, self.month, withyear=withyear)}"
        cal += f"{self.formatweekheader()}"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, teachers_absences, events, canceled_lessons, replacements)}"
        cal += "</table>"
        return cal