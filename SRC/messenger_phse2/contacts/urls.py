from django.urls import path
from .views import *

urlpatterns = [
    path('create-contact', CreateContact.as_view(), name="create-contact"),
    path('all-contacts', ContactList.as_view(), name="all-contacts"),
    path('contact-detail/<int:pk>', ContactDetail.as_view(), name="contact-detail"),
]
