from django.db import models
from dashboard.models import Profile, Notification
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User