from django import forms
from .models import Proposal

class ProposalForm(forms.ModelForm):

    class Meta:
        model = Proposal

        fields = [
            "talent",
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

        labels = {
            "title": "프로젝트 제목",
            "goal": "목표",
            "message": "제안 메시지",
        }
