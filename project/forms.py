from datetime import timedelta

from django import forms

from match.models import Proposal
from user.models import Talent, User
from .models import ProjectFile, Task
class ProjectOverviewForm(forms.Form):
    title = forms.CharField(
        label="프로젝트 제목",
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "placeholder": "제목을 입력하세요.",
                "maxlength": "50",
            }
        ),
    )

    summary = forms.CharField(
        label="프로젝트 요약",
        max_length=50,
        widget=forms.Textarea(
            attrs={
                "placeholder": "간단한 프로젝트에 대해 입력하세요.",
                "maxlength": "50",
                "rows": "4",
            }
        ),
    )

    give_talent = forms.ModelChoiceField(
        label="제공 가능 역량",
        queryset=Talent.objects.all(),
        empty_label="내가 제공할 수 있는 능력을 선택하세요.",
    )

    need_talent = forms.ModelChoiceField(
        label="필요한 역량",
        queryset=Talent.objects.all(),
        empty_label="나에게 필요한 능력을 선택하세요.",
    )

    mode = forms.ChoiceField(
        label="협업 모드 선택",
        choices=Proposal.Mode.choices,
        widget=forms.RadioSelect,
    )

    period = forms.IntegerField(
        label="기간",
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "기간을 입력하세요.",
            }
        ),
    )

    weekly_time = forms.ChoiceField(
        label="주당 시간",
        choices=[
            ("", "시간을 선택하세요."),
            *Proposal.WeeklyTime.choices,
        ],
    )

    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.project = project

        # 이미 개요를 작성했다면 기존 내용을 수정 폼에 표시
        if project and project.overview_completed and not self.is_bound:
            proposal = project.proposal

            self.initial.update(
                {
                    "title": project.title,
                    "summary": proposal.goal,
                    "give_talent": proposal.give_talent,
                    "need_talent": proposal.need_talent,
                    "mode": proposal.mode,
                    "period": proposal.period,
                    "weekly_time": proposal.weekly_time,
                }
            )

    def save(self):
        project = self.project
        proposal = project.proposal

        project.title = self.cleaned_data["title"]
        project.end_date = project.start_date + timedelta(
            weeks=self.cleaned_data["period"]
        )
        project.overview_completed = True

        project.save(
            update_fields=[
                "title",
                "end_date",
                "overview_completed",
            ]
        )

        proposal.goal = self.cleaned_data["summary"]
        proposal.give_talent = self.cleaned_data["give_talent"]
        proposal.need_talent = self.cleaned_data["need_talent"]
        proposal.mode = self.cleaned_data["mode"]
        proposal.period = self.cleaned_data["period"]
        proposal.weekly_time = self.cleaned_data["weekly_time"]

        proposal.save(
            update_fields=[
                "goal",
                "give_talent",
                "need_talent",
                "mode",
                "period",
                "weekly_time",
            ]
        )

        return project

class TaskForm(forms.ModelForm):
    def __init__(self, *args, project=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["deadline"].required = True

        if project:
            self.fields["assignee"].queryset = User.objects.filter(
                projectmember__project=project
            ).distinct()

    class Meta:
        model = Task

        fields = [
            "title",
            "assignee",
            "deadline",
            "description",
        ]

        labels = {
            "title": "협업 제목",
            "assignee": "담당자 입력",
            "deadline": "마감일",
            "description": "설명(선택)",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "협업 제목을 입력하세요.",
                    "maxlength": "50",
                }
            ),

            "assignee": forms.Select(),

            "deadline": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "placeholder": "협업에 관한 설명을 입력하세요.",
                    "maxlength": "100",
                    "rows": "5",
                }
            ),
        }


class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile

        fields = [
            "file_path",
            "folder_name",
        ]