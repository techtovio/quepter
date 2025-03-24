from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import  Profile
from post.models import CommunityPostLike
from dashboard.models import Funding
from decimal import Decimal
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=CommunityPostLike)
def award_points_on_like(sender, instance, **kwargs):
    post = instance.post
    likes_count = post.likes()
    points_awarded = likes_count // 25  # 25 likes = 1 point

    # Update the user's profile with the new points
    profile, created = Profile.objects.get_or_create(user=post.author)
    profile.points = points_awarded
    profile.save()


@receiver(post_save, sender=Funding)
def update_user_points(sender, instance, **kwargs):
    if instance.status == "Completed":  # Only award points for completed funding
        points_earned = int(instance.amount / 2)  # 1 point per KES 2
        profile, created = Profile.objects.get_or_create(user=instance.user)
        profile.points += points_earned
        profile.save()