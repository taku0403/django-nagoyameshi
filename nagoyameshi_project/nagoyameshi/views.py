from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView

class TopView(TemplateView):
    template_name = "nagoyameshi/top.html"