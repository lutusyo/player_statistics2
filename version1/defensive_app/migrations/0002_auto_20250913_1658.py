from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("defensive_app", "0001_initial"),  # replace with your latest migration filename
    ]

    operations = [
        migrations.RemoveField(
            model_name="playerdefensivestats",
            name="corner",
        ),
    ]
