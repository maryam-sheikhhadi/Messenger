from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile


class SignupForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'phone_number', 'birth_date', 'gender', 'country', 'password1', 'password2']
