from django.shortcuts import render, redirect, HttpResponse
from .models import Post, Comment, PostImage, HashTag
from .forms import CommentForm, PostForm
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from .image_parser import parse_images

def feeds(request):
    if not request.user.is_authenticated:
        return redirect("/users/login/")

    posts = Post.objects.all()
    comment_form = CommentForm()

    request.session.pop('selected_img_urls', None)
    context = {
        "posts": posts,
        "comment_form": comment_form,
        }
    
    return render(request, "posts/feeds.html", context)

@require_POST
def comment_add(request):
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.save()

        url_next = request.GET.get("next") or reverse("posts:feeds") + f"#post-{comment.post.id}"

        return HttpResponseRedirect(url_next)

@require_POST
def comment_delete(request, comment_id):
    comment = Comment.objects.get(id=comment_id)

    if comment.user == request.user:
        comment.delete()
        return HttpResponseRedirect(f"/posts/feeds/#post-{comment.post.id}")

    else:
        return HttpResponseForbidden("해당 댓글을 삭제할 권한이 없습니다")

def search_img(request):
    if request.method == "POST":
        keyword = request.POST['keyword'].strip()

        if len(keyword) > 0:
            cnt = int(request.POST['cnt'])
            request.session['img_url_list'] = parse_images(keyword, cnt)
            request.session['keyword'] = keyword
            return redirect('posts:select_img')

        else:
            context = {'error_message': "키워드를 다시 입력해주세요."}

    return render(request, 'posts/search_img.html')


def select_img(request):
    if request.method == "POST":
        request.session['selected_img_urls'] = request.POST.getlist('selectedImages', '')
        return redirect('posts:post_add')
    
    img_url_list = request.session.pop('img_url_list', '')
    keyword = request.session.pop('keyword', '')

    context = {
        "img_url_list": img_url_list,
        "keyword": keyword,
    }
    return render(request, 'posts/select_img.html', context)



def post_add(request):
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        local_image = request.FILES.getlist("images")
        selected_img_urls = request.session.pop('selected_img_urls', '')
        keyword = request.session.pop('keyword', '')
        print('진입 : ', selected_img_urls)

        if selected_img_urls or local_image:
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            for image_file in local_image:
                PostImage.objects.create(
                    post=post,
                    photo=image_file,
                )

            for selected_image_url in selected_img_urls:
                PostImage_instance = PostImage.objects.create(
                    post=post,
                    image_url=selected_image_url,
                ) 
                PostImage_instance.save_image_from_url(keyword, request.user)

            tag_string = request.POST.get("tags")  # input의 name값을 적으면 input값을 들고 온다.
            if tag_string:
                tag_names = [tag_name.strip() for tag_name in tag_string.split(",")]
                for tag_name in tag_names:
                    tag, _ = HashTag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)

            url = reverse("posts:feeds") + f"#post-{post.id}"
            return HttpResponseRedirect(url)

        else:
            context = {'error_message': "한 개 이상의 이미지가 필요합니다."}
            return render(request, "posts/post_add.html", context)

    form = PostForm()
    selected_img_urls = request.session.get('selected_img_urls', '')

    context = {
        "selected_img_urls": selected_img_urls,
        "form": form,
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



