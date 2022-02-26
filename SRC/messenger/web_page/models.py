from django.db import models
from about_user.models import UserProfile
from .validators import validate_file_size


class Label(models.Model):
    title = models.CharField(max_length=100, null=False)
    slug = models.SlugField(max_length=100, unique=True, null=True)


class Contact(models.Model):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    email = models.EmailField(null=False)
    profile_photo = models.ImageField(upload_to='media/profile_contact', null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    contact_user = models.ManyToManyField(UserProfile, related_name='contact_user')
    slug = models.SlugField(max_length=100, unique=True, null=True)


class Signature(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.SET_DEFAULT, default='deleted')
    text = models.CharField(max_length=100, null=False)
    photo = models.ImageField(upload_to='media/signature', null=True, blank=True)


class Email(models.Model):
    subject = models.CharField(max_length=100, null=True)
    text = models.TextField(max_length=1000, null=True)
    file = models.FileField(upload_to='media/docs', validators=[validate_file_size], null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    receiver = models.ManyToManyField(Contact, related_name='receivers')
    label = models.ManyToManyField(Label, related_name='labels', null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    is_inbox = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    signature = models.ForeignKey(Signature, on_delete=models.SET_NULL, null=True, blank=True)
    sender = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, related_name='sender', blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True)
