from django.contrib import admin
from post.models import CommunityPost, CommunityPostComment, CommunityPostLike

admin.site.register(CommunityPost)
admin.site.register(CommunityPostComment)
admin.site.register(CommunityPostLike)