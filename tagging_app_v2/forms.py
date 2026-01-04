# tagging_app_v2/forms.py

from django import forms
from lineup_app.models import MatchLineup
from tagging_app_v2.constants import BALL_ACTION_CHOICES


class PassEventV2Form(forms.Form):
    actor = forms.ModelChoiceField(queryset=MatchLineup.objects.none())
    action_type = forms.ChoiceField(choices=BALL_ACTION_CHOICES)
    receiver = forms.ModelChoiceField(
        queryset=MatchLineup.objects.none(),
        required=True
    )
    timestamp = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        match = kwargs.pop("match")
        super().__init__(*args, **kwargs)

        self.fields["actor"].queryset = MatchLineup.objects.filter(match=match)
        self.fields["receiver"].queryset = MatchLineup.objects.filter(match=match)
