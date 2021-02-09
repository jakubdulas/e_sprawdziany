from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class School(models.Model):
    name = models.CharField(max_length=128)
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=10)
    is_paid = models.BooleanField(default=False)
    free_trial_up = models.BooleanField(default=False)
    join_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.name)

    def get_teachers(self):
        return self.teacher_set.all()


class SchoolYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    start = models.DateField(null=True)
    end = models.DateField(null=True)

    def __str__(self):
        return str(self.name)


class SchoolTerm(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    number = models.IntegerField()
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f"{self.school.name} | Semestr {self.number}"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user} | teacher"

    @property
    def is_headmaster(self):
        if Headmaster.objects.filter(teacher=self):
            return True
        return False

    def is_in_class(self, key):
        try:
            if SchoolClass.objects.get(access_key=key).teacher == self:
                return True
            else:
                return False
        except:
            pass
        return False


class Subject(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.user.username} | student"


class ClassTemplate(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    subjects_1 = models.ManyToManyField(Subject, blank=True, related_name='subjects1')
    subjects_2 = models.ManyToManyField(Subject, blank=True, related_name='subjects2')
    subjects_3 = models.ManyToManyField(Subject, blank=True, related_name='subjects3')
    subjects_4 = models.ManyToManyField(Subject, blank=True, related_name='subjects4')
    subjects_5 = models.ManyToManyField(Subject, blank=True, related_name='subjects5')
    subjects_6 = models.ManyToManyField(Subject, blank=True, related_name='subjects6')
    subjects_7 = models.ManyToManyField(Subject, blank=True, related_name='subjects7')
    subjects_8 = models.ManyToManyField(Subject, blank=True, related_name='subjects8')


class SchoolClass(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    number = models.IntegerField(default=1)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    class_template = models.ForeignKey(ClassTemplate, null=True, on_delete=models.SET_NULL)
    students = models.ManyToManyField(Student, blank=True)

    class Meta:
        verbose_name_plural = 'Classes'

    def __str__(self):
        if self.class_template:
            return f"{self.number} {self.class_template.name}"
        return f"{self.number}"

    @property
    def members_quantity(self):
        return self.students.count()

    @property
    def tests(self):
        return self.blanktest_set.all()


class Group(models.Model):
    related_classes = models.ManyToManyField(SchoolClass)
    subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, blank=True)
    teacher = models.ForeignKey(Teacher, null=True, on_delete=models.SET_NULL)
    students = models.ManyToManyField(Student, blank=True)

    def __str__(self):
        return str(self.name)


class Headmaster(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, null=True)
    school = models.OneToOneField(School, on_delete=models.CASCADE, null=True, blank=True)


class Bell(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    number_of_lesson = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.school.name} | {self.number_of_lesson}"


class ScheduleElement(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)
    bell = models.ForeignKey(Bell, on_delete=models.SET_NULL, null=True)
    day_of_week = models.IntegerField()


class Lesson(models.Model):
    schedule_element = models.ForeignKey(ScheduleElement, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True, null=True)
    notes = models.TextField()
    homework = models.TextField()
