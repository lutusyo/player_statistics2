from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from reports_app.forms import ReportFilterForm
from reports_app.models import (
    Medical, Transition, Scouting, Performance,
    IndividualActionPlan, Mesocycle, FitnessPlan
)
from django.shortcuts import render, get_object_or_404
from teams_app.models import Team


SECTION_MAP = {
    'Medical': (Medical, 'date'),
    'Transition': (Transition, 'date'),
    'Scouting': (Scouting, 'date'),
    'Performance': (Performance, 'date'),
    'IAP': (IndividualActionPlan, 'date'),
    'Mesocycle': (Mesocycle, 'start_date'),
    'Fitness': (FitnessPlan, 'date'),
}



def filter_queryset_by_period(queryset, period, start_date=None, end_date=None, date_field='date'):
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()

    if period == 'day':
        queryset = queryset.filter(**{date_field: today})
    elif period == 'week':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        queryset = queryset.filter(**{f"{date_field}__range": [week_start, week_end]})
    elif period == 'month':
        queryset = queryset.filter(**{f"{date_field}__month": today.month, f"{date_field}__year": today.year})
    elif period == 'custom' and start_date and end_date:
        queryset = queryset.filter(**{f"{date_field}__range": [start_date, end_date]})

    return queryset





def reports_dashboard(request, team_id=None):
    """Team-specific Reports Dashboard."""
    team = get_object_or_404(Team, id=team_id) if team_id else None
    form = ReportFilterForm(request.GET or None)
    context = {'form': form, 'team': team}

    section_data = {}

    if form.is_valid():
        team_selected = form.cleaned_data.get('team') or team
        period = form.cleaned_data.get('period')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        # Convert custom dates to date objects
        if period == 'custom' and start_date and end_date:
            from datetime import datetime
            start_date = datetime.strptime(str(start_date), "%Y-%m-%d").date()
            end_date = datetime.strptime(str(end_date), "%Y-%m-%d").date()

        for key, (model, date_field) in SECTION_MAP.items():
            qs = model.objects.all()
            if team_selected:
                if hasattr(model, 'squad'):
                    qs = qs.filter(squad=team_selected)
                elif hasattr(model, 'team'):
                    qs = qs.filter(team=team_selected)
            if period:
                qs = filter_queryset_by_period(qs, period, start_date, end_date, date_field)

            section_data[key.lower()] = qs

    context.update(section_data)
    return render(request, 'reports_app/daily_report_templates/reports_dashboard.html', context)



