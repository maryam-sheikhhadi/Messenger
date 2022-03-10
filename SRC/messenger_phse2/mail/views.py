from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView
from accounts.models import User
from .forms import EmailModelForm, ReplyEmailForm, LabelModelForm
from .models import Email, Label
from django.db.models import Q

"""
    email views: create, forward, reply, delete, update, list and detail
"""


class CreateEmail(LoginRequiredMixin, View):
    def get(self, request):
        form = EmailModelForm()
        contacts_list = User.objects.get(id=request.user.id).contacts_of_user.all().values_list('email', flat=True)
        contacts_list = list(contacts_list)
        label_list = Label.objects.all().filter(owner=request.user.id).values_list('title', flat=True).distinct()
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
        cc_list = cc.split(',')
        bcc_list = bcc.split(',')
        to_list = receivers.split(',')
        labels_list = label.split(',')


        users = User.objects.all().values_list('username', flat=True)
        users_list = [i for i in users]
        labels_of_user = Label.objects.all().filter(owner=request.user)
        labels_of_user_list = [i for i in labels_of_user]

        to_list = [i for i in to_list if i in users_list]
        cc_list = [i for i in cc_list if i in users_list]
        bcc_list = [i for i in bcc_list if i in users_list]
        labels_list = [i for i in labels_list if i in labels_of_user_list]

        list_id_to = [User.objects.get(username=i).id for i in to_list]
        list_id_cc = [User.objects.get(username=i).id for i in cc_list]
        list_id_bcc = [User.objects.get(username=i).id for i in bcc_list]
        list_id_label = [Label.objects.get(title=i).id for i in labels_list]

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
            if 'draft' in request.POST:
                email_obj.label.add(*list_id_label)
                email_obj.is_draft=True
                email_obj.save()
                return redirect('/mail/draft')
            else:
                email_obj.label.add(*list_id_label)
                email_obj.cc.add(*list_id_cc)
                email_obj.receivers.add(*list_id_to)
                email_obj.bcc.add(*list_id_bcc)

                return HttpResponse(f"'saved',{form.errors}")
            return HttpResponse(f"'not saved', {form.errors}")


class EmailList(LoginRequiredMixin, View):

    def get(self, request):
        emails = Email.objects.all().filter(
            Q(sender=request.user.id) | Q(receivers=request.user.id)
            | Q(cc=request.user.id) | Q(bcc=request.user.id)).distinct()

        return render(request, 'mail/email_list.html', {'emails': emails})


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
        cc_list = cc.split(',')
        bcc_list = bcc.split(',')
        to_list = receivers.split(',')

        users = User.objects.all().values_list('username', flat=True)
        users_list = [i for i in users]

        to_list = [i for i in to_list if i in users_list]
        cc_list = [i for i in cc_list if i in users_list]
        bcc_list = [i for i in bcc_list if i in users_list]

        list_id_to = [User.objects.get(username=i).id for i in to_list]
        list_id_cc = [User.objects.get(username=i).id for i in cc_list]
        list_id_bcc = [User.objects.get(username=i).id for i in bcc_list]

        email_obj = Email(sender=forwarder, subject=email.subject,
                          text=email.text)
        email_obj.email_object = email
        email_obj.save()

        email_obj.cc.add(*list_id_cc)
        email_obj.receivers.add(*list_id_to)
        email_obj.bcc.add(*list_id_bcc)

        return redirect(f'/mail/mail-detail/{pk}')



class SendDraft(LoginRequiredMixin, View):
    def get(self, request, pk):
        contacts_list = User.objects.get(id=request.user.id).contacts_of_user.all().values_list('email', flat=True)
        return render(request, 'mail/send_draft.html', {'contacts_list': list(contacts_list)})

    def post(self, request, pk):
        forwarder = request.user
        email = Email.objects.get(id=pk)
        receivers = request.POST['to']
        cc = request.POST['cc']
        bcc = request.POST['bcc']
        cc_list = cc.split(',')
        bcc_list = bcc.split(',')
        to_list = receivers.split(',')

        users = User.objects.all().values_list('username', flat=True)
        users_list = [i for i in users]

        to_list = [i for i in to_list if i in users_list]
        cc_list = [i for i in cc_list if i in users_list]
        bcc_list = [i for i in bcc_list if i in users_list]

        list_id_to = [User.objects.get(username=i).id for i in to_list]
        list_id_cc = [User.objects.get(username=i).id for i in cc_list]
        list_id_bcc = [User.objects.get(username=i).id for i in bcc_list]

        email_obj = Email(sender=forwarder, subject=email.subject,
                          text=email.text)
        email_obj.email_object = email
        email_obj.save()

        email_obj.cc.add(*list_id_cc)
        email_obj.receivers.add(*list_id_to)
        email_obj.bcc.add(*list_id_bcc)

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

class AddLabel(View):

    def get(self, request,pk):
        query = Label.objects.filter(owner=request.user).values_list('title', flat=True)
        return render(request,'mail/add_label_to_email.html', {'query':list(query)})

    def post(self, request, pk):
        print(request.POST)
        label = request.POST.getlist('selected_label')
        email = Email.objects.get(id=pk)
        label_id = [Label.objects.get(title=i) for i in label]
        email.label.add(*label_id)
        return HttpResponse('okay!')



class CreateLabel(LoginRequiredMixin, View):

    def get(self, request):
        form = LabelModelForm()
        return render(request, 'mail/create_label.html', {"form": form})

    def post(self, request):
        form = LabelModelForm(request.POST)
        if form.is_valid():
            label_obj = Label(title=form.cleaned_data['title'],
                              owner=request.user)
            label_obj.save()
            return HttpResponse('this label created')


class LabelList(LoginRequiredMixin, View):
    def get(self, request):
        labels = Label.objects.all().filter(owner=request.user)
        return render(request, 'mail/label_list.html', {'labels': labels})


class LabelDetail(LoginRequiredMixin, DetailView):
    model = Label


class DeleteLabel(LoginRequiredMixin, DeleteView):
    model = Label
    success_url = '/'


class SearchByLable(LoginRequiredMixin, View):

    def get(self, request):
        label_list = Label.objects.all().filter(owner=request.user.id).values_list('title', flat=True)
        return render(request, 'mail/search_box.html', {'label_list': list(label_list)})

    def post(self, request):
        search_label = request.POST['search_label']

        result = Email.objects.all().filter(
            Q(label__title__startswith=search_label) & Q(sender=request.user.id)
            | Q(receivers=request.user.id) | Q(cc=request.user.id) |
            Q(bcc=request.user.id)).distinct()

        return render(request, 'mail/email_with_label_input.html', {'result': result})


"""
    categories: sent, inbox, draft, trash, archive
"""


class SentBox(LoginRequiredMixin, View):
    def get(self, request):
        sent_box = Email.objects.filter(sender=request.user.id).distinct()
        return render(request, 'mail/sent_box.html', {'sent_box': sent_box})


class Inbox(LoginRequiredMixin, View):
    def get(self, request):
        emails_to = Email.objects.filter(receivers=request.user.id).distinct()
        emails_cc = Email.objects.filter(cc=request.user.id).distinct()
        emails_bcc = Email.objects.filter(bcc=request.user.id).distinct()
        return render(request, 'mail/inbox.html', {'emails_to': emails_to,
                                                       'emails_cc': emails_cc,
                                                       'emails_bcc': emails_bcc})


class Draft(LoginRequiredMixin, View):

    def get(self, request):
        draft = Email.objects.filter((Q(is_draft=True) & Q(sender=request.user.id)) |
                                              (Q(is_draft=True) & Q(bcc=request.user.id)) |
                                              (Q(is_draft=True) & Q(cc=request.user.id)) |
                                              (Q(is_draft=True) & Q(receivers=request.user.id)))
        draft = draft.distinct()

        return render(request, 'mail/draft.html', {'draft': draft})


class Archive(LoginRequiredMixin, View):

    def get(self, request):
        archive = Email.objects.filter((Q(is_archive=True) & Q(sender=request.user.id)) |
                                               (Q(is_archive=True) & Q(bcc=request.user.id)) |
                                               (Q(is_archive=True) & Q(cc=request.user.id)) |
                                               (Q(is_archive=True) & Q(receivers=request.user.id)))
        archive = archive.distinct()

        return render(request, 'mail/archive.html', {'archive': archive})


class Trash(LoginRequiredMixin, View):

    def get(self, request):
        trash = Email.objects.filter((Q(is_trash=True) & Q(sender=request.user.id)) |
                                              (Q(is_trash=True) & Q(receivers=request.user.id)) |
                                              (Q(is_trash=True) & Q(cc=request.user.id)) |
                                              (Q(is_trash=True) & Q(bcc=request.user.id)))
        trash = trash.distinct()

        return render(request, 'mail/trash.html', {'trash': trash})



"""
    آخیش🥱
"""

