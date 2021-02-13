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

    def __init__(self, school=None, *args, **kwargs):
        super(CreateClassTemplateForm, self).__init__(*args, **kwargs)
        if school:
            self.fields['subjects_1'].queryset = school.subjects.all()
            self.fields['subjects_2'].queryset = school.subjects.all()
            self.fields['subjects_3'].queryset = school.subjects.all()
            self.fields['subjects_4'].queryset = school.subjects.all()
            self.fields['subjects_5'].queryset = school.subjects.all()
            self.fields['subjects_6'].queryset = school.subjects.all()
            self.fields['subjects_7'].queryset = school.subjects.all()
            self.fields['subjects_8'].queryset = school.subjects.all()
            # self.fields['group'].req = school.subjects.all()

    subjects_1 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    subjects_2 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    subjects_3 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    subjects_4 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    subjects_5 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    subjects_6 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    subjects_7 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)
    subjects_8 = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)


class CreateSchool(forms.ModelForm):
    class Meta:
        model = School
        fields = '__all__'
        exclude = ['is_paid', 'free_trial_up', 'key']

    subjects = forms.ModelMultipleChoiceField(queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple)


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