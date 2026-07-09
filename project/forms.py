from django import forms
from .models import Task, ProjectFile

class TaskForm(forms.ModelForm):

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