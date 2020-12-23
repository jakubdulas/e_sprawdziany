from django import forms
from .models import Task

class UploadImageToTask(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['image']