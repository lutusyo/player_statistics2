from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render
from django.utils import timezone

from apps.medical_data.models import (MedicalRecoveryDay, MedicalRecoveryPlan,)
from apps.medical_data.models.medical_recovery_day import (RecoveryDayStatus,)
from apps.medical_data.models.medical_recovery_plan import (RecoveryPlanStatus,)


@login_required
def medical_coach_dashboard(request):
    today = timezone.localdate()
    today_programs = (MedicalRecoveryDay.objects.filter(date=today, status=RecoveryDayStatus.PLANNED,
            recovery_plan__status__in=[RecoveryPlanStatus.ACTIVE, RecoveryPlanStatus.EXTENDED,],
        )
        .select_related("recovery_plan", "recovery_plan__visit",
            "recovery_plan__visit__player","recovery_plan__visit__team",
        ).order_by("recovery_plan__visit__team", "recovery_plan__visit__player",)
    )

    completed_today = (MedicalRecoveryDay.objects.filter(date=today,status=RecoveryDayStatus.COMPLETED,)
        .select_related("recovery_plan__visit__player", "recovery_plan__visit__team",)
    )

    total_today = ( today_programs.count() + completed_today.count() )

    context = {
        "today": today,
        "today_programs": today_programs,
        "completed_today": completed_today,
        "total_today": total_today,
        "completed_count": completed_today.count(),
        "remaining_count": today_programs.count(),
        "page_title": "Special Coach Dashboard",
    }

    return render(request,"medical_data/medical_coach_dashboard.html",context,)