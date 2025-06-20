# Generated by Django 5.1.6 on 2025-06-09 18:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('birthdate', models.CharField(blank=True, max_length=10, null=True)),
                ('place_of_birth', models.CharField(default='Tanzania', max_length=100)),
                ('natinality', models.CharField(default='Tanzania', max_length=50)),
                ('position', models.CharField(choices=[('Forward', 'Forward'), ('Midfielder', 'Midfielder'), ('Defender', 'Defender'), ('Goalkeeper', 'Goalkeeper')], max_length=50)),
                ('height', models.DecimalField(decimal_places=0, default=170, max_digits=5)),
                ('weight', models.DecimalField(decimal_places=0, default=65, max_digits=5)),
                ('foot_preference', models.CharField(choices=[('Left', 'Left'), ('Right', 'Right')], default='Right', max_length=5)),
                ('jersey_number', models.PositiveIntegerField(default=0)),
                ('photo', models.ImageField(default='files_to_be_imported/default_image.png', upload_to='player_photos/')),
                ('age_group', models.CharField(choices=[('U20', 'Under 20'), ('U17', 'Under 17'), ('U15', 'Under 15')], default='U20', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerCareerStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage_type', models.CharField(choices=[('academy', 'Academy'), ('club', 'Club'), ('national', 'National Team')], max_length=20)),
                ('team_name', models.CharField(max_length=100)),
                ('start_year', models.PositiveIntegerField()),
                ('end_year', models.PositiveIntegerField(blank=True, null=True)),
                ('position', models.CharField(blank=True, max_length=50)),
                ('matches_played', models.PositiveIntegerField(default=0)),
                ('minutes_played', models.PositiveIntegerField(default=0)),
                ('goals_scored', models.PositiveIntegerField(default=0)),
                ('assists', models.PositiveIntegerField(default=0)),
                ('notes', models.TextField(blank=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='career_stages', to='players_app.player')),
            ],
            options={
                'ordering': ['start_year'],
            },
        ),
    ]
