from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import ClubMembership, ClubBroadcast
from dashboard.models import Profile, Notification

@receiver(post_save, sender=ClubBroadcast)
def notify_club_members(sender, instance, **kwargs):
    """Notify all club members when a new broadcast is created."""
    club_members = instance.club.members.all()
    # Assuming there's a Notification model or method to notify users
    for member in club_members:
        Notification.objects.create(
            user=member,
            message=f"New message from {instance.club.name}: {instance.message}",
            title = f"New message from {instance.club.name}"
        )
