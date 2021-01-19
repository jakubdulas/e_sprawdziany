from django import forms
from .models import School, Teacher, Class, RequestForJoiningToSchool


school_choices = School.objects.all().values_list('name', 'name')
school_list = []
for school in school_choices:
    school_list.append(school)


class SendRequestForJoiningToSchool(forms.ModelForm):
    class Meta:
        model = RequestForJoiningToSchool
        fields = ['school']

        widgets = {
            'school': forms.Select(choices=school_list)
        }


class CreateClass(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'max_members']


class CreateSchool(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        exclude = ['is_paid', 'free_trial_up', 'key']

