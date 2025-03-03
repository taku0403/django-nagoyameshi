from django.shortcuts import render, redirect

# Create your views here.

from django.views.generic import TemplateView, DetailView, ListView 
from .models import Restaurant, Review, Favorite, Reservation, PremiumUser

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

         # ログインをしているのかチェック。
        if self.request.user.is_authenticated:
            # 店舗のお気に入り積みかチェック
            context["is_favorite"] = Favorite.objects.filter(restaurant=kwargs["object"].id, user=self.request.user.id).exists()

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["is_premium"] = PremiumUser.objects.filter(user=self.request.user).exists()

        return context

class FavoriteListView(ListView):
    model = Favorite
    template_name = "nagoyamehi/favorite_list.html"

class ReservationListView(ListView):
    model = Reservation
    template_name = "nagoyameshi/reservation_list.html"

# サブスク登録はログイン済みのユーザーだけ
from django.contrib.auth.mixins import LoginRequiredMixin
# setting.pyの内容を用意
from django.conf import settings
# リダイレクト先の指定（カード決済を終えた後のリダイレクト先の指定）
from django.urls import reverse_lazy
# stripe ライブラリをimport , pip install stripe
import stripe

# セッションを作るため、APIキーをセット
stripe.api_key  = settings.STRIPE_API_KEY

# 「有料会員登録をする」ボタン　CheckoutViewのpostメソッドへ
"""
class IndexView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        return render(request, "bbs/index.html")

index   = IndexView.as_view()
"""

# 1~4: セッションを作って、ユーザーがカード入力ページへ
class CheckoutView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):

        # 1: セッションを作る
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': settings.STRIPE_PRICE_ID,
                    'quantity': 1,
                },
            ],
            payment_method_types=['card'],
            mode='subscription',
            # カード決済が失敗、成功したときのダイレクト先を指定
            # TIPS: Stripeからのリダイレクトなため、https://~から始まるように
            success_url=request.build_absolute_uri(reverse_lazy("success")) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse_lazy("mypage")),
        )

        # 2: セッションid
        print( checkout_session["id"] )

        # 3~4: リダイレクト　～　ユーザーがカードの入力
        return redirect(checkout_session.url)

# 7: セッションidを使ってstripeに決済をしたか確認
class SuccessView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        # パラメータにセッションIDがあるかチェック
        if "session_id" not in request.GET:
            print("セッションIDがありません。")
            return redirect("top")


        # そのセッションIDは有効であるかチェック。
        try:
            checkout_session_id = request.GET['session_id']
            checkout_session    = stripe.checkout.Session.retrieve(checkout_session_id)
        except:
            print( "このセッションIDは無効です。")
            return redirect("top")

        print(checkout_session)

        # statusをチェックする。未払であれば拒否する。(未払いのsession_idを入れられたときの対策)
        if checkout_session["payment_status"] != "paid":
            print("未払い")
            return redirect("top")

        print("支払い済み")


        # 有効であれば、セッションIDからカスタマーIDを取得。ユーザーモデルへカスタマーIDを記録する。
        """
        request.user.customer   = checkout_session["customer"]
        request.user.save()
        """

        premium_user = PremiumUser()    
        premium_user.user = request.user
        premium_user.premium_code = checkout_session["customer"]
        premium_user.save()

        print("有料会員登録しました！")

        return redirect("mypage")

# サブスクリプションの操作関係
class PortalView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):

        premium_user = PremiumUser.objects.filter(user=request.user).first()

        if not premium_user:
            print( "有料会員登録されていません")
            return redirect("mypage")

        # ユーザーモデルに記録しているカスタマーIDを使って、ポータルサイトへリダイレクト
        portalSession   = stripe.billing_portal.Session.create(
            customer    = premium_user.premium_code ,
            return_url  = request.build_absolute_uri(reverse_lazy("mypage")),
        )

        return redirect(portalSession.url)

"""
class PremiumView(View):
    def get(self, request, *args, **kwargs):
        
        if not request.user.customer:
            print("カスタマーIDがセットされていません。")
            return redirect("bbs:index")


        # カスタマーIDを元にStripeに問い合わせ
        try:
            subscriptions = stripe.Subscription.list(customer=request.user.customer)
        except:
            print("このカスタマーIDは無効です。")

            request.user.customer   = ""
            request.user.save()

            return redirect("bbs:index")


        # ステータスがアクティブであるかチェック。
        for subscription in subscriptions.auto_paging_iter():
            if subscription.status == "active":
                print("サブスクリプションは有効です。")

                return render(request, "bbs/premium.html")
            else:
                print("サブスクリプションが無効です。")


        return redirect("bbs:index")

premium     = PremiumView.as_view()
"""