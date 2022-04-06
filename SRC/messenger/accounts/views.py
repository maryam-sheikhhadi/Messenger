from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.views.generic import View
from .forms import SignupForm
from .models import User
from .tokens import account_activation_token
import logging
from django.http import HttpResponse

logger = logging.getLogger('accounts')


# view for register user
class Register(View):
    form_class = SignupForm
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Messenger Account'
            message = render_to_string('registration/activate_account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            messages.success(request, ('Please Confirm your email to complete registration.'))

            return HttpResponse('An activation link was sent to your email. <a href="/login/">login</a>')
        else:
            logger.error('register form not valid')
            return render(request, self.template_name, {'form': form})


# view for activate user account
class ActivateAccount(View):

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.username += '@gmail.com'
            user.save()
            messages.success(request, ('Your account have been confirmed.'))
            return render(request, 'registration/activate_successfully.html', {})
        else:
            logger.error(f'expire activate link for {user}')
            return render(request, 'registration/expire_activate_link.html', {})


class Login(LoginView):
    def get_success_url(self):
        user = self.request.user

        if user.is_active:
            return reverse_lazy("accounts:home")
        else:
            logger.warning(f'{user} try to login but he is not active')
            return reverse_lazy("accounts:profile")


def profile(request):
    return render(request, "registration/profile.html", {})


def home(request):
    return redirect('/')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/login/')
    elif request.method == 'GET':
        return render(request, "registration/logout.html")
