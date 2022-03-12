from django import forms
from .models import Email, Signature, Label


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


class SignatureModelForm(forms.ModelForm):
    class Meta:
        model = Signature
        fields = ('text',)
#
#     def clean(self):
#         cleaned_data = super().clean()
#         text = cleaned_data.get('text')



        # if email == None and phone == None:
        #     raise forms.ValidationError('You must enter an email or phone number')
        # else:
        #     return cleaned_data