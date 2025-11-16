from django import forms
from perfomance_rating_app.models import StaffPlayerRating

class SingleRatingForm(forms.ModelForm):
    class Meta:
        model = StaffPlayerRating
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 0, "max": 10, "step": 0.1, "required": True}),
            "comment": forms.Textarea(attrs={"rows": 2, "placeholder": "optional Comment"}),
        }