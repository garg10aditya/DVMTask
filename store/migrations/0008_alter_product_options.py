# Generated by Django 4.2.1 on 2023-05-19 08:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_order_orderitem_delete_orders'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('-avail_qty',)},
        ),
    ]