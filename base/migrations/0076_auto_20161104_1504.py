# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-04 14:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0075_offeryear_enrollment_enabled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='examenrollment',
            name='enrollment_state',
            field=models.CharField(choices=[('ENROLLED', 'ENROLLED'), ('NOT_ENROLLED', 'NOT_ENROLLED')], db_index=True, default='ENROLLED', max_length=20),
        ),
    ]