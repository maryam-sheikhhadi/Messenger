from django.contrib import admin
from .models import Label, Signature, Email

admin.site.register(Email)
admin.site.register(Label)
admin.site.register(Signature)