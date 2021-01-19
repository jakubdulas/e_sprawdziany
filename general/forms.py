from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']


class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']