from django.shortcuts import render
from django.http import HttpResponseServerError


def error_403_csrf(request, reason=''):
    return render(request, 'core/403csrf.html', status=403)


def error_404(request, exception):
    return render(request, 'core/404.html', status=404)


def error_500(request):
    return HttpResponseServerError(render(request, 'core/500.html'))
