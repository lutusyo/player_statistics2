from django.shortcuts import render, get_object_or_404
from teams_app.models import Team
from reports_app.forms import ReportFilterForm
from reports_app.models import (
    Medical, Transition, Scouting, Performance,
    IndividualActionPlan, Mesocycle, FitnessPlan
)
from .report_filters import filter_queryset_by_period

SECTION_MAP = {
    'Medical': (Medical, 'date'),
    'Transition': (Transition, 'date'),
    'Scouting': (Scouting, 'date'),
    'Performance': (Performance, 'date'),
    'IAP': (IndividualActionPlan, 'date'),
    'Mesocycle': (Mesocycle, 'start_date'),
    'Fitness': (FitnessPlan, 'date'),
}


def team_reports_dashboard(request, team_id):
    """
    Displays the reports dashboard for a specific team, 
    including filters, sticky navbar, and export buttons.
    """
    team = get_object_or_404(Team, id=team_id)

    # Pre-fill the filter form with the selected team
    form = ReportFilterForm(request.GET or None, initial={'team': team})

    section_data = {}

    if form.is_valid():
        period = form.cleaned_data.get('period')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        for key, (model, date_field) in SECTION_MAP.items():
            qs = model.objects.all()

            # Filter by the current team
            if hasattr(model, 'squad'):
                qs = qs.filter(squad=team)
            elif hasattr(model, 'team'):
                qs = qs.filter(team=team)

            # Filter by time period if chosen
            if period:
                qs = filter_queryset_by_period(qs, period, start_date, end_date, date_field)

            section_data[key.lower()] = qs

    context = {
        'team': team,
        'form': form,
        'team_id': team.id,
        **section_data,
    }

    return render(request, 'reports_app/daily_report_templates/reports_dashboard.html', context)




