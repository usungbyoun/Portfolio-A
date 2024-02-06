from django.db import models
from django.contrib.auth.models import AbstractUser # 추가
import os
from django.conf import settings

class User(AbstractUser):

    def get_upload_path(self, filename):
        # 파일 이름이 "profile_basic.png"이면 업로드를 거부
        if filename == 'profile_basic':
            return f'users/profile/basicProfile/basic_{self.username}.png'
        else:
            return f'users/profile/profile_{self.username}.png'

    profile_image = models.ImageField("프로필 이미지", upload_to=get_upload_path, blank=True)
    short_description = models.TextField("소개글", null=True, blank=True)
    like_posts = models.ManyToManyField(
        "posts.Post",
        verbose_name="좋아요 누른 Post 목록",
        related_name="like_users",
        blank=True,
    )
    following = models.ManyToManyField(
        "self",
        verbose_name="팔로우 중인 사용자들",
        related_name="followers",
        symmetrical=False,
        through="users.Relationship",
    )


    def __str__(self):
        return self.username



class Relationship(models.Model):
    from_user = models.ForeignKey(
        "users.User",
        verbose_name="팔로우를 요청한 사용자",
        related_name="following_relationships",
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        "users.User",
        verbose_name="팔로우 요청의 대상",
        related_name="follower_relationships",
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"관계 ({self.from_user} -> {self.to_user})"
