
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Analysis
from django.db import transaction

from .models import (Analysis, AnalysisPeriod, AnalysisTeam, AnalysisPeriodTeam,)

from .forms import (
    AnalysisForm,
    TeamSelectionForm,
    AnalysisPeriodFormSet,
)

from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import (
    Analysis,
    AnalysisPeriod,
    AnalysisTeam,
    AnalysisPeriodTeam,
    AnalysisRun,
)

from .services.report_builder import build_analysis_report

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import Analysis, AnalysisRun
from .services.excel_export import export_analysis_excel
from .services.pdf_export import export_analysis_pdf

from .services.pptx_export import export_analysis_pptx

@login_required
def dashboard(request):
    analyses = Analysis.objects.filter(
        created_by=request.user
    ).prefetch_related("periods", "age_groups")

    context = {
        "analyses": analyses,
        "total_analyses": analyses.count(),
    }
    return render(request, "performance_analysis/dashboard.html", context)


@login_required
def create_analysis(request):

    if request.method == "POST":
        analysis_form = AnalysisForm(request.POST)
        team_form = TeamSelectionForm(request.POST)

        period_formset = AnalysisPeriodFormSet(
            request.POST,
            prefix="periods",
        )

        if (
            analysis_form.is_valid()
            and team_form.is_valid()
            and period_formset.is_valid()
        ):

            comparison_mode = analysis_form.cleaned_data[
                "comparison_mode"
            ]

            valid_periods = [
                form for form in period_formset.forms
                if form.cleaned_data
                and not form.cleaned_data.get("DELETE", False)
            ]

            has_valid_teams = True

            if comparison_mode == Analysis.ComparisonMode.SAME_TEAMS:

                if not team_form.cleaned_data["teams"].exists():
                    team_form.add_error(
                        "teams",
                        "Select at least one academy team."
                    )
                    has_valid_teams = False

            else:

                for form in valid_periods:
                    if not form.cleaned_data.get("teams"):
                        form.add_error(
                            "teams",
                            "Select at least one team for this period."
                        )
                        has_valid_teams = False

            if has_valid_teams:

                with transaction.atomic():

                    analysis = analysis_form.save(commit=False)
                    analysis.created_by = request.user
                    analysis.save()

                    analysis_form.save_m2m()

                    # Save reporting periods
                    for order, form in enumerate(valid_periods, start=1):

                        period = AnalysisPeriod.objects.create(
                            analysis=analysis,
                            name=form.cleaned_data["name"],
                            start_date=form.cleaned_data["start_date"],
                            end_date=form.cleaned_data["end_date"],
                            order=order,
                        )

                        # Different teams for each period
                        if comparison_mode == Analysis.ComparisonMode.PER_PERIOD:

                            selected_teams = form.cleaned_data["teams"]

                            AnalysisPeriodTeam.objects.bulk_create([
                                AnalysisPeriodTeam(
                                    period=period,
                                    team=team,
                                )
                                for team in selected_teams
                            ])

                    # Same teams across all periods
                    if comparison_mode == Analysis.ComparisonMode.SAME_TEAMS:

                        selected_teams = team_form.cleaned_data["teams"]

                        AnalysisTeam.objects.bulk_create([
                            AnalysisTeam(
                                analysis=analysis,
                                team=team,
                            )
                            for team in selected_teams
                        ])

                return redirect(
                    "performance_analysis:analysis_detail",
                    pk=analysis.pk,
                )

    else:
        analysis_form = AnalysisForm()
        team_form = TeamSelectionForm()

        period_formset = AnalysisPeriodFormSet(
            prefix="periods"
        )

    context = {
        "analysis_form": analysis_form,
        "team_form": team_form,
        "period_formset": period_formset,
    }

    return render(
        request,
        "performance_analysis/create_analysis.html",
        context,
    )






@login_required
def analysis_detail(request, pk):
    analysis = get_object_or_404(
        Analysis.objects.prefetch_related(
            "periods",
            "age_groups",
            "selected_teams__team",
            "periods__selected_teams__team",
        ),
        pk=pk,
        created_by=request.user,
    )

    latest_run = analysis.runs.order_by("-generated_at").first()

    report = None

    if latest_run and latest_run.status == "COMPLETED":
        report = latest_run.results_snapshot

    context = {
        "analysis": analysis,
        "latest_run": latest_run,
        "report": report,
    }

    return render(request, "performance_analysis/analysis_detail.html", context,)




@login_required
@require_POST
def generate_analysis(request, pk):
    analysis = get_object_or_404(
        Analysis,
        pk=pk,
        created_by=request.user,
    )

    run = AnalysisRun.objects.create(
        analysis=analysis,
        generated_by=request.user,
        status="PENDING",
        filters_snapshot={
            "analysis_type": analysis.analysis_type,
            "comparison_mode": analysis.comparison_mode,
        },
    )

    try:
        report = build_analysis_report(analysis)

        run.results_snapshot = report
        run.status = "COMPLETED"
        run.save(update_fields=[
            "results_snapshot",
            "status",
        ])

        messages.success(
            request,
            "Performance analysis generated successfully.",
        )

    except Exception as error:
        run.status = "FAILED"
        run.error_message = str(error)
        run.save(update_fields=[
            "status",
            "error_message",
        ])

        messages.error(
            request,
            "Analysis generation failed. Please check the error and try again.",
        )

    return redirect(
        "performance_analysis:analysis_detail",
        pk=analysis.pk,
    )




@login_required
def export_excel(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)

    # Prevent another user from exporting a private analysis.
    if analysis.created_by_id and analysis.created_by_id != request.user.id:
        raise Http404

    run = analysis.runs.filter(
        status="COMPLETED"
    ).order_by("-generated_at").first()

    if not run:
        raise Http404("No completed analysis report is available.")

    return export_analysis_excel(run)


@login_required
def export_pdf(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)

    if analysis.created_by_id and analysis.created_by_id != request.user.id:
        raise Http404

    run = analysis.runs.filter(
        status="COMPLETED"
    ).order_by("-generated_at").first()

    if not run:
        raise Http404("No completed analysis report is available.")

    return export_analysis_pdf(run)

@login_required
def export_pptx(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)

    if analysis.created_by_id and analysis.created_by_id != request.user.id:
        raise Http404

    run = analysis.runs.filter(
        status="COMPLETED"
    ).order_by("-generated_at").first()

    if not run:
        raise Http404("No completed analysis report is available.")

    return export_analysis_pptx(run)