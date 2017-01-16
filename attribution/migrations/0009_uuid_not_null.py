# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-01-05 12:15
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0008_populate_uuid_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribution',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
