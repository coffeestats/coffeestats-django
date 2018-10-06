# Generated by Django 2.1.2 on 2018-10-06 10:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('caffeine_oauth2', '0003_auto_20160930_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='coffeestatsapplication',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='coffeestatsapplication',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='coffeestatsapplication',
            name='agree',
            field=models.BooleanField(help_text='You have to agree to the <a href="/api/v2/agreement/">API usage agreement</a> to use our APIs.', verbose_name='accept API usage agreement'),
        ),
        migrations.AlterField(
            model_name='coffeestatsapplication',
            name='approved_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='coffeestatsapplication',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='coffeestatsapplication',
            name='logo',
            field=models.ImageField(upload_to='appimages', verbose_name='application logo'),
        ),
        migrations.AlterField(
            model_name='coffeestatsapplication',
            name='redirect_uris',
            field=models.TextField(blank=True, help_text='Allowed URIs list, space separated'),
        ),
        migrations.AlterField(
            model_name='coffeestatsapplication',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='caffeine_oauth2_coffeestatsapplication', to=settings.AUTH_USER_MODEL),
        ),
    ]
