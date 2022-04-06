from django.test import TestCase
from .forms import SignupForm
from .models import User
from django.urls import reverse


class AccountTest(TestCase):

    def setUp(self):
        user_1 = User.objects.create(username='sara', password='ab654321')

    def test_signup_form(self):
        form = SignupForm(data={'username': 'u', 'email': 'u@gmail.com', 'password1': 'ab654321',
                                'password2': 'ab654321'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data['password1'], form.data['password2'])

    def test_login(self):
        response = self.client.get(reverse('accounts:home'), follow=True)
        self.assertEqual(response.status_code, 200)

