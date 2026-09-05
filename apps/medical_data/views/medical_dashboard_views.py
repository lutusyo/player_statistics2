from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone

from apps.medical_data.models import MedicalVisit
from apps.medical_data.models.medical_follow_up import MedicalFollowUp
from apps.medical_data.models.medical_recovery_plan import (
    MedicalRecoveryPlan,
    RecoveryPlanStatus,
)


@login_required
def medical_dashboard(request):

    today = timezone.localdate()

    # ============================================================
    # BASE QUERYSET
    # ============================================================

    visits = MedicalVisit.objects.all()

    # ============================================================
    # BASIC VISIT STATISTICS
    # ============================================================

    total_records = visits.count()

    visits_today = visits.filter(
        date=today
    ).count()

    visits_this_month = visits.filter(
        date__year=today.year,
        date__month=today.month,
    ).count()

    new_injuries = visits.filter(
        visit_type="new_injury"
    ).count()

    regular_checkups = visits.filter(
        visit_type="regular_checkup"
    ).count()

    # ============================================================
    # AVAILABILITY STATISTICS
    # ============================================================

    available_players = visits.filter(
        availability_status="available"
    ).count()

    restricted_players = visits.filter(
        availability_status="restricted"
    ).count()

    unavailable_players = visits.filter(
        availability_status="unavailable"
    ).count()

    # ============================================================
    # RECOVERY PLAN STATISTICS
    # ============================================================

    active_recovery_plans = MedicalRecoveryPlan.objects.filter(
        status__in=[
            RecoveryPlanStatus.ACTIVE,
            RecoveryPlanStatus.EXTENDED,
        ]
    ).count()

    completed_recovery_plans = MedicalRecoveryPlan.objects.filter(
        status=RecoveryPlanStatus.COMPLETED
    ).count()

    cancelled_recovery_plans = MedicalRecoveryPlan.objects.filter(
        status=RecoveryPlanStatus.CANCELLED
    ).count()

    # ============================================================
    # INJURIES BY COMPLAINT
    # ============================================================

    complaint_data = list(
        visits
        .filter(
            visit_type="new_injury"
        )
        .values("main_complaint")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    complaint_choices = dict(
        MedicalVisit._meta.get_field(
            "main_complaint"
        ).choices
    )

    complaint_labels = [
        complaint_choices.get(
            item["main_complaint"],
            item["main_complaint"]
        )
        for item in complaint_data
    ]

    complaint_values = [
        item["total"]
        for item in complaint_data
    ]

    # ============================================================
    # INJURIES BY TEAM
    # ============================================================

    team_data = list(
        visits
        .filter(
            visit_type="new_injury"
        )
        .values("team__name")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    team_labels = [
        item["team__name"]
        for item in team_data
    ]

    team_values = [
        item["total"]
        for item in team_data
    ]

    # ============================================================
    # AVAILABILITY STATISTICS FOR CHART
    # ============================================================

    availability_stats = (
        visits
        .values("availability_status")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # ============================================================
    # VISITS OVER LAST 30 DAYS
    # ============================================================

    start_date = today - timedelta(days=29)

    daily_data = list(
        visits
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

        date_labels.append(
            current_date.strftime("%d %b")
        )

        date_values.append(
            daily_lookup.get(current_date, 0)
        )

        current_date += timedelta(days=1)

    # ============================================================
    # PENDING FOLLOW-UPS
    # ============================================================

    pending_followups = (
        MedicalFollowUp.objects
        .filter(
            status=False,
            review_date__gte=today,
        )
        .select_related(
            "visit__player",
            "visit__team",
        )
        .order_by("review_date")
    )

    # ============================================================
    # OVERDUE FOLLOW-UPS
    # ============================================================

    overdue_followups = (
        MedicalFollowUp.objects
        .filter(
            status=False,
            review_date__lt=today,
        )
        .select_related(
            "visit__player",
            "visit__team",
        )
        .order_by("review_date")
    )

    # ============================================================
    # UPCOMING RETURN DATES
    # ============================================================

    upcoming_returns = (
        visits
        .filter(
            expected_return_date__gte=today,
        )
        .select_related(
            "player",
            "team",
        )
        .order_by("expected_return_date")[:10]
    )

    # ============================================================
    # RECENT MEDICAL VISITS
    # ============================================================

    recent_visits = (
        visits
        .select_related(
            "player",
            "team",
        )
        .order_by(
            "-date",
            "-created_at",
        )[:10]
    )

    # ============================================================
    # CONTEXT
    # ============================================================

    context = {

        "page_title": "Medical Dashboard",
        "today": today,

        # Basic statistics
        "total_records": total_records,
        "visits_today": visits_today,
        "visits_this_month": visits_this_month,
        "new_injuries": new_injuries,
        "regular_checkups": regular_checkups,

        # Availability
        "available_players": available_players,
        "restricted_players": restricted_players,
        "unavailable_players": unavailable_players,
        "availability_stats": availability_stats,

        # Recovery plans
        "active_recovery_plans": active_recovery_plans,
        "completed_recovery_plans": completed_recovery_plans,
        "cancelled_recovery_plans": cancelled_recovery_plans,

        # Injury charts
        "complaint_data": complaint_data,
        "complaint_labels": complaint_labels,
        "complaint_values": complaint_values,

        "team_labels": team_labels,
        "team_values": team_values,

        # 30-day chart
        "date_labels": date_labels,
        "date_values": date_values,

        # Follow-ups
        "pending_followups": pending_followups,
        "overdue_followups": overdue_followups,

        # Return dates
        "upcoming_returns": upcoming_returns,

        # Recent visits
        "recent_visits": recent_visits,
    }

    return render(
        request,
        "medical_data/dashboard.html",
        context,
    )