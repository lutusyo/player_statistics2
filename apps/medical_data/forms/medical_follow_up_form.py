from django import forms

from apps.medical_data.models.medical_follow_up import MedicalFollowUp


class MedicalFollowUpForm(forms.ModelForm):
    class Meta:

        model = MedicalFollowUp
        fields = [
            "review_date",
            "notes",
            "status",
        ]

        widgets = {

            "review_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                }
            ),

            "completed": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }