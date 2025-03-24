from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid
import string
import random
from datetime import datetime, timedelta

class Event(models.Model):
    title = models.CharField(max_length=800)
    image = models.ImageField(blank=False, null=False, upload_to='events')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    date = models.DateField()
    is_completed = models.BooleanField(default=False)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.title