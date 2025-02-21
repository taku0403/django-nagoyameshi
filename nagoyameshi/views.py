from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView, ListView
from .models import Restaurant

class TopView(TemplateView):
    template_name = "nagoyameshi/top.html"

""""
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
"""

class RestaurantListView(ListView):
    model = Restaurant
    paginate_by = 5