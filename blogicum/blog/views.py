from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone

from blog.models import Category, Post, User
from .forms import UserForm, PostForm


def profile(request, username):
    template_name = 'blog/profile.html'
    context = {
        'profile': get_object_or_404(
            User,
            username=username
        )
    }
    return render(request, template_name, context)


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


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')


class PostDetailView(DeleteView):
    model = Post


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_obj'] = get_post_list()
        return context


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


def category_posts(request, category_slug):
    template_name = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    context = {
        'category': category,
        'post_list': get_post_list().filter(
            category__slug=category_slug
        )
    }
    return render(
        request,
        template_name,
        context
    )


def post_detail(request, post_id):
    template_name = 'blog/detail.html'
    post = get_object_or_404(
        get_post_list(),
        pk=post_id
    )
    context = {
        'post': post
    }
    return render(
        request,
        template_name,
        context
    )
