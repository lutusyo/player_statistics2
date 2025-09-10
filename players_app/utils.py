import pandas as pd
from players_app.models import Player

def import_players_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            Player.objects.create(
                name=row['name'],
                birthdate=str(row.get('birthdate', '')),
                place_of_birth='Tanzania',
                nationality='Tanzania',
                position=row['position'],
                height=row.get('height', 170),
                weight=row.get('weight', 65),
                foot_preference=row.get('p_foot', 'Right'),
                jersey_number=row.get('jersey_no', 0),
                age_group='U17',  # Fixed for all
                # photo uses default
            )

        print("✅ All players imported successfully.")
    except Exception as e:
        print(f"❌ Error importing players: {e}")
