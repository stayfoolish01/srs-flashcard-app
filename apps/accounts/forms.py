from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """ユーザー登録フォーム"""

    email = forms.EmailField(
        required=True,
        label="メールアドレス",
        widget=forms.EmailInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "placeholder": "example@email.com",
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # フィールドのカスタマイズ
        self.fields["username"].label = "ユーザー名"
        self.fields["username"].widget.attrs.update({
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "placeholder": "ユーザー名を入力",
        })

        self.fields["password1"].label = "パスワード"
        self.fields["password1"].widget.attrs.update({
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "placeholder": "パスワードを入力",
        })

        self.fields["password2"].label = "パスワード（確認）"
        self.fields["password2"].widget.attrs.update({
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "placeholder": "パスワードを再入力",
        })

    def clean_email(self):
        """メールアドレスの重複チェック"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは既に登録されています。")
        return email


class LoginForm(AuthenticationForm):
    """ログインフォーム"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "ユーザー名"
        self.fields["username"].widget.attrs.update({
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "placeholder": "ユーザー名を入力",
        })

        self.fields["password"].label = "パスワード"
        self.fields["password"].widget.attrs.update({
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
            "placeholder": "パスワードを入力",
        })


class UserUpdateForm(forms.ModelForm):
    """ユーザー情報更新フォーム"""

    timezone = forms.ChoiceField(
        label="タイムゾーン",
        choices=[
            ("Asia/Tokyo", "Asia/Tokyo (日本標準時)"),
            ("UTC", "UTC (協定世界時)"),
            ("America/New_York", "America/New_York (東部標準時)"),
            ("Europe/London", "Europe/London (イギリス時間)"),
        ],
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
        })
    )
    daily_new_cards = forms.IntegerField(
        label="1日の新規カード上限",
        min_value=1,
        max_value=999,
        widget=forms.NumberInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
        })
    )

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        self.profile = kwargs.pop("profile", None)
        super().__init__(*args, **kwargs)

        self.fields["email"].label = "メールアドレス"
        self.fields["email"].widget.attrs.update({
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent",
        })

        # プロフィールの初期値を設定
        if self.profile:
            self.fields["timezone"].initial = self.profile.timezone
            self.fields["daily_new_cards"].initial = self.profile.daily_new_cards

    def clean_email(self):
        """メールアドレスの重複チェック（自分以外）"""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("このメールアドレスは既に登録されています。")
        return email

    def save(self, commit=True):
        """ユーザーとプロフィールを保存"""
        user = super().save(commit=commit)

        if self.profile and commit:
            self.profile.timezone = self.cleaned_data["timezone"]
            self.profile.daily_new_cards = self.cleaned_data["daily_new_cards"]
            self.profile.save()

        return user