from django import forms
from .models import MusicDB, Comment

class CommentForm(forms.ModelForm):
    class Meta: 
        model = Comment
        fields = ('text', )