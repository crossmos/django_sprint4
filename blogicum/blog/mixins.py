from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect

from .models import Comment, Post


class CommentMixin:
    """Миксин, передающий базовые параметры для CBV комментов"""

    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post=self.kwargs['post_id']
        )


class PostMixin:
    """Миксин, передающий базовые параметры для CBV постов"""

    model = Post
    pk_url_kwarg = 'post_id'


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин, проверяющий авторство"""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs['post_id']
        )


class ReversePostDetailMixin:
    """Миксин, отвечающий за реверс на страницу поста"""

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class ReverseProfileMixin:
    """Миксин, отвечающий за реверс на профиль"""

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
