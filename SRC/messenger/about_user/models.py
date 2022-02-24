from django.db import models
from django.contrib.auth.models import AbstractUser
from about_user.manager import UserManager


class UserProfile(AbstractUser):
    email = models.EmailField(null=True, blank=True, verbose_name='Email Recovery')
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    status_choices_gender = [
        ('F', 'female'),
        ('M', 'male'),
        ('C', 'Custom'),
        ('R', 'Rather not say')
    ]

    gender = models.CharField(max_length=1, choices=status_choices_gender, null=True, blank=True)
    status_choices_country = [
        ('IR', 'Iran'),
        ('FR', 'France'),
        ('UK', 'United Kingdom'),
        ('US', 'United States'),
    ]

    country = models.CharField(max_length=2, choices=status_choices_country, null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True, null=True)

    objects = UserManager()
