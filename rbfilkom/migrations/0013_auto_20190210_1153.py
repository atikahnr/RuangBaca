# Generated by Django 2.1b1 on 2019-02-10 04:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rbfilkom', '0012_auto_20190209_2047'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='denda',
            name='kode_transaksi',
        ),
        migrations.DeleteModel(
            name='Denda',
        ),
    ]