from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.medical_data.models import (
    MedicalRecoveryDay,
    MedicalRecoveryPlan,
)
from apps.medical_data.models.medical_recovery_day import (
    RecoveryDayStatus,
)
from apps.medical_data.models.medical_recovery_plan import (
    RecoveryPlanStatus,
)


@transaction.atomic
def create_recovery_days(plan):

    existing_days = set(
        plan.daily_programs.values_list(
            "day_number",
            flat=True,
        )
    )

    days = []

    for day_number in range(
        1,
        plan.planned_days + 1,
    ):

        if day_number in existing_days:
            continue

        program_date = (
            plan.start_date
            + timedelta(days=day_number - 1)
        )

        days.append(
            MedicalRecoveryDay(
                recovery_plan=plan,
                day_number=day_number,
                date=program_date,
                focus_point="",
                activities="",
                status=RecoveryDayStatus.PLANNED,
            )
        )

    if days:
        MedicalRecoveryDay.objects.bulk_create(days)

    return days


@transaction.atomic
def extend_recovery_plan(plan, new_total_days):

    if new_total_days <= plan.planned_days:
        return False

    if plan.status in [
        RecoveryPlanStatus.COMPLETED,
        RecoveryPlanStatus.CANCELLED,
    ]:
        return False

    plan.planned_days = new_total_days

    plan.expected_end_date = (
        plan.start_date
        + timedelta(days=new_total_days - 1)
    )

    plan.status = RecoveryPlanStatus.EXTENDED

    plan.save()

    create_recovery_days(plan)

    return True


@transaction.atomic
def complete_recovery_plan(
    plan,
    recovery_date=None,
):

    recovery_date = (
        recovery_date
        or timezone.localdate()
    )

    plan.actual_recovery_date = recovery_date
    plan.status = RecoveryPlanStatus.COMPLETED

    plan.save()

    plan.daily_programs.filter(
        date__gt=recovery_date,
        status=RecoveryDayStatus.PLANNED,
    ).update(status=RecoveryDayStatus.CANCELLED)

    return plan


@transaction.atomic
def cancel_recovery_plan(plan):
    plan.status = RecoveryPlanStatus.CANCELLED
    plan.save()
    plan.daily_programs.filter(status=RecoveryDayStatus.PLANNED).update(status=RecoveryDayStatus.CANCELLED)

    return plan