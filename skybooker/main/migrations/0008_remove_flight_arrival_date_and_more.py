# Generated by Django 5.0.4 on 2024-04-27 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_flight_arrival_date_flight_departure_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flight',
            name='arrival_date',
        ),
        migrations.RemoveField(
            model_name='flight',
            name='departure_date',
        ),
        migrations.AlterField(
            model_name='flight',
            name='arrival_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='flight',
            name='departure_time',
            field=models.DateTimeField(),
        ),
    ]
