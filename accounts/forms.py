from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation

User = get_user_model()

class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", required=False, widget=forms.PasswordInput)

    email = forms.EmailField(required=False, empty_value=None)
    phone = forms.CharField(required=False, empty_value=None)

    class Meta:
        model = User
        fields = ("role", "nickname", "email", "phone", "password1", "password2")

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("두 비밀번호가 일치하지 않습니다.")
            password_validation.validate_password(p1, self.instance)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)

        if user.email == "":
            user.email = None
        if user.phone == "":
            user.phone = None

        # username 자동 생성
        base = (user.email.split("@")[0] if user.role == "manager" and user.email
                else f"user_{user.phone[-4:]}" if user.phone
                else "user")
        candidate, i = base, 1
        from django.contrib.auth import get_user_model
        U = get_user_model()
        while U.objects.filter(username=candidate).exists():
            candidate, i = f"{base}_{i}", i + 1
        user.username = candidate

        # 비밀번호 설정(없으면 unusable)
        p1 = self.cleaned_data.get("password1")
        user.set_password(p1) if p1 else user.set_unusable_password()

        if commit:
            user.save()
        return user
