# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 15:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0012_auto_20161007_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='release',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='track.Release'),
        ),
    ]
