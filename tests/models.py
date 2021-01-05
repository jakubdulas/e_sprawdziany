from django.db import models
from teacher.models import Teacher, Class
from student.models import Student


# Create your models here.

class BlankTest(models.Model):
    label = models.CharField(max_length=128, blank=False, null=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    students = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=False)
    countdown = models.DurationField(null=True)
    are_exists_allowed = models.BooleanField(default=True)
    allowed_exits = models.IntegerField(default=0)

    def __str__(self):
        return str(self.label)

    @property
    def tasks(self):
        return self.task_set.all()

    @property
    def students_tests(self):
        return self.test_set.all()

    @property
    def tests(self):
        return self.test_set.all()

    @property
    def threshold(self):
        return self.mark_set.all()

    @property
    def autocheck(self):
        foo = False
        if self.threshold:
            for task in self.tasks:
                if 'otwarte' != task.type.label and 'tablica' != task.type.label:
                    foo = True
                else:
                    return False
        return foo

    @property
    def total_points(self):
        total = 0
        for task in self.tasks:
            total += task.points
        return total


class Test(models.Model):
    label = models.CharField(max_length=128, blank=False, null=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    blank_test = models.ForeignKey(BlankTest, on_delete=models.CASCADE, null=True)
    mark = models.CharField(max_length=1, null=True, blank=True)
    is_done = models.BooleanField(default=False)
    exits = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.label} | {self.student}"

    @property
    def tasks(self):
        return self.task_set.all()

    @property
    def total_points(self):
        total = 0
        for task in self.tasks:
            total += task.answer_set.first().earned_points
        return total

    def get_logs(self):
        return self.testlog_set.all()


class Task(models.Model):
    test = models.ForeignKey(BlankTest, on_delete=models.CASCADE, null=True)
    students_test = models.ManyToManyField(Test)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    type = models.ForeignKey("TypeOfTask", on_delete=models.CASCADE)
    correct_answer = models.CharField(max_length=100, null=True, blank=True)
    points = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return f"{self.content[:15]} | {str(self.test)}"

    @property
    def answer_options(self):
        try:
            return self.answeroption_set.all()
        except:
            pass

    def students_answer(self, student):
        try:
            return self.answer_set.get(student=student)
        except:
            return ""

    @property
    def correct_answer_option(self):
        return self.answer_options.filter(is_correct=True).first()


class TypeOfTask(models.Model):
    label = models.CharField(max_length=50)

    def __str__(self):
        return self.label


class AnswerOption(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    label = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    img = models.ImageField(upload_to='answer_options_imgs/', null=True, blank=True)

    def __str__(self):
        return f"{self.label} | {str(self.task)}"


class Answer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    textarea = models.TextField(null=True, blank=True)
    char_field = models.CharField(max_length=128, null=True, blank=True)
    board = models.ImageField(upload_to='boards/', null=True, blank=True)
    answer_option = models.OneToOneField(AnswerOption, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False, null=True, blank=True)
    earned_points = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        if self.textarea:
            return self.textarea[0:15]
        elif self.char_field:
            return self.char_field
        else:
            return f"{self.student.user.first_name}'s answer"

    @property
    def test(self):
        return self.task.test


class Mark(models.Model):
    mark = models.CharField(max_length=2)
    from_percent = models.IntegerField()
    to_percent = models.IntegerField()
    blank_test = models.ForeignKey(BlankTest, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.mark}"


class TestLog(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    context = models.TextField()

    def __str__(self):
        return f"{self.context}"

