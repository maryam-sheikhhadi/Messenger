from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from about_user.models import UserProfile
from .forms import EmailModelForm, LabelModelForm, ContactModelForm
from django.shortcuts import render
from .models import Email
from messenger import settings


@login_required(login_url=settings.LOGIN_URL)
def create_email(request):
    if request.method == "GET":
        form = EmailModelForm()
        return render(request, 'web_page/create_email.html', {"form": form})
    elif request.method == "POST":
        form = EmailModelForm(request.POST, request.FILES)
        if form.is_valid():
            sender = UserProfile.objects.get(id=request.user.id)
            email = Email(subject=form.cleaned_data['subject'],
                          text=form.cleaned_data['text'],
                          receiver=form.cleaned_data['receiver'],
                          sender=sender, is_sent=True, is_inbox=True)
            email.save()
            return HttpResponse('sent')
        else:
            return HttpResponse(f"{form.errors}")
