from django import forms
from .models import *
from django.conf import settings


class CreateClass(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['number', 'teacher', 'students']


class CreateClassTemplateForm(forms.ModelForm):
    class Meta:
        model = ClassTemplate
        fields = '__all__'
        exclude = ('school', )


class CreateSchool(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        exclude = ['is_paid', 'free_trial_up', 'key']


class SchoolTermForm(forms.ModelForm):
    start = forms.DateField(required=True, input_formats=settings.DATE_INPUT_FORMATS)
    end = forms.DateField(required=True, input_formats=settings.DATE_INPUT_FORMATS)

    start.widget.attrs.update({'placeholder': 'DD-MM-YYYY'})
    end.widget.attrs.update({'placeholder': 'DD-MM-YYYY'})

    class Meta:
        model = SchoolTerm
        fields = '__all__'
        exclude = ['school', 'number', 'school_year']


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'


class ScheduleElementForm(forms.ModelForm):
    class Meta:
        model = ScheduleElement
        fields = ['group']

    def __init__(self, teacher=None, *args, **kwargs):
        super(ScheduleElementForm, self).__init__(*args, **kwargs)
        if teacher:
            self.fields['group'].queryset = Group.objects.filter(teacher=teacher)
            self.fields['group'].req = Group.objects.filter(teacher=teacher)