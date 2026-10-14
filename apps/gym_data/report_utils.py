from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models import Sum, Count

from .models import GroupExercise


def get_report_queryset():
    """
    Base queryset for all gym reports.
    """

    return (
        GroupExercise.objects
        .select_related(
            "gym_group",
            "gym_group__gym_session",
            "gym_group__gym_session__team",
            "gym_group__gym_type",
            "exercise",
            "exercise__category",
        )
        .prefetch_related(
            "gym_group__players",
        )
        .order_by(
            "-gym_group__gym_session__date",
            "gym_group__gym_session__team__name",
            "gym_group__gym_type__name",
            "exercise__name",
        )
    )


def apply_report_filters(queryset, form):
    """
    Apply common gym report filters.
    """

    if not form.is_valid():
        return queryset

    team = form.cleaned_data.get("team")
    player = form.cleaned_data.get("player")
    start_date = form.cleaned_data.get("start_date")
    end_date = form.cleaned_data.get("end_date")
    gym_type = form.cleaned_data.get("gym_type")
    category = form.cleaned_data.get("category")
    exercise = form.cleaned_data.get("exercise")

    if team:
        queryset = queryset.filter(
            gym_group__gym_session__team=team
        )

    if player:
        queryset = queryset.filter(
            gym_group__players=player
        )

    if start_date:
        queryset = queryset.filter(
            gym_group__gym_session__date__gte=start_date
        )

    if end_date:
        queryset = queryset.filter(
            gym_group__gym_session__date__lte=end_date
        )

    if gym_type:
        queryset = queryset.filter(
            gym_group__gym_type=gym_type
        )

    if category:
        queryset = queryset.filter(
            exercise__category=category
        )

    if exercise:
        queryset = queryset.filter(
            exercise=exercise
        )

    return queryset


def add_volume(queryset):
    """
    Calculate training volume.

    Volume = weight × sets × reps
    """

    return queryset.annotate(
        volume=ExpressionWrapper(
            F("weight_kg") * F("sets") * F("reps"),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2,
            ),
        )
    )