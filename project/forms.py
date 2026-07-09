from django import forms
from .models import Task, ProjectFile, Review

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
            "file",
            "folder_name",
        ]

class ReviewForm(forms.ModelForm):

    class Meta:

        model = Review

        fields = [
            "rating",
            "content",
        ]

        widgets = {

            "content": forms.Textarea(
                attrs={
                    "rows": 4
                }
            )

        }