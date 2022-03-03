from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from accounts.models import User
from .forms import EmailModelForm, ReplyEmailForm, LabelModelForm
from .models import Email, Label

"""
    email views: create, forward, reply, delete, update, list and detail
"""


class CreateEmail(LoginRequiredMixin, View):
    def get(self, request):
        form = EmailModelForm()
        contacts_list = User.objects.get(id=request.user.id).contacts_of_user.all().values_list('email', flat=True)
        contacts_list = list(contacts_list)
        label_list = Label.objects.all().values_list('title', flat=True)
        label_list = list(label_list)
        return render(request, 'mail/create_email.html', {"form": form,
                                                          'contacts_list': contacts_list,
                                                          'label_list': label_list})

    def post(self, request):
        form = EmailModelForm(request.POST, request.FILES)
        receivers = request.POST['to']
        cc = request.POST['cc']
        bcc = request.POST['bcc']
        label = request.POST['label']

        if form.is_valid():
            email_obj = Email(subject=form.cleaned_data['subject'],
                              text=form.cleaned_data['text'],
                              is_draft=form.cleaned_data['is_draft'],
                              is_trash=form.cleaned_data['is_trash'],
                              is_archive=form.cleaned_data['is_archive'],
                              signature=form.cleaned_data['signature'],
                              file=form.cleaned_data['file'],
                              sender=User.objects.get(id=request.user.id)
                              )
            email_obj.save()
            to_pk = User.objects.get(username=receivers).id
            cc_pk = User.objects.get(username=cc).id
            bcc_pk = User.objects.get(username=bcc).id
            label_pk = Label.objects.get(title=label).id
            email_obj.receivers.add(to_pk)
            email_obj.cc.add(cc_pk)
            email_obj.bcc.add(bcc_pk)
            email_obj.label.add(label_pk)
            return HttpResponse(f"'saved',{form.errors}")
        return HttpResponse(f"'not saved', {form.errors}")


class EmailList(LoginRequiredMixin, ListView):
    model = Email


class EmailDetail(LoginRequiredMixin, DetailView):
    model = Email

    def post(self, request, pk):
        email = Email.objects.get(id=pk)
        email.is_trash = True
        email.save()
        return redirect(f'/mail/all-mails')


class ReplyEmail(LoginRequiredMixin, View):
    def get(self, request, pk):
        form = ReplyEmailForm()
        replied_email = Email.objects.get(id=pk)
        return render(request, 'mail/reply_email.html', {'form': form, 'replied_email': replied_email})

    def post(self, request, pk):
        form = ReplyEmailForm(request.POST)
        if form.is_valid():
            replier = request.user
            email = Email.objects.get(id=pk)

            email_obj = Email(sender=replier, subject=form.cleaned_data['subject'],
                              text=form.cleaned_data['text'])
            email_obj.email_object = email
            email_obj.save()
            receiver = email.sender.id
            email_obj.receivers.add(receiver)
            return redirect(f'/mail/mail-detail/{pk}')
        return HttpResponse('ok nashod')


class ForwardEmail(LoginRequiredMixin, View):
    def get(self, request, pk):
        contacts_list = User.objects.get(id=request.user.id).contacts_of_user.all().values_list('email', flat=True)
        return render(request, 'mail/forward_email.html', {'contacts_list': list(contacts_list)})

    def post(self, request, pk):
        forwarder = request.user
        email = Email.objects.get(id=pk)
        receivers = request.POST['to']
        cc = request.POST['cc']
        bcc = request.POST['bcc']
        email_obj = Email(sender=forwarder, subject=email.subject,
                          text=email.text)
        email_obj.email_object = email
        email_obj.save()
        to_pk = User.objects.get(username=receivers).id
        cc_pk = User.objects.get(username=cc).id
        bcc_pk = User.objects.get(username=bcc).id
        email_obj.receivers.add(to_pk)
        email_obj.cc.add(cc_pk)
        email_obj.bcc.add(bcc_pk)
        return redirect(f'/mail/mail-detail/{pk}')


class UpdateEmail(LoginRequiredMixin, UpdateView):
    model = Email
    template_name = 'mail/edite_email.html'
    fields = ['is_trash', 'is_archive', 'is_draft']
    success_url = '/'


class DeleteEmail(LoginRequiredMixin, DeleteView):
    model = Email
    success_url = '/'


"""
    label views: create, delete, search, list and detail
"""


class CreateLabel(LoginRequiredMixin, View):

    def get(self, request):
        form = LabelModelForm()
        return render(request, 'mail/create_label.html', {"form": form})

    def post(self, request):
        form = LabelModelForm(request.POST)
        if form.is_valid():
            label_obj = Label(title=form.cleaned_data['title'], )
            label_obj.save()
            return HttpResponse('this label created')


class LabelList(LoginRequiredMixin, ListView):
    model = Label


class LabelDetail(LoginRequiredMixin, DetailView):
    model = Label


class DeleteLabel(LoginRequiredMixin, DeleteView):
    model = Label
    success_url = '/'


class SearchByLable(LoginRequiredMixin, View):

    def get(self, request):
        label_list = Label.objects.all().values_list('title', flat=True)
        return render(request, 'mail/search_box.html', {'label_list': list(label_list)})

    def post(self, request):
        search_label = request.POST['search_label']
        label_list = Label.objects.all().values_list('title', flat=True)

        result = Email.objects.all().filter(label__title__startswith=search_label).values_list('subject', flat=True)
        return render(request, 'mail/email_with_label_input.html', {'result': result})


"""
    categories: sent, inbox, draft, trash, archive
"""


class SentBox(LoginRequiredMixin, View):
    def get(self, request):
        sent_box = Email.objects.filter(sender=request.user.id)
        return render(request, 'mail/sent_box.html', {'sent_box': sent_box})


class Inbox(LoginRequiredMixin, View):
    def get(self, request):
        inbox = Email.objects.filter(receivers=request.user.id)
        inbox_bcc = Email.objects.filter(bcc=request.user.id)
        inbox_cc = Email.objects.filter(cc=request.user.id)
        return render(request, 'mail/inbox.html', {'inbox': inbox,
                                                   'inbox_bcc': inbox_bcc,
                                                   'inbox_cc': inbox_cc})


class Draft(LoginRequiredMixin, View):
    def get(self, request):
        draft = Email.objects.filter(is_draft=True)
        return render(request, 'mail/draft.html', {'draft': draft})


class Archive(LoginRequiredMixin, View):
    def get(self, request):
        draft = Email.objects.filter(is_archive=True)
        return render(request, 'mail/archive.html', {'draft': draft})


class Trash(LoginRequiredMixin, View):
    def get(self, request):
        trash = Email.objects.filter(is_trash=True)
        return render(request, 'mail/trash.html', {'trash': trash})


"""
    آخیش🥱
"""