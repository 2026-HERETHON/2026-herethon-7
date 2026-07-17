from django import forms
from .models import Proposal
from user.models import Talent


class ProposalForm(forms.ModelForm):
    # 직접 입력하거나 여러 개 선택한 재능 이름 (쉼표로 구분)
    give_talent_custom = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.HiddenInput,
    )
    need_talent_custom = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.HiddenInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["give_talent"].required = False
        self.fields["need_talent"].required = False
        self.fields["give_talent"].queryset = Talent.objects.filter(id__lte=7)
        self.fields["need_talent"].queryset = Talent.objects.filter(id__lte=7)
        self.fields["mode"].choices = [
            (Proposal.Mode.ONE, "1:1 협업"),
            (Proposal.Mode.GROUP, "소그룹(2-5명)"),
        ]
        self.fields["weekly_time"].choices = [
            ("", "시간을 입력하세요."),
            *Proposal.WeeklyTime.choices,
        ]
        self.fields["communication"].initial = Proposal.Communication.ETC

        for field_name in [
            "title",
            "goal",
            "mode",
            "period",
            "weekly_time",
        ]:
            self.fields[field_name].error_messages["required"] = "필수 항목을 입력하세요."

    def clean(self):
        cleaned_data = super().clean()

        for field_name in ["give_talent", "need_talent"]:
            custom_name = (cleaned_data.get(f"{field_name}_custom") or "").strip()
            cleaned_data[f"{field_name}_custom"] = custom_name
            if not cleaned_data.get(field_name) and not custom_name:
                self.add_error(field_name, "필수 항목을 입력하세요.")

        return cleaned_data

    def save(self, commit=True):
        proposal = super().save(commit=False)

        for field_name in ["give_talent", "need_talent"]:
            custom_name = self.cleaned_data.get(f"{field_name}_custom")
            if custom_name:
                talent = Talent.objects.filter(name=custom_name).first()
                if talent is None:
                    talent = Talent.objects.create(name=custom_name)
                setattr(proposal, field_name, talent)

        if commit:
            proposal.save()
            self.save_m2m()
        return proposal

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
            "title": forms.TextInput(attrs={
                "placeholder": "제목을 입력하세요.",
                "maxlength": 50,
            }),
            "goal": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "목표를 입력하세요.",
                "maxlength": 50,
            }),
            "mode": forms.RadioSelect,
            "communication": forms.HiddenInput,
            "message": forms.HiddenInput,
            "period": forms.NumberInput(attrs={
                "placeholder": "기간을 입력하세요.",
                "min": 1,
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
