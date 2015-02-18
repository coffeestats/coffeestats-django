# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('caffeine', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caffeine',
            name='user',
            field=models.ForeignKey(related_name='caffeines', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
