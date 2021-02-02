from django.db import models
from django.contrib.auth.models import User
from teacher.models import Class,  School


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    school_class = models.ManyToManyField(Class, blank=True)

    def __str__(self):
        return f"{self.user.username} | student"

    def is_in_class(self, key):
        try:
            if self in Class.objects.get(access_key=key).students:
                return True
            else:
                return False
        except:
            pass
        return False
