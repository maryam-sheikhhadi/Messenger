from django.test import TestCase
from .models import Contact
from .forms import ContactModelForm

import unittest
from django.test import Client
from django.urls import reverse


class ContactTest(TestCase):

    def setUp(self):
        c = Contact.objects.create(first_name="Mim", last_name="Shin",
                                   email='min_shin@gmail.com')
        c2 = Contact.objects.create(first_name="Mim2", last_name="Shin2",
                                    email='min_shin2@gmail.com')

    def test_valid_email_contact(self):
        c = Contact.objects.get(first_name="Mim")
        self.assertEqual("@gmail.com", c.email[-10:])

    def test_uniq_email_contact(self):
        c = Contact.objects.get(first_name="Mim").email
        c2 = Contact.objects.get(first_name="Mim2").email
        self.assertTrue(bool(c != c2))

    def test_create_contact(self):
        form = ContactModelForm(
            data={'first_name': 'mahdiye', 'last_name': 'kaffash', 'email': 'kaffashmhdiye@gmail.com'})
        self.assertTrue(form.is_valid())

    def test_search_contact(self):
        text = 'Mim2'
        c = Contact.objects.get(first_name='Mim2').first_name
        result = list(Contact.objects.filter(first_name__startswith=text).values_list('first_name', flat=True))[0]
        self.assertEqual(c, result)

    def test_contact_list(self):
        response = self.client.get(f'/contacts/all-contacts', follow=True)
        self.assertEqual(response.status_code, 200)


class ContactListTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        person1 = Contact.objects.create(first_name="Mim3", last_name="Shin3",
                                         email='min_shin3@gmail.com')
        person2 = Contact.objects.create(first_name="Mim4", last_name="Shin4",
                                         email='min_shin4@gmail.com')

    def test_details(self):
        def test_contact_list(self):
            response = self.client.get(reverse('contacts:all-contacts'))
            self.assertIn('environment', response.context)
