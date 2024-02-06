from django.shortcuts import render, redirect, HttpResponse
from .models import Post, Comment, PostImage, HashTag
from .forms import CommentForm, PostForm
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse

import requests
import urllib
from bs4 import BeautifulSoup as bs

def feeds(request):
    # 요청에 포함된 사용자가 로그인하지 않은 경우
    if not request.user.is_authenticated:
        return redirect("/users/login/")

    # 모든 글 목록을 템플릿으로 전달
    posts = Post.objects.all()
    comment_form = CommentForm()
    context = {
        "posts": posts,
        "comment_form": comment_form,
               }
    return render(request, "posts/feeds.html", context)

@require_POST   # 댓글 작성을 처리할 View, Post 요청만 허용한다.
def comment_add(request):
    # request.POST로 전달된 데이터를 사용해 CommentForm 인스턴스를 생성
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # commit=False 옵션으로 메모리상에 Comment 객체 생성
        comment = form.save(commit=False)

        # Comment 생성에 필요한 사용자 정보를 request에서 가져와 할당
        comment.user = request.user

        # DB에 Comment 객체 저장
        comment.save()

        # URL로 'next' 값을 전달받았다면, 댓글 작성 완료 후 전달받은 값으로 이동한다
        url_next = request.GET.get("next") or reverse("posts:feeds") + f"#post-{comment.post.id}"
        return HttpResponseRedirect(url_next)

@require_POST
def comment_delete(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.user == request.user:
        comment.delete()
        return HttpResponseRedirect(f"/posts/feeds/#post-{comment.post.id}")
    else:
        return HttpResponseForbidden("이 댓글을 삭제할 권한이 없습니다")

selected_image_urls = []
keyword = ''
def post_add(request):
    global selected_image_urls
    global keyword

    if 'img_select' in request.META.get('HTTP_REFERER', ''):
        selected_image_urls = request.POST.getlist('selectedImages')
        keyword = request.POST.get('keyword')

    elif 'feeds' in request.META.get('HTTP_REFERER', ''):
        selected_image_urls = []

    if request.method == "POST":
        # request.POST로 온 데이터 ("content")는 PostForm으로 처리
        form = PostForm(request.POST, request.FILES)
        submit = request.POST.get('submit_check', '')

        if submit == "submit" and form.is_valid():

            # Post의 "user" 값은 request에서 가져와 자동 할당한다.
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            print("aaa:", request.FILES.getlist("images"))
            # Post를 생성한 후
            # request.FILES.getlist("images")로 전송된 이미지들을 순회하며 PostImage 객체를 생성한다.
            for image_file in request.FILES.getlist("images"):
                # request.FILES 또는 request.FILES.getlist()로 가져온 파일은
                # Model의 imageField 부분에 곧바로 할당한다.

                PostImage.objects.create(
                    post=post,
                    photo=image_file,
                )

            for selected_image_url in selected_image_urls:
                my_model_instance = PostImage.objects.create(
                    post=post,
                    image_url=selected_image_url,
                )
                my_model_instance.save_image_from_url(keyword, request.user)

            tag_string = request.POST.get("tags")  # input의 name값을 적으면 input값을 들고 온다.
            if tag_string:
                tag_names = [tag_name.strip() for tag_name in tag_string.split(",")]
                for tag_name in tag_names:
                    tag, _ = HashTag.objects.get_or_create(name=tag_name)
                    # get_or_create로 생성하거나 가져온 HashTag 객체를 Post의 tags에 추가한다
                    post.tags.add(tag)

            url = reverse("posts:feeds") + f"#post-{post.id}"
            return HttpResponseRedirect(url)

    # GET 요청일 때는 빈 form을 보여주도록 한다.
    else:
        form = PostForm()

    context = {"form": form,
               "selected_image_urls": selected_image_urls,

               }
    return render(request, "posts/post_add.html", context)

def tags(request, tag_name):
    try:
        # HTML에서 요청한 해시태그(tag_name)에 해당하는 HashTag모델(DB)의 객체를 불러옴
        tag = HashTag.objects.get(name=tag_name)
    except HashTag.DoesNotExist:
        # tag_name에 해당하는 HashTag를 찾지 못한 경우, 빈 쿼리셋을 돌려준다.
        posts = Post.objects.none()
    else:   # 찾은경우 태그된 Post의 쿼리셋을 불러온다.
        posts = Post.objects.filter(tags=tag)

    context = {
        "tag_name": tag_name,
        "posts": posts,
    }
    return render(request, 'posts/tags.html', context)

def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    comment_form = CommentForm()
    context = {
        "post": post,
        "comment_form": comment_form,
    }
    return render(request, "posts/post_detail.html", context)

def post_like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = request.user

    # 사용자가 "좋아료를 누른 Post 목록"에 "좋아요 버튼을 누른 Post"가 존재한다면
    if user.like_posts.filter(id=post.id).exists():
        # 좋아요 목록에서 삭제한다
        user.like_posts.remove(post)
    # 존재하지 않는다면 좋아요 목록에 추가한다
    else:
        user.like_posts.add(post)



    # next로 값이 전달되었다면 해당 위치로, 전달되지 않았다면 피드 페이지에서 해당 Post 위치로 이동한다.
    url_next = request.GET.get("next") or reverse("posts:feeds") + f"#post-{post.id}"
    return HttpResponseRedirect(url_next)




def img_select(request):
    img_url_list = []

    if request.method == "POST":
        if request.POST['keyword'] != "":
            keyword = request.POST['keyword']
            cnt = int(request.POST['cnt'])

            print(keyword)
            print(cnt)

            keyword_quote = urllib.parse.quote(keyword)
            url = 'https://images.search.yahoo.com/search/images;_ylt=Awr9IlCx7FdgSIEAGZJXNyoA;_ylu==Y29sbwNncTEEcG9zAzEEdnRpZANDMDE2MF8xBHNlYwNwaXZz?p='
            url = url + keyword_quote + '&fr2=piv-web&fr=yfp-t'
            response = requests.get(url)
            soup = bs(response.text, 'html.parser')
            tag_imgs = soup.select('li.ld a > img')

            for tag_img in tag_imgs:
                img_url_list.append(tag_img.attrs['data-src'])

            context = {
                "img_url_list": img_url_list[:cnt],
                "keyword": keyword,
            }
        else:
            context = {}
            print('aa')
    else:
        context = {}
        print('bb')

    print('cc')

    return render(request, 'posts/img_select.html', context)


def test_add(request):
    pass
    # if request.method == 'POST':
    #     selected_image_urls = request.POST.getlist('selectedImages')
    #     print(selected_image_urls)
    #
    # return render(request, 'posts/img_select.html')
        # 여기에서 선택된 이미지의 URL을 처리하거나 다른 로직을 수행할 수 있습니다.
        # json으로 처리
        # return JsonResponse({'message': 'Success', 'selected_image_urls': selected_image_urls})
