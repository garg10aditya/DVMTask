# Generated by Django 4.2.1 on 2023-05-18 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='isVendor',
            field=models.BooleanField(default=False),
        ),
    ]
