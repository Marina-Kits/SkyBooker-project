# Generated by Django 5.0.4 on 2024-05-24 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_ticket_delete_tickets'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='reminder_sent',
            field=models.BooleanField(default=False),
        ),
    ]