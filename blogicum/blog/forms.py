from django import forms

from .models import Comment, Post, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('is_published', 'author')
        widgets = {
            'pub_date': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            )
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
