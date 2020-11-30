from django.db import models
from teacher.models import Teacher, Class, Student


# Create your models here.

class Test(models.Model):
    label = models.CharField(max_length=128, blank=False, null=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.label)

    @property
    def tasks(self):
        return self.task_set.all()


class Task(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    type = models.OneToOneField("TypeOfTask", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.content[:15]} | {str(self.test)}"

    @property
    def answer_options(self):
        try:
            return self.answeroption_set.all()
        except:
            pass


class AnswerOption(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    label = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.label} | {str(self.task)}"


class TypeOfTask(models.Model):
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label
