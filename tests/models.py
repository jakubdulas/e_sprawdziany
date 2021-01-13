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
    ignore_upper_case = models.BooleanField(default=True)

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
        return self.threshold_set.all()

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


class TestGroup(models.Model):
    number = models.IntegerField()
    blank_test = models.ForeignKey(BlankTest, on_delete=models.CASCADE)

    @property
    def points(self):
        points = 0
        for task in self.task_set.all():
            points += task.points
        return points


class Test(models.Model):
    label = models.CharField(max_length=128, blank=False, null=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    blank_test = models.ForeignKey(BlankTest, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(TestGroup, on_delete=models.CASCADE, null=True)
    mark = models.CharField(max_length=1, null=True, blank=True)
    is_done = models.BooleanField(default=False)
    exits = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.label} | {self.student}"

    @property
    def tasks(self):
        return self.group.task_set.all()

    def get_logs(self):
        return self.testlog_set.all()


class Task(models.Model):
    test = models.ForeignKey(BlankTest, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(TestGroup, on_delete=models.CASCADE, null=True)
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
            return self.answer_set.filter(student=student).first()
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
    char_field = models.CharField(max_length=250, null=True, blank=True)
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


class Threshold(models.Model):
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


class TrueFalseTask(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    content = models.CharField(max_length=250)
    is_correct = models.BooleanField(default=False)
    points = models.IntegerField(default=0)


class AnswerForTF(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True)
    checked = models.BooleanField(blank=True, null=True)
    true_false = models.OneToOneField(TrueFalseTask, on_delete=models.CASCADE, null=True)
    is_correct = models.BooleanField(default=False, null=True)


class Grade(models.Model):
    mark = models.CharField(max_length=3, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.DO_NOTHING, blank=True, null=True)
    test = models.OneToOneField(Test, on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    category = models.CharField(max_length=250, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    weight = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.mark} | {self.student.user.first_name} {self.student.user.last_name}"