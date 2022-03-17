import itertools
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import DetailView, DeleteView
from accounts.models import User
from .forms import EmailModelForm, ReplyEmailForm, LabelModelForm, SignatureModelForm
from .models import Email, Label, Signature, EmailFolder, Filter
from django.db.models import Q
from django.http import JsonResponse
import json
from django.contrib import messages
from django.utils import timezone

"""
    email views: create, forward, reply, delete, update, list and detail
"""

class CreateEmail(LoginRequiredMixin, View):
    def get(self, request):
        form = EmailModelForm()
        contacts_list = User.objects.get(id=request.user.id).contacts_of_user.all().values_list('email', flat=True)
        contacts_list = list(contacts_list)
        signature_list = Signature.objects.filter(user=request.user).values_list('text', flat=True)
        return render(request, 'mail/create_email.html', {"form": form,
                                                          'contacts_list': contacts_list,
                                                          'signature_list': list(signature_list)
                                                          })

    def post(self, request):
        form = EmailModelForm(request.POST, request.FILES)
        receivers = request.POST['to']
        cc = request.POST['cc']
        bcc = request.POST['bcc']
        if request.POST.get('selected_singature') != 'None':
            signature = Signature.objects.get(text=request.POST['selected_singature'], user=request.user)
        else:
            signature = None

        cc_list = cc.split(',')
        bcc_list = bcc.split(',')
        to_list = receivers.split(',')
        all_receivers = cc_list + bcc_list + to_list
        all_receivers =  [i for i in all_receivers if i]

        users = User.objects.all().values_list('username', flat=True)
        users_list = [i for i in users]

        for i in all_receivers:
            if i not in users_list:
                messages.add_message(request, messages.ERROR,
                                     f"Sorry, there is no user with this {i} account. 🤔")
                return HttpResponseRedirect("/")

        for i in to_list:
            if i=='':
                messages.add_message(request, messages.ERROR,
                                     f"Sorry, receiver to can not be empty  🤷‍♂ 🧛‍♀️")
                return HttpResponseRedirect("/")

        to_list = [i for i in to_list if i in users_list]
        cc_list = [i for i in cc_list if i in users_list]
        bcc_list = [i for i in bcc_list if i in users_list]

        list_id_to = [User.objects.get(username=i).id for i in to_list]
        list_id_cc = [User.objects.get(username=i).id for i in cc_list]
        list_id_bcc = [User.objects.get(username=i).id for i in bcc_list]

        if form.is_valid():
            sender = User.objects.get(id=request.user.id)
            email_obj = Email(subject=form.cleaned_data['subject'],
                              text=form.cleaned_data['text'],
                              signature=signature,
                              file=form.cleaned_data['file'],
                              sender=sender
                              )
            email_obj.save()
            if 'draft' in request.POST:
                EmailFolder(user=sender, email=email_obj, is_draft = True).save()
                return redirect('/mail/draft')
            else:
                email_obj.cc.add(*list_id_cc)
                email_obj.receivers.add(*list_id_to)
                email_obj.bcc.add(*list_id_bcc)
                EmailFolder(user=sender, email=email_obj).save()

                for receiver in to_list:
                    EmailFolder(user=User.objects.get(username=receiver), email=email_obj).save()
                for receiver in cc_list:
                    EmailFolder(user=User.objects.get(username=receiver), email=email_obj).save()
                for receiver in bcc_list:
                    EmailFolder(user=User.objects.get(username=receiver), email=email_obj).save()

                messages.add_message(request, messages.SUCCESS,
                                     f'sent successfully. 😊👌')

                return HttpResponseRedirect("/")

        messages.error(request, f'{form.errors}')
        return redirect('/')


class EmailList(LoginRequiredMixin, View):

    def get(self, request):
        emails = Email.objects.all().filter(
            Q(sender=request.user.id) | Q(receivers=request.user.id)
            | Q(cc=request.user.id) | Q(bcc=request.user.id)).distinct()

        for e in emails:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            for i in email_folder:
                if i.is_trash is True or i.is_archive is True or i.is_draft is True:
                    emails = emails.exclude(pk=e.pk)

        emails_ = Email.objects.all().filter(Q(receivers=request.user.pk) | Q(cc=request.user.pk)
                                             | Q(bcc=request.user.pk))
        for email in emails_:
            if request.user.last_login <= email.created <= timezone.now():
                messages.add_message(request, messages.SUCCESS,
                                     f'An email was sent to you by {email.sender} on the {email.created}'
                                     f'with subject --> {email.subject}')

        return render(request, 'mail/email_list.html', {'emails': emails})


class EmailDetail(LoginRequiredMixin, DetailView):
    model = Email

    def get_context_data(self, **kwargs):
        context = super(EmailDetail, self).get_context_data(**kwargs)
        if context['object'].label:
            context['labels']=list(
                context['object'].label.filter(owner_id=self.request.user.pk))

        places = list(EmailFolder.objects.filter(email=context['object'].pk,
                                                 user_id=self.request.user.pk))
        context['places'] = places
        return context


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

            EmailFolder(user=email.sender, email=email_obj).save()
            EmailFolder(user=request.user,email=email_obj).save()

            messages.add_message(request, messages.SUCCESS,
                                 f'email replied. 😊👌')
            return redirect('/')
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

        EmailFolder(user=request.user, email=email_obj).save()

        for receiver in to_list:
            EmailFolder(user=User.objects.get(username=receiver), email=email_obj).save()
        for receiver in cc_list:
            EmailFolder(user=User.objects.get(username=receiver), email=email_obj).save()
        for receiver in bcc_list:
            EmailFolder(user=User.objects.get(username=receiver), email=email_obj).save()

        messages.add_message(request, messages.SUCCESS,
                             f'email Forwarded. 😊👌')
        return redirect('/')


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


        email.cc.add(*list_id_cc)
        email.receivers.add(*list_id_to)
        email.bcc.add(*list_id_bcc)

        place = EmailFolder.objects.get(user=forwarder, email=email.pk)
        place.is_draft = False
        place.save(update_fields=['is_draft'])

        for receiver in to_list:
            EmailFolder(user=User.objects.get(username=receiver), email=email).save()
        for receiver in cc_list:
            EmailFolder(user=User.objects.get(username=receiver), email=email).save()
        for receiver in bcc_list:
            EmailFolder(user=User.objects.get(username=receiver), email=email).save()

        return redirect(f'/mail/mail-detail/{pk}')


class DeleteEmail(LoginRequiredMixin, DeleteView):
    model = Email
    success_url = '/'



@login_required
def search_content_email(req):
    if req.method == 'POST':
        text = req.POST.get('text')
        if not text:
            json_data = json.loads(req.body)
            text = json_data['text']

        email = Email.objects.filter(subject__contains=text)
        email_list = email.values_list('text','subject')
        email_lst = list(itertools.chain(*email_list))
        emails = [i for i in email_lst if i]
        if email:
            return JsonResponse({
                'emails': emails
            })
        else:
            return JsonResponse({
                'emails': [],
                'msg': "doesn't match any emails",
            })
    else:
        return render(req, 'mail/search_content_email_box.html', {})


class FilterEmail(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, 'mail/filter_email.html', {})

    def post(self, request):

        if 'sender' in request.POST:
            search_input = request.POST['sender']
            users = User.objects.all().values_list('username', flat=True)
            users_list = [i for i in users]
            if search_input in users_list:
                query = Email.objects.filter(Q(sender=User.objects.get(username=search_input)) & (Q(receivers=request.user) |
                                                                               Q(cc=request.user) |
                                                                               Q(bcc=request.user)))
                filter = Filter(title=request.POST['filter_name'], owner=request.user)
                filter.save()
                for i in query:
                    i.filter.add(filter.id)

                return render(request, 'mail/result_filter.html', {'query': list(query)})


        if 'word' in request.POST:
            search_input = request.POST['word']
            query = Email.objects.filter(Q(subject__contains=search_input) | Q(text__contains=search_input) &
                                         (Q(receivers=request.user) |
                                          Q(cc=request.user) |
                                          Q(bcc=request.user)))

            filter = Filter(title=request.POST['filter_name'], owner=request.user)
            filter.save()
            for i in query:
                i.filter.add(filter.id)

            return render(request, 'mail/result_filter.html', {'query': list(query)})


"""
    label views: create, delete, search, list and detail
"""


class AddLabel(View):

    def get(self, request, pk):
        query = Label.objects.filter(owner=request.user).values_list('title', flat=True)
        return render(request, 'mail/add_label_to_email.html', {'query': list(query)})

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
        emails = Email.objects.filter(sender=request.user.id).distinct()
        for e in emails:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            print(f'_________{email_folder}')
            print(e)
            for i in email_folder:
                print(i)
                if i.is_trash is True or i.is_draft is True:
                    emails=emails.exclude(pk=e.pk)
        return render(request, 'mail/sent_box.html', {'sent_box': emails})


class Inbox(LoginRequiredMixin, View):
    def get(self, request):
        emails_to = Email.objects.filter(receivers=request.user.id).distinct()
        emails_cc = Email.objects.filter(cc=request.user.id).distinct()
        emails_bcc = Email.objects.filter(bcc=request.user.id).distinct()

        for e in emails_to:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            print(f'_________{email_folder}')
            print(e)
            for i in email_folder:
                print(i)
                if i.is_trash is True or i.is_draft is True or i.is_archive is True:
                    emails_to=emails_to.exclude(pk=e.pk)

        for e in emails_cc:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            print(f'_________{email_folder}')
            print(e)
            for i in email_folder:
                print(i)
                if i.is_trash is True or i.is_draft is True or i.is_archive is True:
                    emails_cc=emails_cc.exclude(pk=e.pk)

        for e in emails_bcc:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            print(f'_________{email_folder}')
            print(e)
            for i in email_folder:
                print(i)
                if i.is_trash is True or i.is_draft is True or i.is_archive is True:
                    emails_bcc=emails_bcc.exclude(pk=e.pk)

        return render(request, 'mail/inbox.html', {'emails_to': emails_to,
                                                   'emails_cc': emails_cc,
                                                   'emails_bcc': emails_bcc})


class Draft(LoginRequiredMixin, View):

    def get(self, request):
        emails = Email.objects.filter(sender=request.user.pk, cc=None, bcc=None, receivers=None)
        print(f'before{emails}')
        for e in emails:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            for i in email_folder:
                if i.is_draft is False or i.is_archive is True or i.is_trash is True:
                    emails = emails.exclude(pk=e.pk)
            print(f'after{emails}')
        return render(request, 'mail/draft.html', {'draft': emails})


class Archive(LoginRequiredMixin, View):

    def get(self, request):
        emails = Email.objects.filter(Q(sender=request.user.pk) | Q(bcc=request.user.pk) |
                                      Q(cc=request.user.pk) | Q(receivers=request.user.pk))
        for e in emails:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            print(f'_________{email_folder}')
            print(e)
            for i in email_folder:
                print(i)
                if i.is_archive is False or i.is_trash is True:
                    emails = emails.exclude(pk=e.pk)

        return render(request, 'mail/archive.html', {'archive': emails})


class Trash(LoginRequiredMixin, View):

    def get(self, request):
        emails = Email.objects.filter(Q(sender=request.user.pk) | Q(bcc=request.user.pk) |
                                      Q(cc=request.user.pk) | Q(receivers=request.user.pk))
        for e in emails:
            email_folder = EmailFolder.objects.filter(email=e.pk, user=request.user.pk)
            print(f'_________{email_folder}')
            print(e)
            for i in email_folder:
                print(i)
                if i.is_trash is False:
                    emails = emails.exclude(pk=e.pk)

        return render(request, 'mail/trash.html', {'trash': emails})


@login_required(redirect_field_name='login')
def check_archive(request, pk):
    if request.method == "GET":
        email = Email.objects.get(pk=pk)
        places = EmailFolder.objects.filter(user=request.user.pk, email=email.pk)
        for place in places:
            if place.is_archive is False:
                place.is_archive = True
            elif place.is_archive is True:
                place.is_archive = False
            place.save(update_fields=['is_archive'])
        return redirect('archive')


@login_required(redirect_field_name='login')
def check_trash(request, pk):
    if request.method == "GET":
        email = Email.objects.get(pk=pk)
        places = EmailFolder.objects.filter(user=request.user.pk, email=email.pk)
        for place in places:
            if place.is_trash is False:
                place.is_trash = True
            elif place.is_trash is True:
                place.is_trash = False
            place.save(update_fields=['is_trash', 'is_draft'])
        return redirect('trash')

"""
    آخیش🥱
"""

"""
signature
"""


class CreateSignature(LoginRequiredMixin, View):

    def get(self, request):
        form = SignatureModelForm()
        return render(request, 'mail/signature_form.html', {"form": form})

    def post(self, request):
        form = SignatureModelForm(request.POST, request.FILES)
        if form.is_valid():
            signature_obj = Signature(text=form.cleaned_data['text'],
                                      user=request.user)
            signature_obj.save()
            return HttpResponse('this signature created')


class SignatureList(LoginRequiredMixin, View):
    def get(self, request):
        signatures = Signature.objects.all().filter(user=request.user)
        return render(request, 'mail/signature_list.html', {'signatures': signatures})


class SignatureDetail(LoginRequiredMixin, DetailView):
    model = Signature



