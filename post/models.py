from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
import string
import random
from datetime import datetime, timedelta


CATEGORY_CHOICES = [
    ('education', 'Education & Learning'),
    ('business', 'Business & Entrepreneurship'),
    ('technology', 'Technology & Innovation'),
    ('creative', 'Creative Arts & Media'),
    ('health', 'Health & Wellness'),
    ('sports', 'Sports & Recreation'),
    ('finance', 'Finance & Investment'),
    ('social', 'Social Impact & Community Service'),
    ('environment', 'Environment & Sustainability'),
]

# Terms and conditions for each category
CATEGORY_TERMS = {
    'education': "Focuses on academic discussions, online courses, and study groups.",
    'business': "Encourages startup ideas, business strategies, and entrepreneurship networking.",
    'technology': "Explores tech trends, software development, and innovation in AI and machine learning.",
    'creative': "Promotes art, music, media production, and other creative endeavors.",
    'health': "Centers around mental and physical wellness, fitness, and health resources.",
    'sports': "Engages in sports activities, discussions, and events.",
    'finance': "Covers investment strategies, financial literacy, and cryptocurrency.",
    'social': "Focuses on community service, volunteering, and social impact projects.",
    'environment': "Dedicated to environmental awareness, conservation, and sustainability projects."
}

def gen_uuid():
    return uuid4()

class CommunityPost(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=1000, default="Entrepreneurship", choices=CATEGORY_CHOICES)
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    def likes(self):
        return CommunityPostLike.objects.filter(post=self).count()
    
    def comments(self):
        return CommunityPostComment.objects.filter(post=self)

    def __str__(self):
        return self.title
    
class CommunityPostComment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title} - {self.comment} - {self.user.first_name}"
    
class CommunityPostLike(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title}"