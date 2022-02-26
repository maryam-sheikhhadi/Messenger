from django.urls import path
from .views import *

app_name = 'about_user'
urlpatterns = [
    path('', home, name='home'),
    path('profile/', profile, name="profile"),
]
