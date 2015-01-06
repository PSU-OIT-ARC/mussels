# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminuser',
            name='is_superuser',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='specie',
            name='is_scientific_name',
            field=models.BooleanField(db_column='is_scientific_name', help_text='Determines if italics should be used when displaying on the map', default=False),
            preserve_default=True,
        ),
    ]
