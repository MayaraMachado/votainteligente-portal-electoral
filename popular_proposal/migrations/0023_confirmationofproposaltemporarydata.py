# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-13 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('popular_proposal', '0022_auto_20170612_1710'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfirmationOfProposalTemporaryData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.UUIDField(default=uuid.uuid4)),
                ('confirmed', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('temporary_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='confirmation', to='popular_proposal.ProposalTemporaryData')),
            ],
        ),
    ]
