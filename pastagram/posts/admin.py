from django.contrib import admin
from .models import Post, PostImage, Comment, HashTag
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple
import admin_thumbnails

class CommentInline(admin.TabularInline):
    model = Comment # Post와 연결될 모델
    extra = 1       # 개수

@admin_thumbnails.thumbnail("photo")
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1

class LikeUserInline(admin.TabularInline):
    model = Post.like_users.through
    verbose_name = "좋아요 한 User"
    verbose_name_plural = f"{verbose_name} 목록"
    extra = 1

    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "content",
    ]
    inlines = [
        CommentInline,
        PostImageInline,
        LikeUserInline,
    ]


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "post",
        "photo",
    ]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "post",
        "content",
    ]

@admin.register(HashTag)
class HashTagAdmin(admin.ModelAdmin):
    # Post 변경 화면에서 ManyToManyField를 체크박스로 출력 (formfield_overrides 옵션을 추가하면 선택할 항목을 체크박스로 표시할 수 있다.)
    formfield_overrides = {
        ManyToManyField: {"widget": CheckboxSelectMultiple},
    }