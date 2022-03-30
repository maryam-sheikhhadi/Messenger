from django.urls import path
from .views import *

urlpatterns = [
    path('create-contact', CreateContact.as_view(), name="create-contact"),
    path('all-contacts', ContactList.as_view(), name="all-contacts"),
    path('contact-detail/<int:pk>', ContactDetail.as_view(), name="contact-detail"),
    path('edite_contact/<int:pk>', UpdateContact.as_view(), name='edite_contact'),
    path('delete_contact/<int:pk>', DeleteContact.as_view(), name='delete_contact'),
    path('contact-list-csv', export_csv_contacts_list, name='contact-list-csv'),
    path('search_fields_contact', SearchByFieldContact.as_view(), name='search_fields_contact'),
    path('api/contacts/', ContactsList.as_view(), name='contacts-list'),
    path('search_contacts/', search_contacts, name="search_contacts"),
]
