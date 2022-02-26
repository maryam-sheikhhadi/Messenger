from django.contrib import admin
from .models import Email, Label, Contact, Signature


admin.site.register(Email)
admin.site.register(Label)
admin.site.register(Contact)
admin.site.register(Signature)