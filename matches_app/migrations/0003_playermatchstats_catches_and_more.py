# Generated by Django 5.2.1 on 2025-06-26 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches_app', '0002_match_match_time_match_team_match_venue'),
    ]

    operations = [
        migrations.AddField(
            model_name='playermatchstats',
            name='catches',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='playermatchstats',
            name='clean_sheets',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='playermatchstats',
            name='clearances',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='playermatchstats',
            name='drops',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='playermatchstats',
            name='is_goalkeeper',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='playermatchstats',
            name='penalties_saved',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='playermatchstats',
            name='punches',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='playermatchstats',
            name='saves_success_rate',
            field=models.FloatField(blank=True, default=0.0),
        ),
    ]
