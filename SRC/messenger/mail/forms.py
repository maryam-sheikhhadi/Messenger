from django import forms
from .models import Email, Signature, Label


class EmailModelForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'text', 'signature', 'file']


class ReplyEmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['subject', 'text']


class LabelModelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['title', ]


class SignatureModelForm(forms.ModelForm):
    class Meta:
        model = Signature
        fields = ('text',)