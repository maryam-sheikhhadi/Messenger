from django.db import models
from accounts.models import User
from .validators import validate_file_size
from django.utils.text import slugify


class Label(models.Model):
    title = models.CharField(max_length=100, null=False)
    slug = models.SlugField(max_length=100, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Signature(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.CharField(max_length=100, null=False)
    stamp = models.ImageField(upload_to='media/signature', null=True, blank=True)

    def __str__(self):
        return self.text

class Filter(models.Model):
    # title = models.CharField(max_length=50)
    label = models.ForeignKey(Label, on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    filter_by = models.CharField(null=True, max_length=100)


class Email(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_emails', blank=True)
    receivers = models.ManyToManyField(User, related_name='receivers', null=False)
    cc = models.ManyToManyField(User, related_name='receivers_cc', null=True, blank=True)
    bcc = models.ManyToManyField(User, related_name='receivers_bcc', null=True, blank=True)
    subject = models.CharField(max_length=100, null=True, blank=True)
    text = models.TextField(max_length=1000, null=True, blank=True)
    label = models.ManyToManyField(Label, related_name='labels', null=True, blank=True)
    file = models.FileField(upload_to='media/docs', validators=[validate_file_size], null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    signature = models.ForeignKey(Signature, on_delete=models.SET_NULL, null=True, blank=True)
    email_object = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    filter = models.ManyToManyField(Filter, related_name='filters', blank=True)

    @property
    def file_size(self):
        if self.file and hasattr(self.file, 'size'):
            return self.file.size



class EmailFolder(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_trash = models.BooleanField(default=False)
    is_archive = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)