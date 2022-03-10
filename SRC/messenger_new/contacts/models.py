from django.db import models
from accounts.models import User


class Contact(models.Model):
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    email = models.EmailField(null=False)
    other_emails = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, related_name='contacts_of_user', on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        unique_together = [('user', 'email'), ]

    def __str__(self):
        return self.email
