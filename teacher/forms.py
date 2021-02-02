from django import forms
from .models import School, Teacher, Class, SchoolTerm
from django.conf import settings


class CreateClass(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'number']


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


