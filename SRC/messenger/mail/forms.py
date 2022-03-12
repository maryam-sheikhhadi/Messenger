from django import forms
from .models import Email
from .models import Label


class EmailModelForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'text', 'is_archive', 'is_draft', 'is_trash', 'signature', 'file']


class ReplyEmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'text']


class LabelModelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['title', ]