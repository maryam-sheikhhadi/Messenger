# Generated by Django 3.2 on 2022-03-01 18:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0005_email_is_reply'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='email',
            name='is_reply',
        ),
        migrations.AddField(
            model_name='email',
            name='email_object',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mail.email'),
        ),
    ]
