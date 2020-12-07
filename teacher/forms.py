from django import forms
from .models import School, Teacher, Class


school_choices = School.objects.all().values_list('name', 'name')
school_list = []
for school in school_choices:
    school_list.append(school)


class ChooseSchool(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['school']

        widgets = {
            'school': forms.Select(choices=school_list)
        }

class CreateClass(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'max_members']



