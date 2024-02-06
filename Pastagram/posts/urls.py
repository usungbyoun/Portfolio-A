from django.urls import path
from .views import feeds, comment_add, comment_delete, post_add, tags, post_detail, post_like, img_select, test_add
from django.conf.urls.static import static
from django.conf import settings

app_name = "posts"
urlpatterns = [
    path("feeds/", feeds, name="feeds"),
    path("comment_add/", comment_add, name="comment_add"),
    path("comment_delete/<int:comment_id>", comment_delete, name="comment_delete"),
    path("post_add/", post_add, name="post_add"),
    path("tags/<str:tag_name>", tags, name="tags"),
    path("<int:post_id>/", post_detail, name="post_detail"),
    path("<int:post_id>/like/", post_like, name="post_like"),
    path("img_select/", img_select, name="img_select"),
    path("test_add/", test_add, name="test_add"),

]
