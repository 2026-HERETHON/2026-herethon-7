from django import forms
from .models import Task, ProjectFile
from user.models import User

class TaskForm(forms.ModelForm):

    def __init__(self, *args, project=None, **kwargs):

        super().__init__(*args, **kwargs)

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
            "status",
        ]

        widgets = {

            "deadline": forms.DateInput(
                attrs={
                    "type": "date"
                }
            )

        }


class ProjectFileForm(forms.ModelForm):

    class Meta:

        model = ProjectFile

        fields = [
            "file_path",
            "folder_name",
        ]