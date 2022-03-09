from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from accounts.models import User
from .forms import ContactModelForm
from .models import Contact


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


# class ContactList(LoginRequiredMixin, ListView):
#     model = Contact
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