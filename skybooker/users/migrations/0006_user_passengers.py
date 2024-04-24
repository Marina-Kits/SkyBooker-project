# Generated by Django 5.0.4 on 2024-04-24 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_passenger_passengers'),
        ('users', '0005_delete_passenger'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='passengers',
            field=models.ManyToManyField(blank=True, related_name='users', to='main.passenger'),
        ),
    ]
