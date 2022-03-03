from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
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

            return render(request, 'registration/activate_messege_sent.html', {})

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
            return render(request, 'registration/expire_activate_link.html', {})


class Login(LoginView):
    def get_success_url(self):
        user = self.request.user

        if user.is_active:
            return reverse_lazy("accounts:home")
        else:
            return reverse_lazy("accounts:profile")


def profile(request):
    return render(request, "registration/profile.html", {})


def home(request):
    return render(request, "registration/profile.html", {})