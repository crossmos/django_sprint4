from django.db.models import Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Category, Post


def get_posts(manager=Post.objects, filtred=False, annotated=False):
    queryset = manager.select_related(
        'category',
        'author',
        'location'
    )
    if filtred:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    if annotated:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

    return queryset


class CategoryPage:
    """Класс для работы с категориями"""

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
