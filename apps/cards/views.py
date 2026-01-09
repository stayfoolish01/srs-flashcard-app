from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.http import Http404

from apps.decks.models import Deck
from .models import Card
from .forms import CardForm


class CardOwnerMixin(UserPassesTestMixin):
    """カードの所有者（デッキの所有者）のみアクセス可能にするMixin"""

    def test_func(self):
        card = self.get_object()
        return card.deck.user == self.request.user


class CardCreateView(LoginRequiredMixin, CreateView):
    """カード作成ビュー"""

    model = Card
    form_class = CardForm
    template_name = "cards/card_form.html"

    def dispatch(self, request, *args, **kwargs):
        # デッキの所有者チェック
        self.deck = get_object_or_404(Deck, pk=kwargs["deck_pk"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deck"] = self.deck
        return context

    def form_valid(self, form):
        form.instance.deck = self.deck
        messages.success(self.request, "カードを作成しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容に誤りがあります。")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("decks:deck_detail", args=[self.deck.pk])


class CardUpdateView(LoginRequiredMixin, CardOwnerMixin, UpdateView):
    """カード編集ビュー"""

    model = Card
    form_class = CardForm
    template_name = "cards/card_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deck"] = self.object.deck
        return context

    def form_valid(self, form):
        messages.success(self.request, "カードを更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容に誤りがあります。")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("decks:deck_detail", args=[self.object.deck.pk])


class CardDeleteView(LoginRequiredMixin, CardOwnerMixin, DeleteView):
    """カード削除ビュー"""

    model = Card
    template_name = "cards/card_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["deck"] = self.object.deck
        return context

    def form_valid(self, form):
        deck_pk = self.object.deck.pk
        messages.success(self.request, "カードを削除しました。")
        self.object.delete()
        return redirect(reverse("decks:deck_detail", args=[deck_pk]))

    def get_success_url(self):
        return reverse("decks:deck_detail", args=[self.object.deck.pk])


@login_required
def card_detail_view(request, pk):
    """カード詳細ビュー"""
    card = get_object_or_404(Card, pk=pk)

    # 所有者チェック
    if card.deck.user != request.user:
        raise Http404

    return render(request, "cards/card_detail.html", {
        "card": card,
        "deck": card.deck,
    })
