# Generated by Django 5.2.1 on 2025-07-08 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gps_app', '0004_alter_gpsrecord_top_speed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gpsrecord',
            name='top_speed',
        ),
    ]
