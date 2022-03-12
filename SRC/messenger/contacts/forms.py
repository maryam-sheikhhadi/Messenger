from .models import Contact
from django import forms


class ContactModelForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'other_emails', 'phone_number', 'birth_date']