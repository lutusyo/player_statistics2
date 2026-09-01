import pandas as pd
from django.shortcuts import render
from version2.psychology_app_v2.forms import UploadExcelForm

from version1.players_app.models import Player
from version2.psychology_app_v2.models import  Assessment
from version1.players_app.models import AgeGroup

from django.db.models import Avg
from django.shortcuts import get_object_or_404
import json
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta  # install if needed


# ✅ HELPER FUNCTIONS

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


# ✅ DASHBOARD VIEW



def home(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    period = request.GET.get('period')  # 👈 NEW

    assessments = Assessment.objects.all().order_by('start_date')

    # -----------------------------------
    # ✅ PERIOD FILTER (PRIORITY)
    # -----------------------------------
    if period:
        try:
            period = int(period)

            first_assessment = assessments.first()

            if first_assessment and first_assessment.start_date:
                start = first_assessment.start_date

                # 🔥 1 psychology month = 2 real months
                end = start + relativedelta(months=period * 2)

                assessments = assessments.filter(
                    start_date__gte=start,
                    end_date__lte=end
                )

                # override for UI display
                start_date = start
                end_date = end

        except:
            pass

    # ✅ NORMAL DATE FILTER
    else:
        if start_date:
            assessments = assessments.filter(start_date__gte=start_date)

        if end_date:
            assessments = assessments.filter(end_date__lte=end_date)


    # 📊 STATS
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

    # ✅ CONVERT TO %
    for key in overall_stats:
        if overall_stats[key] is not None:
            overall_stats[key] = overall_stats[key] * 100

    context = {
        'total_players': total_players,
        'total_assessments': total_assessments,
        'age_groups': age_groups,
        'overall_stats': overall_stats,
        'start_date': start_date,
        'end_date': end_date,
        'period': str(period) if period else "",  # 👈 IMPORTANT
    }

    return render(request, 'psychology_app_v2/psychology_home.html', context)
