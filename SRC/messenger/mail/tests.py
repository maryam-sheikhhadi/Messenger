from django.test import TestCase
from .models import *
from accounts.models import *

import unittest
from django.test import Client
from django.urls import reverse


class EmailTest(TestCase):

    def setUp(self):
        u = User.objects.create(username="eli@gmail.com", is_active=True)
        u.set_password('ab654321')
        u.save()
        e = Email.objects.create(sender=u, subject='tft')
        e2 = Email.objects.create(sender=u, pk=0)
        e3 = Email.objects.create(sender=u, subject='e3')
        e4 = Email.objects.create(sender=u, subject='e4')
        folder_e4 = EmailFolder.objects.create(user=u, email=e4, is_archive=True)
        e_trash = Email.objects.create(sender=u, subject='trash')
        folder_e_trash = EmailFolder.objects.create(user=u, email=e_trash, is_trash=True)

        e.receivers.add(u.id)

    def test_receiver_to(self):
        e = Email.objects.get(subject='tft')
        self.assertTrue(bool(e.receivers))

    def test_detail_email(self):
        e2 = Email.objects.get(pk=0)
        response = self.client.get(f'/mail/mail-detail/{e2.pk}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_email(self):
        e3 = Email.objects.get(subject='e3')
        response = self.client.get(f'/mail/delete-email/{e3.pk}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_check_archive(self):
        e4 = Email.objects.get(subject='e4')
        folder_e4 = EmailFolder.objects.get(email=e4)

        response = self.client.get('/mail/archive', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(folder_e4.is_archive, True)

    def test_check_trash(self):
        e_trash = Email.objects.get(subject='trash')
        folder_e_trash = EmailFolder.objects.get(email=e_trash)

        response = self.client.get('/mail/trash', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(folder_e_trash.is_trash, True)


class EmailListTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        user_1 = User.objects.create(username="mah@gmail.com", password='ab123456', is_active=True)
        user_2 = User.objects.create(username="sun@gmail.com", password='ab123456', is_active=True)
        email_1 = Email.objects.create(sender=user_1, subject='green')
        email_2 = Email.objects.create(sender=user_1, subject='orange')
        email_1.receivers.add(user_2.id)
        email_2.receivers.add(user_2.id)

    def test_details(self):
        def test_email_list(self):
            response = self.client.get(reverse('mail:all-mails'))
            self.assertIn('environment', response.context)


class Labeltest(TestCase):

    def setUp(self):
        u = User.objects.create(username="eli2@gmail.com", password='ab123456', is_active=True)
        label_1 = Label.objects.create(owner=u, title='sea', slug='sea')
        label_5 = Label.objects.create(owner=u, title='blue5', slug='blue5')
        label_6 = Label.objects.create(owner=u, title='Mim', slug='Mim')

    def test_detail_label(self):
        label_1 = Label.objects.get(slug='sea')
        response = self.client.get(f'/mail/labels/{label_1.slug}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_label(self):
        label_5 = Label.objects.get(slug='blue5')
        response = self.client.get(f'/mail/delete-label/{label_5.slug}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_search_label(self):
        text = 'Mim'
        l = Label.objects.get(title='Mim').title
        result = list(Label.objects.filter(title__startswith=text).values_list('title', flat=True))[0]
        self.assertEqual(l, result)


class LabelListTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        u = User.objects.create(username="eli3@gmail.com", password='ab123456', is_active=True)
        label_1 = Label.objects.create(owner=u, title='sea2', slug='sea2')
        label_2 = Label.objects.create(owner=u, title='blue2', slug='blue2')

    def test_details(self):
        def test_label_list(self):
            response = self.client.get(reverse('mail:labels'))
            self.assertIn('environment', response.context)


class SignatureTest(TestCase):

    def setUp(self):
        u = User.objects.create(username="eli2@gmail.com", password='ab123456', is_active=True)
        s = Signature.objects.create(user=u, text='sea')
        s = Signature.objects.create(user=u, text='blue')

    def test_detail_signature(self):
        s = Signature.objects.get(text='sea')
        response = self.client.get(f'/mail/signature-detail/{s.pk}', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_signature(self):
        sign = Signature.objects.get(text='blue')
        response = self.client.get(f'/mail/delete-signature/{sign.pk}', follow=True)
        self.assertEqual(response.status_code, 200)


class SignatureListTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        u = User.objects.create(username="eli4@gmail.com", password='ab123456', is_active=True)
        s = Signature.objects.create(user=u, text='sea4')
        s = Signature.objects.create(user=u, text='blue4')

    def test_details(self):
        def test_contact_list(self):
            response = self.client.get(reverse('mail:signatures'))
            self.assertIn('environment', response.context)
