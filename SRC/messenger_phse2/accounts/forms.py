from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'birth_date', 'gender', 'country', 'password1', 'password2']
