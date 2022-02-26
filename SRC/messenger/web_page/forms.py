from django import forms
from .models import Email, Label, Contact


class EmailModelForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'text', 'receiver']


class LabelModelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['title', ]


class ContactModelForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'profile_photo', 'phone_number', 'birth_date']
