from django.contrib.auth import views
from django.urls import path
from .views import *


urlpatterns = [
    path('email-create', create_email, name="email-create"),
]
