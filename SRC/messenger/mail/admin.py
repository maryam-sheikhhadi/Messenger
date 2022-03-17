from django.contrib import admin
from .models import Label, Signature, Email, Filter, EmailFolder

admin.site.register(Email)
admin.site.register(Label)
admin.site.register(Signature)
admin.site.register(Filter)
admin.site.register(EmailFolder)