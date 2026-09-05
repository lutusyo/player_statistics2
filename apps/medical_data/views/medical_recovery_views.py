from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import (get_object_or_404,redirect, render,)
from django.utils import timezone
from apps.medical_data.forms import ( MedicalRecoveryPlanForm, MedicalRecoveryDayForm, MedicalRecoveryCoachForm, )
from apps.medical_data.models import (MedicalVisit, MedicalRecoveryPlan, MedicalRecoveryDay,)
from apps.medical_data.models.medical_recovery_day import (RecoveryDayStatus,)

from apps.medical_data.services.recovery import (create_recovery_days, extend_recovery_plan, complete_recovery_plan, cancel_recovery_plan,)

@login_required
def recovery_plan_create(request, visit_id):

    visit = get_object_or_404(MedicalVisit,pk=visit_id,)
    if hasattr(visit, "recovery_plan"):
        messages.warning(request,"This medical visit already has a recovery plan.",)
        return redirect("medical_data:recovery_plan_detail",pk=visit.recovery_plan.pk,)

    if request.method == "POST":
        form = MedicalRecoveryPlanForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                plan = form.save(commit=False)
                plan.visit = visit
                plan.doctor = request.user
                plan.save()

                create_recovery_days(plan)
            messages.success(request,"Recovery plan created successfully.",)
            return redirect("medical_data:recovery_plan_detail",pk=plan.pk,)

    else:

        form = MedicalRecoveryPlanForm( initial={"start_date": visit.date})
    
    context = {
            "form": form,
            "visit": visit,
            "page_title": "Create Recovery Plan",
    }
    return render(request, "medical_data/recovery_plan_form.html", context,)


@login_required
def recovery_plan_detail(request, pk):

    plan = get_object_or_404(MedicalRecoveryPlan.objects
        .select_related("visit__player", "visit__team","doctor",)
        .prefetch_related("daily_programs",),
        pk=pk,
    )

    today = timezone.localdate()
    today_program = (plan.daily_programs.filter(date=today).first())

    return render(request,"medical_data/recovery_plan_detail.html",
        {
            "plan": plan,
            "today": today,
            "today_program": today_program,
            "page_title": "Recovery Plan",
        },
    )

@login_required
def recovery_day_update(request, pk):

    day = get_object_or_404(MedicalRecoveryDay.objects
        .select_related(
            "recovery_plan__visit__player",
            "recovery_plan__visit__team",
        ),
        pk=pk,
    )

    if request.method == "POST":

        form = MedicalRecoveryDayForm(request.POST, instance=day,)
        if form.is_valid():
            form.save()

            messages.success(request,"Daily recovery program updated.",)
            return redirect("medical_data:recovery_plan_detail", pk=day.recovery_plan.pk,)

    else:

        form = MedicalRecoveryDayForm(instance=day)

    return render(request, "medical_data/recovery_day_form.html",
        {
            "form": form,
            "day": day,
            "page_title": (
                f"Day {day.day_number} Program"
            ),
        },
    )




@login_required
def recovery_plan_extend(request, pk):

    plan = get_object_or_404(MedicalRecoveryPlan,pk=pk,)
    if request.method == "POST":
        try:
            new_days = int(
                request.POST.get(
                    "planned_days",
                    0,
                )
            )
        except (TypeError, ValueError):
            new_days = 0

        if new_days <= plan.planned_days:

            messages.error(request,"New recovery period must be longer than the current period.",)

        else:

            success = extend_recovery_plan(plan, new_days,)
            if success:
                messages.success(request, f"Recovery plan extended to {new_days} days.",)
                return redirect("medical_data:recovery_plan_detail",pk=plan.pk,)

            messages.error(request,"This recovery plan cannot be extended.",)

    return render(request, "medical_data/recovery_plan_extend.html",
        {
            "plan": plan,
            "page_title": "Extend Recovery Plan",
        },
    )


@login_required
def recovery_day_complete(request, pk):
    day = get_object_or_404(MedicalRecoveryDay.objects.select_related("recovery_plan"),pk=pk,)
    if request.method == "POST":
        form = MedicalRecoveryCoachForm(request.POST, instance=day,)
        if form.is_valid():
            day = form.save(commit=False)
            day.status = RecoveryDayStatus.COMPLETED
            day.completed_at = timezone.now()
            day.save()
            messages.success(request,f"Day {day.day_number} marked as completed.",)
    return redirect("medical_data:medical_coach_dashboard")


@login_required
def recovery_plan_complete(request, pk):

    plan = get_object_or_404(MedicalRecoveryPlan,pk=pk,)
    if request.method == "POST":
        recovery_date = request.POST.get("recovery_date")
        if recovery_date:
            from datetime import datetime
            recovery_date = datetime.strptime(
                recovery_date,
                "%Y-%m-%d",
            ).date()

        else:
            recovery_date = timezone.localdate()

        complete_recovery_plan(plan,recovery_date,)
        messages.success(request,"Player recovery has been completed. Remaining days were cancelled.",)
        return redirect("medical_data:recovery_plan_detail",pk=plan.pk,)


    return render(request,"medical_data/recovery_plan_complete.html",
        {
            "plan": plan,
            "today": timezone.localdate(),
            "page_title": "Complete Recovery",
        },
    )


@login_required
def recovery_plan_cancel(request, pk):

    plan = get_object_or_404(MedicalRecoveryPlan,pk=pk,)
    if request.method == "POST":
        cancel_recovery_plan(plan)
        messages.success(request,"Recovery plan cancelled.",)

        return redirect("medical_data:recovery_plan_detail",pk=plan.pk,)

    return render(request, "medical_data/recovery_plan_cancel.html",
        {
            "plan": plan,
            "page_title": "Cancel Recovery Plan",
        },
    )


