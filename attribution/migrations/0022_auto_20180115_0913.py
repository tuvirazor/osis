# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-15 08:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0021_attributionnew_substitute'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attributionnew',
            name='substitute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Person'),
        ),
    ]
