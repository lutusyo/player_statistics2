import os
import pandas as pd
from players_app.models import Player
from teams_app.models import AgeGroup
from django.core.files import File

def import_players(file_path):
    try:
        df = pd.read_excel(file_path)

        # Ensure the Under 17 age group exists
        age_group_name = 'SENIOR'
        try:
            age_group = AgeGroup.objects.get(name=age_group_name)
        except AgeGroup.DoesNotExist:
            print(f"❌ Age group '{age_group_name}' does not exist.")
            return

        for _, row in df.iterrows():
            name = str(row['name']).strip()
            birthdate = row.get('birthdate', None)
            position = row.get('position', '')
            foot = row.get('p_foot', 'Right')
            jersey = row.get('jersey_no', 0)
            height = row.get('height', 170)
            weight = row.get('weight', 65)
            former_club = row.get('former_club', 'Null')

        

            # Avoid duplicates (check by name and birthdate if available)
            exists_query = Player.objects.filter(name=name)
            if birthdate:
                exists_query = exists_query.filter(birthdate=birthdate)

            if exists_query.exists():
                print(f"⏭️ Skipping existing player: {name}")
                continue

            # Create new player
            player = Player(
                name=name,
                birthdate=birthdate,
                place_of_birth='Tanzania',
                nationality='Tanzania',
                position=position,
                height=height,
                weight=weight,
                foot_preference=foot,
                jersey_number=jersey,
                former_club=former_club,
                age_group=age_group
            )


            player.save()
            print(f"✅ Imported: {name}")

        print("🎉 All players processed successfully.")

    except Exception as e:
        print(f"❌ Error importing players: {e}")
