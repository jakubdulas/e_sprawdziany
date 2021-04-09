from django import forms
from .models import Task
from teacher.models import Grade, FinalGrade


class UploadImageToTask(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['image']


class GiveGradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['mark', 'weight', 'category', 'description', 'include_in_mean']

    def __init__(self, school=None, *args, **kwargs):
        super(GiveGradeForm, self).__init__(*args, **kwargs)
        if school:
            self.fields['mark'].queryset = school.grades.all()
            self.fields['mark'].req = school.grades.all()

class FinalGradeForm(forms.ModelForm):
    class Meta:
        model = FinalGrade
        fields = ['mark']