from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from blog.models import Category, Post

POSTS_LIMIT = 5


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


def index(request):
    template_name = 'blog/index.html'
    context = {
        'post_list': get_post_list()[:POSTS_LIMIT]
    }
    return render(request, template_name, context)


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
