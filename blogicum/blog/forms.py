from django import forms

from .models import Post, User


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('location', 'category', 'is_published')
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
