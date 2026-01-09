from django import forms
from .models import Deck


class DeckForm(forms.ModelForm):
    """デッキ作成・編集フォーム"""

    class Meta:
        model = Deck
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
                "placeholder": "デッキ名を入力",
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
                "placeholder": "デッキの説明（任意）",
                "rows": 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        """同一ユーザー内でデッキ名の重複をチェック"""
        name = self.cleaned_data.get("name")
        if self.user:
            queryset = Deck.objects.filter(user=self.user, name=name)
            # 編集時は自分自身を除外
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise forms.ValidationError("同じ名前のデッキが既に存在します。")
        return name
