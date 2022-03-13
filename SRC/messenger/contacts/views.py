import itertools

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from accounts.models import User
from .forms import ContactModelForm
from .models import Contact
from django.http import HttpResponse
import csv


class CreateContact(LoginRequiredMixin, View):

    def get(self, request):
        form = ContactModelForm()
        return render(request, 'contacts/create_contact.html', {"form": form})

    def post(self, request):
        form = ContactModelForm(request.POST)
        if form.is_valid():
            contact_obj = Contact(first_name=form.cleaned_data['first_name'],
                                  last_name=form.cleaned_data['last_name'],
                                  email=form.cleaned_data['email'],
                                  other_emails=form.cleaned_data['other_emails'],
                                  phone_number=form.cleaned_data['phone_number'],
                                  birth_date=form.cleaned_data['birth_date'],
                                  user=User.objects.get(id=request.user.id)
                                  )
            contact_obj.save()
            return redirect("/contacts/all-contacts")


class ContactList(LoginRequiredMixin, ListView):
    def get(self, request):
        contacts_of_user = Contact.objects.all().filter(user=request.user.id)

        return render(request, 'contacts/contact_list.html', {'contacts_of_user': contacts_of_user})


class ContactDetail(LoginRequiredMixin, DetailView):
    model = Contact


class UpdateContact(LoginRequiredMixin, UpdateView):
    model = Contact
    template_name = 'contacts/edite_contact.html'
    fields = ['first_name', 'last_name', 'email', 'birth_date', 'phone_number', 'other_emails']
    success_url = '/'


class DeleteContact(LoginRequiredMixin, DeleteView):
    model = Contact
    success_url = '/'


def export_csv_contacts_list(request):
    contacts = Contact.objects.all().filter(user=request.user)
    response = HttpResponse('')
    response['Content-Disposition'] = 'attachment; filename=contacts.csv'
    writer = csv.writer(response)
    writer.writerow(['first_name', 'last_name', 'email', 'other_emails', 'phone_number', 'birth_date'])
    contacts = contacts.values_list('first_name', 'last_name', 'email', 'other_emails', 'phone_number', 'birth_date')
    for contact in contacts:
        writer.writerow(contact)
    return response


class SearchByFieldContact(LoginRequiredMixin, View):

    def get(self, request):
        fields_contacts_list = Contact.objects.all().filter(user=request.user.id).values_list('first_name', 'last_name',
                                                                                              'email', 'other_emails',
                                                                                              'phone_number')
        # c = Contact.objects.all().filter(user=request.user.id).values_list('birth_date', flat=True)
        # c2 = [i.strftime("%m/%d/%Y") for i in c if i]
        # print(c2)
        # last_name_list = Contact.objects.all().filter(owner=request.user.id).values_list('last_name', flat=True)
        # email_list = Contact.objects.all().filter(owner=request.user.id).values_list('email', flat=True)
        # other_emails_list = Contact.objects.all().filter(owner=request.user.id).values_list('other_emails', flat=True)
        # phone_number_list = Contact.objects.all().filter(owner=request.user.id).values_list('phone_number', flat=True)
        # birth_date_list = Contact.objects.all().filter(owner=request.user.id).values_list('birth_date', flat=True)
        r = list(itertools.chain(*fields_contacts_list))
        res = [i for i in r if i]
        print(res)
        return render(request, 'contacts/search_fields_contact.html', {'res': res})

    # def post(self, request):
    #     search_fields_contacts = request.POST['search_label']
    #
    #     result = Contact.objects.all()
    #
    #     return render(request, 'mail/email_with_label_input.html', {'result': result})
