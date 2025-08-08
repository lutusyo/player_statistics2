# check_gps_data.py

import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "player_statistics_project.settings")
django.setup()

from gps_app.models import GPSRecord
from matches_app.models import Match

def main():
    print("🔍 Checking GPS data per match...\n")

    has_data = False
    for match in Match.objects.all():
        count = GPSRecord.objects.filter(match=match).count()
        if count > 0:
            has_data = True
            print(f"✅ Match ID {match.id} | {match.get_team_display()} vs {match.opponent} ({match.date})")
            print(f"   - GPS Records: {count}\n")

    if not has_data:
        print("⚠️  No matches have any GPS data linked.\n")

if __name__ == "__main__":
    main()
