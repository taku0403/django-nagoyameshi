from django.shortcuts import render, redirect

# Create your views here.

from django.views.generic import TemplateView, DetailView, ListView 
from .models import Restaurant, Review, Favorite, Reservation

class TopView(TemplateView):
    template_name = "nagoyameshi/top.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurants'] = Restaurant.objects.all()
        return context

class RestaurantDetailView(DetailView):
    model = Restaurant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 該当店舗のレビューだけ表示
        context["reviews"] = Review.objects.filter(restaurant=kwargs["object"].id)

        # 店舗のお気に入り積みかチェック
        context["is_favorite"] = Favorite.objects.filter(restaurant=kwargs["object"].id, user=self.request.user).exists()

        return context

from django.views import View
from .forms import ReviewForm, FavoriteForm, ReservationForm

class ReviewCreateView(View):
    def post(self, request, *args, **kwargs):
        # POSTメソッド受け取り処理
        form = ReviewForm(request.POST)

        # 投稿されたデータが制約内か検証
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        
        return redirect("detail", request.POST["restaurant"])
    
class FavoriteCreateView(View):
    def post(self, request, *args, **kwargs):
        #すでに登録済みの場合、削除
        favorites = Favorite.objects.filter(user=request.user, restaurant=request.POST["restaurant"])
        if favorites:
            favorites.delete()
            return redirect("detail", request.POST["restaurant"])

        form = FavoriteForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)

        return redirect("detail", request.POST["restaurant"])
    
class ReservationCreateView(View):
    def post(self, request, *args, **kwargs):
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        return redirect("detail", request.POST["restaurant"])
    
class MypageView(TemplateView):
    template_name = "nagoyameshi/mypage.html"

class FavoriteListView(ListView):
    model = Favorite
    template_name = "nagoyamehi/favorite_list.html"

class ReservationListView(ListView):
    model = Reservation
    template_name = "nagoyameshi/reservation_list.html"