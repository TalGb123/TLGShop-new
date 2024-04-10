from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    id = forms.CharField(required=True, max_length=9)
    first_name = forms.CharField(required=True, max_length=20)
    last_name = forms.CharField(required=True, max_length=20)

    class Meta:
        model = User
        fields = [
            "username",
            "id",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]
