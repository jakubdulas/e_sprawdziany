from django import forms
from .models import Test

class CreateTestForm(forms.Form):
    class Meta:
        model = Test
        fields = ['label', 'students']

