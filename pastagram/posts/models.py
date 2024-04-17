from django.db import models
from django.core.files import File
from tempfile import NamedTemporaryFile
import requests

class Post(models.Model):
    user = models.ForeignKey(
        "users.User",
        verbose_name="작성자",
        on_delete=models.CASCADE,
    )
    content = models.TextField("내용", blank=True, null=True)
    created = models.DateTimeField("생성일시", auto_now_add=True)
    tags = models.ManyToManyField("posts.HashTag", verbose_name="해시태그 목록", blank=True)

    def __str__(self):
        return f"{self.user.username}의 Post(id: {self.id})"

class PostImage(models.Model):

    post = models.ForeignKey(
        Post,
        verbose_name="포스트",
        on_delete=models.CASCADE,
    )
    photo = models.ImageField("사진", upload_to="post")
    image_url = models.URLField(blank=True, null=True)


    def save_image_from_url(self, keyword, user):
        response = requests.get(self.image_url)
        if response.status_code == 200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.content)
            img_temp.flush()
            self.photo.save(f"{user}_{keyword}_image.jpg", File(img_temp), save=True)


class Comment(models.Model):
    user = models.ForeignKey(
        "users.User",
        verbose_name="작성자",
        on_delete=models.CASCADE,   # 한 줄 건너뛰어서 괄호를 닫았으니 ,을 찍어야 한다.
    )
    post = models.ForeignKey(Post, verbose_name="포스트", on_delete=models.CASCADE) # 바로 닫았으니 , 필요없음
    content = models.TextField("내용")
    created = models.DateTimeField("생성일시", auto_now_add=True)

class HashTag(models.Model):
    name = models.CharField("태그명", max_length=50)

    def __str__(self):
        return self.name
