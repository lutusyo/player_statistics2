# Generated by Django 5.2.1 on 2025-07-25 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actions_app', '0009_playerdetailedaction_red_cards_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerdetailedaction',
            name='minutes_played',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
