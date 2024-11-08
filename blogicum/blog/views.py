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

from blog.models import Category, Comment, Post, User
from .forms import CommentForm, UserForm, PostForm


def get_posts_list():
    return Post.objects.select_related(
        'category',
        'author',
        'location').filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True)


def get_all_posts():
    return Post.objects.select_related(
        'category',
        'author',
        'location')


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'profile_slug': self.request.user}
        )


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.filter(
            post_id=self.kwargs['post_id'])
        return context

    def get_queryset(self):
        post = get_object_or_404(
            get_all_posts(), pk=self.kwargs['post_id'])
        if post.author == self.request.user:
            return get_all_posts().filter(pk=self.kwargs['post_id'])
        else:
            return get_posts_list().filter(pk=self.kwargs['post_id'])


class PostListView(ListView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_posts_list().annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'profile_slug': self.request.user}
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'profile_slug': self.request.user}
        )


class CategoryPostsListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context

    def get_queryset(self):
        return get_posts_list().annotate(
            comment_count=Count('comments')
        ).filter(
            category__slug=self.kwargs['category_slug']
        ).order_by('-pub_date')


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentListView(ListView):
    model = Comment
    template_name = 'blog/comments.html'
    paginate_by = 10


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


def profile(request, profile_slug):
    template_name = 'blog/profile.html'
    # Получаю данные о профиле по slug
    profile = get_object_or_404(
        User,
        username=profile_slug
    )
    # Получаю посты по полученному профилу через related name "posts"
    posts = profile.posts.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': profile,
        'page_obj': page_obj
    }

    return render(request, template_name, context)
