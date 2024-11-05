from django.shortcuts import render
from django.views.generic import TemplateView


class AboutDetailView(TemplateView):
    template_name = 'pages/about.html'


class RulesDetailView(TemplateView):
    template_name = 'pages/rules.html'
