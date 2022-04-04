from django.test import TestCase
from .models import Contact


# Create your tests here.
class ContactTest(TestCase):

    def setUp(self):
        Contact.objects.create(first_name="Mim", last_name="Shin",
                                      email='min_shin@gmail.com')

    def test_question_text(self):
        c = Contact.objects.get(first_name="Mim")
        self.assertEqual("@gmail.com", c.email[-10:])
