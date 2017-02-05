# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-15 08:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20160210_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='offeryear',
            name='offer_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='base.OfferYear'),
        ),
    ]