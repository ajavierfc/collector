# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 12:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0010_link_host'),
    ]

    operations = [
        migrations.AddField(
            model_name='release',
            name='host_list',
            field=models.CharField(default='', max_length=200),
        ),
    ]
