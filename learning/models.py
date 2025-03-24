from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4


def gen_uuid():
    return uuid4()

class Ebook(models.Model):
    TITLE_MAX_LENGTH = 200
    
    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True)
    description = models.TextField()
    file = models.FileField(upload_to='ebooks/')
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Only used for paid ebooks
    author = models.ForeignKey(User, related_name='uploaded_ebooks', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LearningResource(models.Model):
    RESOURCE_TYPES = (
        ('ebook', 'Ebook'),
        ('video', 'Video'),
    )
    ACCESS_TYPES = (
        ('free', 'Free'),
        ('paid', 'Paid'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    uuid = models.UUIDField(default=gen_uuid, editable=False, unique=True)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPES)
    access_type = models.CharField(max_length=10, choices=ACCESS_TYPES)
    file = models.FileField(upload_to='resources/')  # For ebooks
    image = models.ImageField(upload_to='resource-images/', blank=True, null=True)
    video_link = models.URLField(null=True, blank=True)  # For videos
    price = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)  # For paid resources
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.title
