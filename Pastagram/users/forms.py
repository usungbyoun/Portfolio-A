from django import forms
from django.core.exceptions import ValidationError
from .models import User
from pathlib import Path
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
import os

class LoginForm(forms.Form):
    username = forms.CharField(
        min_length=3,
        widget=forms.TextInput(
            attrs={"placeholder": "사용자명 (3자리 이상)"},
        ),
    )
    password = forms.CharField(
        min_length=4,
        widget=forms.PasswordInput(
            attrs={"placeholder": "비밀번호 (4자리 이상)"},
        ),
    )

class SignupForm(forms.Form):

    username = forms.CharField()
    password1 = forms.CharField(widget=forms.PasswordInput)  # 회원가입시 ***으로 보여진다.
    password2 = forms.CharField(widget=forms.PasswordInput)
    profile_image = forms.ImageField(required=False)
    short_description = forms.CharField(required=False)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError(f"입력한 사용자면({username})은 이미 사용 중입니다")
        return username

    def clean(self):
        password1 = self.cleaned_data["password1"]
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            # password2 필드에 오류를 추가
            self.add_error("password2", "비밀번호가 일치하지 않습니다")


    def save(self):
        username = self.cleaned_data['username']
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        profile_image = self.cleaned_data['profile_image']
        short_description = self.cleaned_data['short_description']

        if not profile_image:
            default_image_path = './static/image/profile_basic.png'
            with open(default_image_path, 'rb') as f:
                content = f.read()
                image = Image.open(default_image_path)
                profile_image = ContentFile(content, name='profile_basic')

        user = User.objects.create_user(
            username=username,
            password=password1,
            profile_image=profile_image,
            short_description=short_description,
        )
        return user