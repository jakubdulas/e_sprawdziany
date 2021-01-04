from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=128)
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=10)
    key = models.CharField(max_length=11, null=True, unique=True)
    is_paid = models.BooleanField(default=False)
    free_trial_up = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    def get_teachers(self):
        return self.teacher_set.all()


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ManyToManyField(School)
    is_paid = models.BooleanField(default=False)
    free_trial_up = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} | teacher"

    @property
    def is_headmaster(self):
        if Headmaster.objects.filter(teacher=self):
            return True
        return False

    def is_in_class(self, key):
        try:
            if Class.objects.get(access_key=key).teacher == self:
                return True
            else:
                return False
        except:
            pass
        return False


class Class(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    access_key = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=100)
    max_members = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Classes'

    def __str__(self):
        return str(self.name)

    @property
    def students(self):
        return self.student_set.all()

    @property
    def members_quantity(self):
        return self.student_set.count()

    @property
    def tests(self):
        return self.blanktest_set.all()


class RequestForJoiningToSchool(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher} | {self.school}"


class Headmaster(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE, null=True)
    school = models.OneToOneField(School, on_delete=models.CASCADE, null=True, blank=True)
