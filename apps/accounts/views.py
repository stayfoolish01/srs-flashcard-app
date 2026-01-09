from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import SignUpForm, LoginForm, UserUpdateForm
from .models import UserProfile


class SignUpView(CreateView):
    """ユーザー登録ビュー"""

    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form):
        # ユーザーを保存
        user = form.save()

        # UserProfileを自動作成
        UserProfile.objects.create(user=user)

        messages.success(self.request, "アカウントを作成しました。ログインしてください。")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容に誤りがあります。")
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    """カスタムログインビュー"""

    form_class = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        messages.success(self.request, f"ようこそ、{form.get_user().username}さん！")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "ユーザー名またはパスワードが正しくありません。")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """カスタムログアウトビュー"""

    def dispatch(self, request, *args, **kwargs):
        messages.info(request, "ログアウトしました。")
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    """プロフィール表示ビュー"""

    # UserProfileが存在しない場合は作成
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    return render(request, "accounts/profile.html", {
        "user": request.user,
        "profile": profile,
    })


@login_required
def profile_edit_view(request):
    """プロフィール編集ビュー"""

    # UserProfileが存在しない場合は作成
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user, profile=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "プロフィールを更新しました。")
            return redirect("accounts:profile")
        else:
            messages.error(request, "入力内容に誤りがあります。")
    else:
        form = UserUpdateForm(instance=request.user, profile=profile)

    return render(request, "accounts/profile_edit.html", {
        "form": form,
    })