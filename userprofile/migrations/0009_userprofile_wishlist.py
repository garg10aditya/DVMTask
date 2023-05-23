# Generated by Django 4.2.1 on 2023-05-20 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_wishlist'),
        ('userprofile', '0008_userprofile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='wishlist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='userprofile', to='store.wishlist'),
        ),
    ]