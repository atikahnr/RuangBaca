# Generated by Django 2.1b1 on 2019-02-09 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbfilkom', '0006_notifikasi'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifikasi',
            name='viewed',
            field=models.BooleanField(default=False),
        ),
    ]