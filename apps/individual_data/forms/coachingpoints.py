from django import forms
from apps.individual_data.models.data_collection import (CoachingPoint, PlayerInterventionCoachingPoint,)
from django.db.models import Q


class InterventionCoachingPointForm(forms.ModelForm):
    class Meta:
        model = PlayerInterventionCoachingPoint
        fields = ["coaching_point", "achieved", "note"]
        widgets = {
            "coaching_point": forms.Select(
                attrs={"class": "form-select"}
            ),
            "achieved": forms.CheckboxInput(attrs={"class": "form-check-input"}),

            "note": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Optional note",
                }
            ),
        }

    def __init__(self, *args, objective=None, position=None, **kwargs):
        super().__init__(*args, **kwargs)

        points = CoachingPoint.objects.filter(is_active=True)

        if objective:
            points = points.filter(objective=objective)

        if position:
            points = points.filter(
                Q(position=position)
                | Q(position__isnull=True)
                | Q(position="")
            )
        else:
            points = points.filter(
                Q(position__isnull=True)
                | Q(position="")
            )
        self.fields["coaching_point"].queryset = points.order_by("order", "name")
