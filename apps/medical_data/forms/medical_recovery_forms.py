from datetime import timedelta
from django import forms
from apps.medical_data.models import (MedicalRecoveryPlan,MedicalRecoveryDay, )

class MedicalRecoveryPlanForm(forms.ModelForm):

    class Meta:
        model = MedicalRecoveryPlan
        fields = ["start_date", "planned_days", "recovery_notes",]
        widgets = {

            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "planned_days": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "e.g. 14",
                }
            ),

            "recovery_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": (
                        "General recovery instructions..."
                    ),
                }
            ),

        }

    def clean_planned_days(self):
        days = self.cleaned_data["planned_days"]
        if days < 1:
            raise forms.ValidationError("Recovery period must be at least 1 day.")

        if days > 365:
            raise forms.ValidationError("Recovery period cannot exceed 365 days.")

        return days


class MedicalRecoveryDayForm(forms.ModelForm):

    class Meta:
        model = MedicalRecoveryDay
        fields = ["focus_point", "activities",]

        widgets = {

            "focus_point": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": (
                        "e.g. Mobility and activation"
                    ),
                }
            ),

            "activities": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": (
                        "Describe exactly what the player "
                        "should do..."
                    ),
                }
            ),

        }