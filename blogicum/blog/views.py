from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView
)

from django.conf import settings
from .mixins import (
    CommentMixin,
    PostMixin,
    OnlyAuthorMixin,
    ReversePostDetailMixin,
    ReverseProfileMixin
)
from .models import Comment, Post, User
from .forms import CommentForm, UserForm, PostForm
from .query_utils import CategoryPage, get_posts


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
                get_posts(filtred=True),
                pk=self.kwargs['post_id']
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class PostListView(PostMixin, ListView):
    template_name = 'blog/index.html'
    paginate_by = settings.PAGINATE_BY

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
    paginate_by = settings.PAGINATE_BY

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['category'] = CategoryPage.get_category(self)
        return context

    def get_queryset(self):
        return get_posts(
            manager=CategoryPage.get_category(self).posts,
            filtred=True,
            annotated=True
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
    paginate_by = settings.PAGINATE_BY


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

    posts = get_posts(
        manager=profile.posts,
        filtred=(request.user != profile),
        annotated=True
    )

    paginator = Paginator(posts, settings.PAGINATE_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'page_obj': page_obj
    }

    return render(request, template_name, context)
