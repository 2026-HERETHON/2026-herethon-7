from django import forms
from .models import Proposal

class ProposalForm(forms.ModelForm):

    class Meta:
        model = Proposal

        fields = [
            "give_talent",
            "need_talent",
            "title",
            "goal",
            "message",
            "mode",
            "period",
            "weekly_time",
            "communication",
            "attachment",
        ]

        widgets = {
            "goal": forms.Textarea(attrs={
                "rows": 4
            }),

            "message": forms.Textarea(attrs={
                "rows": 5
            }),
    }
