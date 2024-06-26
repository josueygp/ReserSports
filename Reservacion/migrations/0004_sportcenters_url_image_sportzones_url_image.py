# Generated by Django 5.0.1 on 2024-01-23 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Reservacion', '0003_sportzonesphotos_url_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='sportcenters',
            name='url_image',
            field=models.ImageField(default='images/transparent.png', upload_to='images/sport-centers/'),
        ),
        migrations.AddField(
            model_name='sportzones',
            name='url_image',
            field=models.ImageField(default='images/transparent.png', upload_to='images/sport-zones/'),
        ),
    ]
