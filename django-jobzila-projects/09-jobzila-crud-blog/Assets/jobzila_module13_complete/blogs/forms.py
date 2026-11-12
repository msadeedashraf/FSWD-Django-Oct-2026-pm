from django import forms
from .models import Blog


class CreateBlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title', 'body', 'banner']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Article title'}),
            'body': forms.Textarea(attrs={'rows': 12, 'placeholder': 'Write your article'}),
            'banner': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
