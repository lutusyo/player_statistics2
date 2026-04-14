import pandas as pd
from django.shortcuts import render
from .forms import UploadExcelForm
from .models import Player, Assessment, AgeGroup


from django.db.models import Avg
from .models import Player, Assessment, AgeGroup

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


# ------------------------
# ✅ HELPER FUNCTIONS
# ------------------------

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


# ------------------------
# ✅ DASHBOARD VIEW
# ------------------------




from django.db.models import Avg
from datetime import datetime

def home(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    assessments = Assessment.objects.all()

    # 🎯 Apply date filtering
    if start_date:
        assessments = assessments.filter(start_date__gte=start_date)

    if end_date:
        assessments = assessments.filter(end_date__lte=end_date)

    total_players = Player.objects.count()
    total_assessments = assessments.count()
    age_groups = AgeGroup.objects.all()

    overall_stats = assessments.aggregate(
        avg_cognitive=Avg('cognitive_percent'),
        avg_personality=Avg('personality_percent'),
        avg_neuro=Avg('neuro_psychology_percent'),
        avg_education=Avg('education_percent'),
        avg_overall=Avg('overall'),
    )

    context = {
        'total_players': total_players,
        'total_assessments': total_assessments,
        'age_groups': age_groups,
        'overall_stats': overall_stats,
        'start_date': start_date,
        'end_date': end_date,
    }


    return render(request, 'psychology_app_v2/psychology_home.html', context)









def player_list(request):
    age_group_id = request.GET.get('age_group')

    players = Player.objects.prefetch_related('assessments')

    if age_group_id:
        players = players.filter(age_group_id=age_group_id)

    age_groups = AgeGroup.objects.all()

    context = {
        'players': players,
        'age_groups': age_groups,
        'selected_age_group': age_group_id,
    }

    return render(request, 'psychology_app_v2/player_list.html', context)





from django.db.models import Avg
import json

def player_detail(request, player_id):
    player = get_object_or_404(Player, id=player_id)

    # 🎯 Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    compare_id = request.GET.get('compare')

    assessments = player.assessments.all().order_by('start_date')

    if start_date:
        assessments = assessments.filter(start_date__gte=start_date)

    if end_date:
        assessments = assessments.filter(end_date__lte=end_date)

    # 📈 Main player data
    dates = [a.start_date.strftime('%Y-%m-%d') for a in assessments if a.start_date]
    overall = [(a.overall or 0) * 100 for a in assessments]

    # 🔥 Fix scale issue (dynamic min/max)
    all_values = [v for v in overall if v is not None]
    y_min = min(all_values) - 5 if all_values else 0
    y_max = max(all_values) + 5 if all_values else 100

    # 🆚 Comparison player
    compare_player = None
    compare_data = []

    if compare_id:
        compare_player = Player.objects.get(id=compare_id)
        compare_assessments = compare_player.assessments.all().order_by('start_date')

        compare_data = [(a.overall or 0) * 100 for a in compare_assessments]

    # 🧠 Radar chart (average scores)
    radar_stats = assessments.aggregate(
        cognitive=Avg('cognitive_percent'),
        personality=Avg('personality_percent'),
        neuro=Avg('neuro_psychology_percent'),
        education=Avg('education_percent'),
    )

    context = {
        'player': player,
        'assessments': assessments,
        'dates': json.dumps(dates),
        'overall': json.dumps(overall),
        'y_min': y_min,
        'y_max': y_max,
        'compare_player': compare_player,
        'compare_data': json.dumps(compare_data),
        'players': Player.objects.all(),  # for dropdown

        'radar': json.dumps([
        (radar_stats['cognitive'] or 0) * 100,
        (radar_stats['personality'] or 0) * 100,
        (radar_stats['neuro'] or 0) * 100,
        (radar_stats['education'] or 0) * 100,
        ]),

        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'psychology_app_v2/player_detail.html', context)