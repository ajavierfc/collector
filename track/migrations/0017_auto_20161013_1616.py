# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-13 16:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0016_upload_link_crc32'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='link_crc32',
            field=models.BigIntegerField(default=0),
        ),
    ]
