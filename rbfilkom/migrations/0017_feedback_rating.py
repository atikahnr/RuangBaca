# Generated by Django 2.1b1 on 2019-02-10 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbfilkom', '0016_auto_20190210_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]