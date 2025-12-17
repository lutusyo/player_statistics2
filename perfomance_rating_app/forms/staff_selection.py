from django import forms
from teams_app.models import StaffMember

class SendRatingLinksForm(forms.Form):
    staff = forms.ModelMultipleChoiceField(
        queryset=StaffMember.objects.none(),  # will set dynamically
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Staff"
    )

    def __init__(self, *args, **kwargs):
        staff_queryset = kwargs.pop('staff_queryset', None)  # get custom queryset
        super().__init__(*args, **kwargs)
        if staff_queryset is not None:
            self.fields['staff'].queryset = staff_queryset
