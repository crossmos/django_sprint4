from django import forms
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DetailView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone

from blog.models import Category, Post, User
from .forms import UserForm, PostForm


def get_post_list():
    return Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def profile(request, slug):
    template_name = 'blog/profile.html'

    context = {
        'profile': get_object_or_404(
            User,
            username=slug
        ),
        'page_obj': Post.objects.filter(
            author__id=get_object_or_404(
                User,
                username=slug
            ).pk
        )
    }
    paginator = Paginator(context['page_obj'], 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}

    return render(request, template_name, context)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'


class PostListView(ListView):
    model = Post
    queryset = get_post_list()
    template_name = 'blog/index.html'
    paginate_by = 10


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    success_url = reverse_lazy('blog:index')


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return self.request.user


class CategoryPostsListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True
        )
        return context

    def get_queryset(self):
        return Post.objects.filter(
            category__slug=self.kwargs['slug']
        )
