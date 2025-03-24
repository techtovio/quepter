from django.urls import path
from . import views

urlpatterns = [
    path('comment/add/<uuid:uuid>/', views.post_comment, name='addComment'),
    path('post/create/', views.create_post, name="create-post"),
    path('like-post/', views.like_post_ajax, name='likePostAjax'),
    path('delete-post/<uuid:uuid>/', views.deletePost, name='deletePost'),
    path('edit-post/<uuid:uuid>/', views.editPost, name='editPost'),
    path('add-comment/<uuid:uuid>/', views.add_comment_ajax, name='addCommentAjax'),
    path('post/comments/<uuid:uuid>/', views.post_detail, name='postComments'),
    path('edit/post/<uuid:uuid>/', views.editPostView, name='editPostView'),
]