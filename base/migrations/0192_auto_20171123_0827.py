# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-11-23 07:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0191_auto_20171122_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupelementyear',
            name='sessions_derogation',
            field=models.CharField(choices=[('SESSION_1', 'SESSION_1'), ('SESSION_2', 'SESSION_2'), ('SESSION_3', 'SESSION_3'), ('SESSION_1_2', 'SESSION_1_2'), ('SESSION_1_3', 'SESSION_1_3'), ('SESSION_2_3', 'SESSION_2_3'), ('SESSION_1_2_3', 'SESSION_1_2_3'), ('SESSION_UNDEFINED', 'SESSION_UNDEFINED'), ('SESSION_PARTIAL_2_3', 'SESSION_PARTIAL_2_3')], default='SESSION_UNDEFINED', max_length=65),
        ),
        migrations.AlterField(
            model_name='educationgrouporganization',
            name='diploma',
            field=models.CharField(choices=[('UNIQUE', 'UNIQUE'), ('SEPARATE', 'SEPARATE'), ('NOT_CONCERNED', 'NOT_CONCERNED')], default='NOT_CONCERNED', max_length=40),
        ),
    ]
