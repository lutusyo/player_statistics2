from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django import forms
from apps.medical_data.models import (MedicalVisit,MedicalFollowUp,)


class MedicalFollowUpForm(forms.ModelForm):

    class Meta:
        model = MedicalFollowUp
        fields = ["review_date","notes","status",]
        widgets = {

            "review_date": forms.DateInput(
                attrs={"type": "date","class": "form-control",}
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                }
            ),

            "completed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


def medical_follow_up_create(request, visit_id):
    medical_visit = get_object_or_404(MedicalVisit,pk=visit_id,)

    if request.method == "POST":

        form = MedicalFollowUpForm(request.POST)

        if form.is_valid():

            follow_up = form.save(commit=False)
            follow_up.visit = medical_visit
            follow_up.doctor = request.user
            follow_up.save()

            messages.success(request,"Follow up added successfully.")

            return redirect("medical_data:medical_visit_detail",pk=medical_visit.pk,)

    else:

        form = MedicalFollowUpForm()

    context =         {
            "form": form,
            "medical_visit": medical_visit,
        }
    return render(request,"medical_data/medical_follow_up/follow_up_form.html", context)


def medical_follow_up_delete(request, pk):

    follow_up = get_object_or_404(MedicalFollowUp,pk=pk,)
    visit_id = follow_up.visit.pk

    if request.method == "POST":

        follow_up.delete()

        messages.success(request,"Follow up deleted.")

        return redirect("medical_data:medical_visit_detail",pk=visit_id,)

    return render(request,"medical_data/medical_follow_up/follow_up_delete.html",
        {
            "follow_up": follow_up,
        }
    )