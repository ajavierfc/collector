# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-14 10:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0022_uploadhost'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UploadHost',
            new_name='Upload_Host',
        ),
    ]
