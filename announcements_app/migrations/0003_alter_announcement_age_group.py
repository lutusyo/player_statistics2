# Generated by Django 5.2.1 on 2025-07-23 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcements_app', '0002_alter_announcement_age_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='age_group',
            field=models.CharField(choices=[('U20', 'Under 20'), ('U17', 'Under 17'), ('U15', 'Under 15'), ('U13', 'Under 13'), ('U10', 'Under 10'), ('ALL', 'All Age Groups')], max_length=10),
        ),
    ]
