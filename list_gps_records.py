import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "player_statistics_project.settings")
django.setup()

from gps_app.models import GPSRecord

print("📋 Listing all GPS records...\n")

records = GPSRecord.objects.all()

if records.exists():
    for r in records:
        match_info = f"Match ID: {r.match.id}" if r.match else "No match linked"
        print(f"Player: {r.player}, Pod: {r.pod_number}, {match_info}")
else:
    print("⚠️  No GPS records found in the database.")
