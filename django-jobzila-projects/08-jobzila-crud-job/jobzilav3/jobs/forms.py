from django import forms

from .models import Job


class CreateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "company",
            "location",
            "description",
            "apply_link",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "Example: Python Developer",
                }
            ),
            "company": forms.TextInput(
                attrs={
                    "placeholder": "Example: Microsoft",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "placeholder": "Example: Toronto, ON",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Describe the job responsibilities and requirements",
                    "rows": 7,
                }
            ),
            "apply_link": forms.URLInput(
                attrs={
                    "placeholder": "https://example.com/apply",
                }
            ),
        }