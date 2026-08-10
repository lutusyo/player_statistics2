from django import forms

from apps.medical_data.models.medical_attachment import MedicalAttachment


class MedicalAttachmentForm(forms.ModelForm):

    class Meta:
        model = MedicalAttachment
        fields = ["file","description",]
        widgets = {
            "file": forms.ClearableFileInput(
                attrs={"class": "form-control",}
            ),

            "description": forms.TextInput(
                attrs={"class": "form-control",
                    "placeholder": "Example: MRI Right Knee",}
            ),

        }