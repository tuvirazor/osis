# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-03-27 12:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0008_auto_20180212_0905'),
    ]

    operations = [
        # Remove all deleted records physically
        migrations.RunSQL("DELETE FROM cms_translatedtextlabel WHERE deleted is not null"),
        migrations.RunSQL("DELETE FROM cms_translatedtext WHERE deleted is not null"),
        migrations.RunSQL("DELETE FROM cms_textlabel WHERE deleted is not null")
    ]
