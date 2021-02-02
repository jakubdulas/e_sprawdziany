from django.db import models
from django.contrib.auth.models import User


class School(models.Model):
    name = models.CharField(max_length=128)
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=10)
    is_paid = models.BooleanField(default=False)
    free_trial_up = models.BooleanField(default=False)

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
            if Class.objects.get(access_key=key).teacher == self:
                return True
            else:
                return False
        except:
            pass
        return False


class Class(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    name = models.CharField(max_length=100)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)

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