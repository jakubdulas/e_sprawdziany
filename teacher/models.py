from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
import datetime
import random


class School(models.Model):
    name = models.CharField(max_length=128)
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=10)
    is_paid = models.BooleanField(default=False)
    free_trial_up = models.BooleanField(default=False)
    join_date = models.DateTimeField(auto_now_add=True, null=True)
    subjects = models.ManyToManyField("Subject")
    grades = models.ManyToManyField("GradeTemplate")

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

    @staticmethod
    def get_current_school_year(school):
        school_year = SchoolYear.objects.filter(
            school=school,
            start__lte=datetime.datetime.today().date(),
            end__gte=datetime.datetime.today().date(),
        ).first()
        return school_year


class SchoolTerm(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    number = models.IntegerField()
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return f"{self.school.name} | Semestr {self.number}"

    @staticmethod
    def get_current_school_term(school):
        school_term = SchoolTerm.objects.filter(
            school=school,
            start__lte=datetime.datetime.today().date(),
            end__gte=datetime.datetime.today().date(),
        ).first()
        return school_term


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
    is_graduate = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} | student"

    def get_form_teacher(self):
        obj = SchoolClass.objects.filter(
            students=self,
            school_year=SchoolYear.get_current_school_year(self.school),
        ).first()

        if obj:
            return obj.teacher
        return None

    def get_number(self, school_year):
        students_class = SchoolClass.objects.filter(
            students=self,
            school_year=school_year
        ).first()

        if students_class:
            students = list(students_class.students.all().order_by('user__last_name'))
            return students.index(self) + 1
        return None


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
    start_date = models.DateTimeField(auto_now_add=True, null=True)
    end_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.teacher.user.username} day: {self.day_of_week}, hour: {self.bell.number_of_lesson}"


class Replacement(models.Model):
    date = models.DateField()
    schedule_element = models.ForeignKey(ScheduleElement, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True)


class Lesson(models.Model):
    schedule_element = models.ForeignKey(ScheduleElement, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True, null=True)
    notes = models.TextField(blank=True)
    homework = models.TextField(blank=True)
    replacement = models.ForeignKey(Replacement, on_delete=models.SET_NULL, null=True, blank=True)
    is_canceled = models.BooleanField(default=False)
    slug = models.SlugField(null=True, unique=True)


class Frequency(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_absent = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    is_exempt = models.BooleanField(default=False)
    excuse = models.BooleanField(default=False)
    term = models.ForeignKey(SchoolTerm, on_delete=models.CASCADE)


class GradeTemplate(models.Model):
    sign = models.CharField(max_length=3, null=True)
    value = models.FloatField()

    def __str__(self):
        return self.sign


class Grade(models.Model):
    mark = models.ForeignKey(GradeTemplate, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING, blank=True, null=True)
    test = models.OneToOneField("tests.Test", on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    weight = models.IntegerField(default=0, blank=True, null=True)
    school_term = models.ForeignKey(SchoolTerm, null=True, on_delete=models.SET_NULL)
    include_in_mean = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.mark} | {self.student.user.first_name} {self.student.user.last_name}"


class FinalGrade(models.Model):
    mark = models.CharField(max_length=2)
    term = models.ForeignKey(SchoolTerm, on_delete=models.CASCADE, null=True, blank=True)
    is_predicted = models.BooleanField(default=False)
    is_annual = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)


class Announcement(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)


class RequestForExcuse(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    frequency = models.ManyToManyField(Frequency)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    is_rejected = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    date = models.DateField()
    schedule_element = models.ForeignKey(ScheduleElement, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=50)
    description = models.TextField()
    color = models.CharField(max_length=7)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    add_date = models.DateTimeField(auto_now_add=True)


class TeachersAbsence(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    from_bell = models.ForeignKey(Bell, on_delete=models.CASCADE, null=True, blank=True, related_name="from_bell")
    to_bell = models.ForeignKey(Bell, on_delete=models.CASCADE, null=True, blank=True, related_name="to_bell")


@receiver(pre_save, sender=Lesson)
def set_slug_to_lesson(sender, instance, *args, **kwargs):
    if not instance.slug:
        signs = "1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"
        code = ""
        for _ in range(30):
            code += signs[random.randint(0, len(signs)-1)]

        while sender.objects.filter(slug=code):
            code = ""
            for _ in range(30):
                code += signs[random.randint(0, len(signs) - 1)]

        instance.slug = code