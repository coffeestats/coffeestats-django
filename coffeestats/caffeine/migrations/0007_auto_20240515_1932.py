# Generated by Django 3.1.14 on 2024-05-15 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caffeine', '0006_auto_20240515_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]
