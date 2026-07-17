# user/forms.py

from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, ProfileTalent, Talent, Portfolio, Review

User = get_user_model()


class SignupForm(forms.ModelForm):
    """회원가입 폼"""
    password = forms.CharField(
        min_length=8, max_length=20,
        widget=forms.PasswordInput,
        label='비밀번호'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label='비밀번호 확인'
    )

    class Meta:
        model = User
        fields = ['email', 'name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 가입된 이메일입니다.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('비밀번호가 일치하지 않습니다.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # username을 email로
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """로그인 폼"""
    email = forms.EmailField(label='이메일')
    password = forms.CharField(widget=forms.PasswordInput, label='비밀번호')


class ProfileForm(forms.ModelForm):
    """프로필 등록/수정 폼"""
    name = forms.CharField(max_length=50, required=True, label='이름')
    give_talents = forms.ModelMultipleChoiceField(
        queryset=Talent.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='줄 수 있는 것 (기부재능)'
    )
    need_talents = forms.ModelMultipleChoiceField(
        queryset=Talent.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='필요한 것 (희망재능)'
    )

    class Meta:
        model = Profile
        fields = ['profile_image', 'intro', 'identity', 'work_style', 'skills']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['name'].initial = self.user.name

        # 수정 시 기존 재능 선택값 채우기
        if self.instance and self.instance.pk:
            self.fields['give_talents'].initial = Talent.objects.filter(
                profiletalent__profile=self.instance,
                profiletalent__type='GIVE'
            )
            self.fields['need_talents'].initial = Talent.objects.filter(
                profiletalent__profile=self.instance,
                profiletalent__type='NEED'
            )

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            profile.user = self.user
        if commit:
            if self.user and self.user.name != self.cleaned_data['name']:
                self.user.name = self.cleaned_data['name']
                self.user.save(update_fields=['name'])
            profile.save()

            # 기존 재능 삭제 후 재등록
            ProfileTalent.objects.filter(profile=profile).delete()

            for talent in self.cleaned_data['give_talents']:
                ProfileTalent.objects.create(
                    profile=profile, talent=talent, type='GIVE'
                )
            for talent in self.cleaned_data['need_talents']:
                ProfileTalent.objects.create(
                    profile=profile, talent=talent, type='NEED'
                )
        return profile


class PasswordFindForm(forms.Form):
    """비밀번호 찾기 폼"""
    email = forms.EmailField(label='가입한 이메일')


class PortfolioForm(forms.ModelForm):
    """포트폴리오 수정 폼"""
    class Meta:
        model = Portfolio
        fields = ['title', 'role', 'summary', 'file_path']


class ReviewForm(forms.ModelForm):
    """후기 작성 폼"""
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }