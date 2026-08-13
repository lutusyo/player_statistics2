from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from apps.medical_data.models.medical_visit import (MedicalVisit,)
from apps.medical_data.models.medical_attachment import MedicalAttachment
from django import forms
from apps.medical_data.forms.medical_attachment_form import MedicalAttachmentForm



def medical_attachment_create(request, visit_id):
    medical_visit = get_object_or_404(MedicalVisit,pk=visit_id,)
    if request.method == "POST":

        form = MedicalAttachmentForm(request.POST,request.FILES,)

        if form.is_valid():

            attachment = form.save(commit=False)
            attachment.visit = medical_visit
            attachment.save()

            messages.success(request,"Attachment uploaded successfully.")
            return redirect("medical_data:medical_visit_detail",pk=medical_visit.pk,)


    else:
        form = MedicalAttachmentForm()

    context = {"form": form,
        "medical_visit": medical_visit,}
    return render(request,"medical_data/medical_attachment/attachment_form.html", context)

def medical_attachment_delete(request, pk):
    attachment = get_object_or_404(MedicalAttachment, pk=pk)
    medical_visit = attachment.visit

    if request.method == "POST":
        attachment.file.delete()
        attachment.delete()

        messages.success(request, "Attachment deleted.")
        return redirect(
            "medical_data:medical_visit_detail",
            pk=medical_visit.pk
        )

    context = {
        "attachment": attachment,
        "medical_visit": medical_visit,
    }

    return render(
        request,
        "medical_data/medical_attachment/attachment_delete.html",
        context
    )