from django import forms
from .models import Card


class CardForm(forms.ModelForm):
    """カード作成・編集フォーム"""

    class Meta:
        model = Card
        fields = ("front", "back", "front_image", "back_image")
        widgets = {
            "front": forms.Textarea(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
                "placeholder": "質問や覚えたい内容を入力",
                "rows": 3,
            }),
            "back": forms.Textarea(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
                "placeholder": "答えや説明を入力",
                "rows": 3,
            }),
            "front_image": forms.FileInput(attrs={
                "class": "w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
                "accept": "image/*",
            }),
            "back_image": forms.FileInput(attrs={
                "class": "w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100",
                "accept": "image/*",
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        front = cleaned_data.get("front")
        front_image = cleaned_data.get("front_image")

        # 表面はテキストか画像のどちらか必須
        if not front and not front_image:
            raise forms.ValidationError("表面にはテキストか画像のどちらかを入力してください。")

        return cleaned_data
