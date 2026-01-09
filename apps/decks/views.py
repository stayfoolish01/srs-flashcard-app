from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

from .models import Deck
from .forms import DeckForm


class DeckListView(LoginRequiredMixin, ListView):
    """デッキ一覧ビュー"""

    model = Deck
    template_name = "decks/deck_list.html"
    context_object_name = "decks"

    def get_queryset(self):
        """ログインユーザーのデッキのみ取得"""
        return Deck.objects.filter(user=self.request.user)


class DeckCreateView(LoginRequiredMixin, CreateView):
    """デッキ作成ビュー"""

    model = Deck
    form_class = DeckForm
    template_name = "decks/deck_form.html"
    success_url = reverse_lazy("decks:deck_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "デッキを作成しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容に誤りがあります。")
        return super().form_invalid(form)


class DeckOwnerMixin(UserPassesTestMixin):
    """デッキの所有者のみアクセス可能にするMixin"""

    def test_func(self):
        deck = self.get_object()
        return deck.user == self.request.user


class DeckUpdateView(LoginRequiredMixin, DeckOwnerMixin, UpdateView):
    """デッキ編集ビュー"""

    model = Deck
    form_class = DeckForm
    template_name = "decks/deck_form.html"
    success_url = reverse_lazy("decks:deck_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "デッキを更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容に誤りがあります。")
        return super().form_invalid(form)


class DeckDeleteView(LoginRequiredMixin, DeckOwnerMixin, DeleteView):
    """デッキ削除ビュー"""

    model = Deck
    template_name = "decks/deck_confirm_delete.html"
    success_url = reverse_lazy("decks:deck_list")

    def form_valid(self, form):
        messages.success(self.request, "デッキを削除しました。")
        return super().form_valid(form)


@login_required
def deck_detail_view(request, pk):
    """デッキ詳細ビュー"""
    deck = get_object_or_404(Deck, pk=pk, user=request.user)

    return render(request, "decks/deck_detail.html", {
        "deck": deck,
    })
