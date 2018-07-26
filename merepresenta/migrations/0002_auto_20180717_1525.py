# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-17 15:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('backend_candidate', '0014_remove_suggesting_models'),
        ('merepresenta', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VolunteerGetsCandidateEmailLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='VolunteerInCandidate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('elections.candidate',),
        ),
        migrations.AddField(
            model_name='volunteerincandidate',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merepresenta.Candidate'),
        ),
        migrations.AddField(
            model_name='volunteerincandidate',
            name='volunteer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='volunteergetscandidateemaillog',
            name='candidate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merepresenta.Candidate'),
        ),
        migrations.AddField(
            model_name='volunteergetscandidateemaillog',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='backend_candidate.CandidacyContact'),
        ),
        migrations.AddField(
            model_name='volunteergetscandidateemaillog',
            name='volunteer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]