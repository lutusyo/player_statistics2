from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from apps.medical_data.models.medical_visit import MedicalVisit
from apps.medical_data.models.medical_follow_up import  MedicalFollowUp

@login_required
def medical_dashboard(request):

    today = timezone.localdate()
    visits = MedicalVisit.objects.all()
    total_records = visits.count()

    new_injuries = visits.filter(visit_type="new_injury").count()
    regular_checkups = visits.filter(visit_type="regular_checkup").count()
    available_players = visits.filter(availability_status="available").count()
    restricted_players = visits.filter(availability_status="restricted").count()
    unavailable_players = visits.filter(availability_status="unavailable").count()

    # INJURIES BY COMPLAINT
    complaint_data = list(visits
        .filter(visit_type="new_injury")
        .values("main_complaint")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    complaint_labels = [
        dict(
            MedicalVisit._meta.get_field("main_complaint").choices
        ).get(item["main_complaint"], item["main_complaint"])
        for item in complaint_data
    ]

    complaint_values = [
        item["total"]
        for item in complaint_data
    ]

    # INJURIES BY TEAM
    team_data = list(visits.filter(visit_type="new_injury").values("team__name").annotate(total=Count("id")).order_by("-total"))
    team_labels = [
        item["team__name"]
        for item in team_data
    ]

    team_values = [
        item["total"]
        for item in team_data
    ]

    # VISITS OVER LAST 30 DAYS
    start_date = today - timedelta(days=29)
    daily_data = list(visits
        .filter(
            date__gte=start_date,
            date__lte=today,
        )
        .values("date")
        .annotate(total=Count("id"))
        .order_by("date")
    )

    daily_lookup = {
        item["date"]: item["total"]
        for item in daily_data
    }

    date_labels = []
    date_values = []
    current_date = start_date
    while current_date <= today:

        date_labels.append(current_date.strftime("%d %b"))
        date_values.append(daily_lookup.get(current_date, 0))
        current_date += timedelta(days=1)

    # PENDING FOLLOW-UPS
    pending_followups = (
        MedicalFollowUp.objects
        .filter(status=False,review_date__gte=today,)
        .select_related("visit__player","visit__team",)
        .order_by("review_date")
    )

    # OVERDUE FOLLOW-UPS

    overdue_followups = (
        MedicalFollowUp.objects
        .filter(status=False,review_date__lt=today,)
        .select_related("visit__player","visit__team",)
        .order_by("review_date")
    )

    # UPCOMING RETURN DATES
    upcoming_returns = (
        visits
        .filter(expected_return_date__gte=today,)
        .select_related("player","team",)
        .order_by("expected_return_date")[:10]
    )

    context = {

        "page_title": "Medical Dashboard",
        "total_records": total_records,
        "new_injuries": new_injuries,
        "regular_checkups": regular_checkups,
        "available_players": available_players,
        "restricted_players": restricted_players,
        "unavailable_players": unavailable_players,
        "complaint_labels": complaint_labels,
        "complaint_values": complaint_values,
        "team_labels": team_labels,
        "team_values": team_values,
        "date_labels": date_labels,
        "date_values": date_values,
        "pending_followups": pending_followups,
        "overdue_followups": overdue_followups,
        "upcoming_returns": upcoming_returns,

    }

    return render(request,"medical_data/medical_dashboard.html",context,)