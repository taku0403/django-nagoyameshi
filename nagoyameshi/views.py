from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView, ListView, DetailView, CreateView 
from .models import Restaurant,Review

class TopView(TemplateView):
    template_name = "nagoyameshi/top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurants'] = Restaurant.objects.all()
        return context

class RestaurantListView(ListView):
    model = Restaurant
    paginate_by = 5

class RestaurantDetailView(DetailView):
    model = Restaurant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 該当店舗のレビューだけ表示
        context["reviews"] = Review.objects.filter(restaurant=kwargs["object"].id)

        return context
    
class ReviewCreateView(CreateView):
    model = Restaurant
    fields = '__all__'
