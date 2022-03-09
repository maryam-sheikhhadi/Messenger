from django.urls import path
from .views import *

urlpatterns = [
    path('create-contact', CreateContact.as_view(), name="create-contact"),
    path('all-contacts', ContactList.as_view(), name="all-contacts"),
    path('contact-detail/<int:pk>', ContactDetail.as_view(), name="contact-detail"),
    path('edite_contact/<int:pk>', UpdateContact.as_view(), name='edite_contact'),
    path('delete_contact/<int:pk>', DeleteContact.as_view(), name='delete_contact'),
]
