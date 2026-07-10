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

        labels = {
            "give_talent": "제공 가능한 재능",
            "need_talent": "배우고 싶은 재능",
            "title": "프로젝트 제목",
            "goal": "목표",
            "message": "제안 메시지",
            "mode": "협업 방식",
            "period": "기간(주)",
            "weekly_time": "주당 가능 시간",
            "communication": "소통 방식",
            "attachment": "첨부파일",
        }
