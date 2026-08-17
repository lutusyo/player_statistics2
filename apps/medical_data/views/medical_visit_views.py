from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from apps.medical_data.forms.medical_filter_form import (MedicalFilterForm,)
from apps.medical_data.forms.medical_visit_form import MedicalVisitForm
from apps.medical_data.models.medical_visit import (MedicalVisit,)

from django.http import JsonResponse
from version1.players_app.models import Player

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone

def medical_visit_list(request):

    queryset = (
        MedicalVisit.objects
        .select_related("team", "player", "created_by")
        .prefetch_related("attachments", "follow_ups")
    )

    form = MedicalFilterForm(request.GET or None)

    if form.is_valid():

        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        team = form.cleaned_data.get("team")
        player = form.cleaned_data.get("player")
        visit_type = form.cleaned_data.get("visit_type")
        main_complaint = form.cleaned_data.get("main_complaint")
        availability_status = form.cleaned_data.get("availability_status")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        if team:
            queryset = queryset.filter(team=team)

        if player:
            queryset = queryset.filter(player=player)

        if visit_type:
            queryset = queryset.filter(
                visit_type=visit_type
            )

        if main_complaint:
            queryset = queryset.filter(
                main_complaint=main_complaint
            )

        if availability_status:
            queryset = queryset.filter(
                availability_status=availability_status
            )

    # -----------------------------
    # STATISTICS
    # -----------------------------

    total_records = queryset.count()

    new_injuries = queryset.filter(
        visit_type="new_injury"
    ).count()

    regular_checkups = queryset.filter(
        visit_type="regular_checkup"
    ).count()

    unavailable = queryset.filter(
        availability_status="unavailable"
    ).count()

    restricted = queryset.filter(
        availability_status="restricted"
    ).count()

    available = queryset.filter(
        availability_status="available"
    ).count()

    # -----------------------------
    # PAGINATION
    # -----------------------------






    paginator = Paginator(queryset, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_string = request.GET.copy()

    if "page" in query_string:
        query_string.pop("page")

    query_string = query_string.urlencode()


    context = {
        "page_title": "Medical Records",
        "medical_visits": page_obj,
        "page_obj": page_obj,
        "filter_form": form,
        "total_records": total_records,
        "new_injuries": new_injuries,
        "regular_checkups": regular_checkups,
        "available": available,
        "restricted": restricted,
        "unavailable": unavailable,
        "query_string": query_string,
    }
    return render(request, "medical_data/medical_visit/medical_visit_list.html", context,)



















def medical_visit_create(request):
    form = MedicalVisitForm(request.POST or None, request.FILES or None,)

    if form.is_valid():
        visit = form.save(commit=False)
        visit.created_by = request.user
        visit.save()

        messages.success(request,"Medical record saved successfully.",)
        return redirect( "medical_data:medical_visit_detail",visit.pk,)

    return render(request,"medical_data/medical_visit/medical_visit_form.html",
        {"form": form,"page_title": "New Medical Visit",},)

def medical_visit_detail(request,pk,):
    visit = (MedicalVisit.objects.select_related("player","team","created_by",)
        .prefetch_related("attachments","follow_ups",)
        .get(pk=pk))
    
    context = {"medical_visit": visit,}
    return render(request,"medical_data/medical_visit/medical_visit_detail.html",context,)

def medical_visit_delete(request,pk,):
    visit = get_object_or_404(MedicalVisit,pk=pk,)

    if request.method == "POST":
        visit.delete()
        messages.success(request,"Medical visit deleted.",)
        return redirect("medical_data:medical_visit_list")
    
    context = {"medical_visit": visit,}
    return render(request,"medical_data/medical_visit/medical_visit_delete.html",context,)

def medical_visit_update(request, pk):
    medical_visit = get_object_or_404(MedicalVisit,pk=pk,)
    form = MedicalVisitForm(request.POST or None,request.FILES or None,instance=medical_visit,)

    if form.is_valid():
        form.save()

        messages.success(request,"Medical visit updated successfully.")
        return redirect("medical_data:medical_visit_detail",pk=medical_visit.pk,)

    context = {
        "page_title": "Edit Medical Visit",
        "form": form,
        "medical_visit": medical_visit,}
    return render(request,"medical_data/medical_visit/medical_visit_form.html",context,)