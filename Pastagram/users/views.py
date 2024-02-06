from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, SignupForm
from django.contrib.auth import authenticate, login, logout
from .models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
import os
from django.conf import settings


def login_view(request):


    if request.user.is_authenticated:
        return redirect("/posts/feeds/")

    if request.method == "POST":
        form = LoginForm(data=request.POST)

        # LoginForm에 전달된 데이터가 유효하다면
        if form.is_valid():
            # username과 password 값을 가져와 변수에 할당
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # username, password에 해당하는 사용자가 있는지 검사
            user = authenticate(username=username, password=password)

            # 해당 사용자가 있다면
            if user:
                # 로그인 처리 후, 피드 페이지로 redirect
                login(request, user)
                return redirect("/posts/feeds/")
            else:
                form.add_error(None, "입력한 자격증명에 해당하는 사용자가 없습니다. ")

        # 어떤 경우든 실패한 경우(데이터 검증, 사용자 검사 과정에서) 다시 LoginForm을 사용한 로그인 페이지 렌더링
        context = {"form": form}
        return render(request, "users/login.html", context)
    else:
        form = LoginForm()
        context = {"form": form}
        return render(request, "users/login.html", context)

def logout_view(request):
    logout(request)  # GET, POST 요청에 관계없이 동작한다.
    return redirect("/users/login/")  # 로그아웃 처리 후, 로그인 페이지로 이동한다.



def signup(request):
    # POST 요청 시, form이 유효하다면 최종적으로 redirect 처리된다
    if request.method == "POST":
        form = SignupForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)

            basicprofile_path = os.path.join(settings.MEDIA_ROOT, 'users/profile/basicProfile/basic.png')
            if os.path.isfile(basicprofile_path):
                os.remove(basicprofile_path)
            return redirect("/posts/feeds/")
        # POST 요청에서 form이 유효하지 않다면, 아래의 context = ... 부분으로 이동한다.

    # GET 요청 시, 빈 form을 생성한다.
    else:
        form = SignupForm()
    context = {"form": form}
    return render(request, "users/signup.html", context)

def profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    context = {
        "user": user,
    }
    return render(request, "users/profile.html", context)

def followers(request, user_id):
    user = get_object_or_404(User, id=user_id)
    relationships = user.follower_relationships.all()
    context = {
        "user": user,
        "relationships": relationships,
    }
    return render(request, "users/followers.html", context)

def following(request, user_id):
    user = get_object_or_404(User, id=user_id)
    relationships = user.following_relationships.all()
    context = {
        "user": user,
        "relationships": relationships,
    }
    return render(request, "users/following.html", context)

def follow(request, user_id):
    # 로그인한 유저
    user = request.user
    # 팔로우하려는 유저
    target_user = get_object_or_404(User, id=user_id)

    # 팔로우하려는 유저가 이미 자신의 팔로잉 목록에 있는 경우
    if target_user in user.following.all():
        # 팔로잉 목록에서 제거
        user.following.remove(target_user)

    # 팔로우하려는 유저가 자신의 팔로잉 목록에 없는 경우
    else:
        # 팔로잉 목록에 추가
        user.following.add(target_user)

    # 팔로우 토글 후 이동할 URL이 전달되었다면 해당 주소로,
    # 전달되지 않았다면 로그인 한 유저의 프로필 페이지로 이동
    url_next = request.GET.get("next") or reverse("users:profile", args=[user.id])
    return HttpResponseRedirect(url_next)
