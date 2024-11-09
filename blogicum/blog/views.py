from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView
)
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect

from blogicum.settings import PAGINATE_BY
from .models import Comment, Post, User
from .forms import CommentForm, UserForm, PostForm
from .utils import get_category, get_posts


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
            kwargs={'username': self.request.user}
        )


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


class PostCreateView(
    PostMixin,
    LoginRequiredMixin,
    ReverseProfileMixin,
    CreateView
):
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(
            get_posts(), pk=self.kwargs['post_id'])
        if post.author != self.request.user:
            return get_object_or_404(
                get_posts(filtred=True, annotated=True),
                pk=self.kwargs['post_id']
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            post_id=self.kwargs['post_id'])
        return context


class PostListView(PostMixin, ListView):
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return get_posts(filtred=True, annotated=True)


class PostUpdateView(
    PostMixin,
    OnlyAuthorMixin,
    ReversePostDetailMixin,
    UpdateView
):
    template_name = 'blog/create.html'
    form_class = PostForm


class PostDeleteView(
    PostMixin,
    OnlyAuthorMixin,
    ReverseProfileMixin,
    DeleteView
):
    pass


class ProfileUpdateView(LoginRequiredMixin, ReverseProfileMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self):
        return self.request.user


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['category'] = get_category(self)
        return context

    def get_queryset(self):
        get_category(self)
        return get_posts(filtred=True, annotated=True).filter(
            category__slug=self.kwargs['category_slug']
        )


class CommentCreateView(
    LoginRequiredMixin,
    ReversePostDetailMixin,
    CreateView
):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentListView(ListView):
    model = Comment
    template_name = 'blog/comments.html'
    paginate_by = PAGINATE_BY


class CommentUpdateView(
    CommentMixin,
    OnlyAuthorMixin,
    ReversePostDetailMixin,
    UpdateView
):
    form_class = CommentForm


class CommentDeleteView(
    CommentMixin,
    OnlyAuthorMixin,
    ReversePostDetailMixin,
    DeleteView
):
    pass


def profile(request, username):
    template_name = 'blog/profile.html'
    profile = get_object_or_404(
        User,
        username=username
    )

    if str(request.user) == profile.username:
        posts = profile.posts.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    else:
        posts = profile.posts.filter(
            pub_date__lte=timezone.now(),
            is_published=True
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    paginator = Paginator(posts, PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'page_obj': page_obj
    }

    return render(request, template_name, context)
