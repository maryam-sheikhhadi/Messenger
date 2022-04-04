import json
from django.db.models import Count, Q
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
from django.http import JsonResponse
from django.urls import path
from django.contrib import admin
from .models import User
from mail.models import Email


def size_format(value):
    """
    Simple kb/mb/gb size
    """

    value = int(value)
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'last_name', 'email', 'first_name', 'birth_date', 'gender', 'country', 'date_joined',
        'get_user_storage', 'email_sent', 'email_received')
    list_filter = ('date_joined',)
    ordering = ('-date_joined',)

    def get_user_storage(self, obj):
        # to show on list display
        user_files = Email.objects.filter(sender=obj).exclude(Q(file='') | Q(file__isnull=True))
        total = sum(int(objects.file_size) for objects in user_files if objects.file_size)
        total = size_format(total)
        return total

    def email_sent(self, obj):
        # to show on list display
        # emails = Email.objects.filter(sender=obj).count
        emails = obj.sent_emails.count()
        return emails

    def email_received(self, obj):
        # to show on list display
        emails = Email.objects.filter(Q(receivers=obj) | Q(bcc=obj) | Q(cc=obj)).count()
        return emails

    def changelist_view(self, request, extra_context=None):
        # Aggregate new subscribers per day
        chart_data = (
            User.objects.annotate(date=TruncMonth("date_joined"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )

        email_whit_file = Email.objects.filter(file__isnull=False).exclude(file='')

        usernames = []
        for email in email_whit_file:
            usernames.append(User.objects.get(pk=email.sender_id))
        usernames = set(usernames)
        usernames = list(usernames)

        file_data = []
        for user in usernames:
            file_of_user = email_whit_file.filter(sender_id=user.id)
            total = sum(int(objects.file_size) for objects in file_of_user if objects.file_size)
            file_data.append({'user': user.username, 'user_size': total})

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json, "file_data": file_data}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("chart_data/", self.admin_site.admin_view(self.chart_data_endpoint))
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls

    # JSON endpoint for generating chart data that is used for dynamic loading
    # via JS.
    def chart_data_endpoint(self, request):
        chart_data = self.chart_data()
        return JsonResponse(list(chart_data), safe=False)

    def chart_data(self):
        return (
            User.objects.annotate(date=TruncMonth("date_joined"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )
