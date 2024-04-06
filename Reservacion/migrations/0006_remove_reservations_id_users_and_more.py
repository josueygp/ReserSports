# Generated by Django 5.0.1 on 2024-01-27 21:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reservacion', '0005_remove_clients_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservations',
            name='id_users',
        ),
        migrations.RemoveField(
            model_name='reservations',
            name='name',
        ),
        migrations.AddField(
            model_name='reservations',
            name='id_clients',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Reservacion.clients'),
        ),
        migrations.AlterField(
            model_name='reservations',
            name='id_admistrators',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
