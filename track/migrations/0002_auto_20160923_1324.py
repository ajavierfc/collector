# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-23 13:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='link',
            name='upload',
        ),
        migrations.DeleteModel(
            name='Link',
        ),
    ]
