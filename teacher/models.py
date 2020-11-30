from django.db import models
from django.contrib.auth.models import User

class School(models.Model):
    name = models.CharField(max_length=128)
    street = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=6)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return str(self.name)

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, null=True, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return f"{self.user} | teacher"

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


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school_class = models.ManyToManyField('Class', blank=True)

    def __str__(self):
        return f"{self.user} | student"

    def is_in_class(self, key):
        try:
            if self in Class.objects.get(access_key=key).students:
                return True
            else:
                return False
        except:
            pass
        return False