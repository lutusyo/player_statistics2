import pandas as pd
from django.shortcuts import render
from version2.psychology_app_v2.forms import UploadExcelForm
from version2.psychology_app_v2.models import Player, Assessment, AgeGroup


from django.db.models import Avg
from django.shortcuts import get_object_or_404
import json




def upload_excel(request):
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)

        if form.is_valid():
            file = request.FILES['file']

            # ✅ Read AGE (first row)
            df_age = pd.read_excel(file, header=None, nrows=1)

            age_group_value = (
                str(df_age.iloc[0, 1])
                .replace('\n', '')
                .replace(' ', '')
                .strip()
                .upper()
            )

            age_group, _ = AgeGroup.objects.get_or_create(name=age_group_value)

            # 🔥 Reset file pointer
            file.seek(0)

            # ✅ Read main data
            df = pd.read_excel(file, header=1)

            # ✅ Clean column names
            df.columns = (
                df.columns
                .str.replace('\n', ' ')
                .str.replace(r'\s+', ' ', regex=True)
                .str.strip()
            )

            current_player = None
            current_join_date = None
            current_core_character = None

            for _, row in df.iterrows():

                # ------------------------
                # ✅ HANDLE PLAYER NAME SAFELY
                # ------------------------

                raw_name = row.get('PLAYER NAME')

                if pd.notna(raw_name):
                    name = str(raw_name).strip().upper()

                    # Track player info
                    if not pd.isna(row.get('JOIN DATE')):
                        current_join_date = parse_date(row.get('JOIN DATE'))

                    if not pd.isna(row.get('CORE CHARACTER')):
                        current_core_character = row.get('CORE CHARACTER')

                    # Create / update player
                    current_player, created = Player.objects.get_or_create(
                        player_name=name,
                        defaults={
                            'join_date': current_join_date,
                            'core_character': current_core_character,
                            'age_group': age_group,
                        }
                    )

                    if not created:
                        current_player.join_date = current_join_date
                        current_player.core_character = current_core_character
                        current_player.age_group = age_group
                        current_player.save()

                # ------------------------
                # ❌ SKIP INVALID ROWS
                # ------------------------

                if not current_player or pd.isna(row.get('START')):
                    continue

                # ------------------------
                # ✅ CREATE ASSESSMENT
                # ------------------------

                Assessment.objects.create(
                    player=current_player,
                    start_date=parse_date(row.get('START')),
                    end_date=parse_date(row.get('END')),
                    task=str(row.get('TASK')).strip().title() if row.get('TASK') else None,

                    iq_range=parse_int(row.get('IQ RANGE')),

                    cognitive_percent=clean_percent(row.get('COGNITIVE')),
                    personality_percent=clean_percent(row.get('PERSONALITY')),
                    neuro_psychology_percent=clean_percent(row.get('NEURO PSYCHOLOGY')),
                    education_percent=clean_percent(row.get('EDUCATION')),
                    overall=clean_percent(row.get('OVERALL')),
                )

    else:
        form = UploadExcelForm()

    return render(request, 'psychology_app_v2/upload.html', {'form': form})

def clean_percent(value):
    if pd.isna(value):
        return None
    return float(str(value).replace('%', '').strip())


def parse_date(value):
    if pd.isna(value):
        return None
    try:
        return pd.to_datetime(value).date()
    except:
        return None


def parse_int(value):
    try:
        return int(value)
    except:
        return None
