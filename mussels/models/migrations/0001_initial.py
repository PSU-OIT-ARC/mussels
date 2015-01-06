# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=100, db_index=True)),
                ('email', models.EmailField(max_length=100)),
                ('first_name', models.CharField(max_length=30, blank=True)),
                ('last_name', models.CharField(max_length=30, blank=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('agency_id', models.AutoField(serialize=False, primary_key=True, db_column='agency_id')),
                ('name', models.CharField(max_length=255, db_column='name')),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'agency',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('observation_id', models.AutoField(serialize=False, primary_key=True, db_column='observation_id')),
                ('date_checked', models.DateField(db_column='date_checked')),
                ('physical_description', models.TextField()),
                ('is_approved', models.BooleanField(default=False, db_column='approved')),
                ('clr_substrate_id', models.IntegerField(default=0, db_column='clr_substrate_id', blank=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326, db_column='the_geom')),
                ('agency', models.ForeignKey(db_column='agency_id', to='models.Agency', null=True, blank=True)),
            ],
            options={
                'db_table': 'observation',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ObservationSubstrate',
            fields=[
                ('substrate_type_id', models.AutoField(serialize=False, primary_key=True, db_column='observation_substrate_id')),
                ('observation', models.ForeignKey(to='models.Observation', db_column='observation_id')),
            ],
            options={
                'db_table': 'observation_substrate',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Specie',
            fields=[
                ('specie_id', models.AutoField(serialize=False, primary_key=True, db_column='specie_id')),
                ('name', models.CharField(max_length=255, db_column='name')),
                ('order_id', models.IntegerField(help_text='The order this should appear in on the legend and search form', db_column='order_id')),
                ('machine_name', models.CharField(help_text='The name used for the map icon', max_length=30, db_column='machine_name')),
                ('is_scientific_name', models.BooleanField(help_text='Determines if italics should be used when displaying on the map', db_column='is_scientific_name')),
            ],
            options={
                'ordering': ['order_id'],
                'db_table': 'specie',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Substrate',
            fields=[
                ('substrate_id', models.AutoField(serialize=False, primary_key=True, db_column='substrate_id')),
                ('name', models.CharField(max_length=255, db_column='name')),
                ('order_id', models.IntegerField(help_text='The order this should appear in on the legend and search form', db_column='order_id')),
                ('machine_name', models.CharField(help_text='The name used for the map icon', max_length=30, db_column='machine_name')),
            ],
            options={
                'ordering': ['order_id'],
                'db_table': 'substrate',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(serialize=False, primary_key=True, db_column='user_id')),
                ('username', models.CharField(max_length=255, db_column='username', blank=True)),
                ('first_name', models.CharField(max_length=255, db_column='fname', blank=True)),
                ('last_name', models.CharField(max_length=255, db_column='lname', blank=True)),
                ('title', models.CharField(max_length=255, db_column='title', blank=True)),
                ('address1', models.CharField(max_length=255, db_column='address1', blank=True)),
                ('address2', models.CharField(max_length=255, db_column='address2', blank=True)),
                ('city', models.CharField(max_length=255, db_column='city', blank=True)),
                ('state', models.CharField(max_length=255, db_column='state', blank=True)),
                ('zip', models.CharField(max_length=255, db_column='zip', blank=True)),
                ('phone1', models.CharField(max_length=255, db_column='phone1', blank=True)),
                ('phone2', models.CharField(max_length=255, db_column='phone2', blank=True)),
                ('email', models.CharField(max_length=255, db_column='email', blank=True)),
                ('reminder', models.CharField(max_length=255, db_column='reminder', blank=True)),
                ('winter_hold_start', models.CharField(max_length=255, db_column='winter_hold_start', blank=True)),
                ('winter_hold_stop', models.CharField(max_length=255, db_column='winter_hold_stop', blank=True)),
                ('admin_notes', models.CharField(max_length=255, db_column='admin_notes', blank=True)),
                ('need_new_mesh', models.BooleanField(default=False, db_column='need_new_mesh')),
                ('is_active', models.BooleanField(default=True, db_column='active')),
            ],
            options={
                'db_table': 'reporter',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Waterbody',
            fields=[
                ('waterbody_id', models.AutoField(serialize=False, primary_key=True, db_column='waterbody_id')),
                ('name', models.CharField(max_length=255, db_column='name')),
                ('reachcode', models.CharField(max_length=32, db_column='reachcode', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'waterbody',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='observationsubstrate',
            name='substrate',
            field=models.ForeignKey(to='models.Substrate', db_column='substrate_id'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='specie',
            field=models.ForeignKey(to='models.Specie', db_column='specie_id'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='substrates',
            field=models.ManyToManyField(to='models.Substrate', through='models.ObservationSubstrate'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='user',
            field=models.ForeignKey(to='models.User', db_column='user_id'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='observation',
            name='waterbody',
            field=models.ForeignKey(db_column='waterbody_id', to='models.Waterbody', null=True, blank=True),
            preserve_default=True,
        ),
    ]
