from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserChallengeParticipation, Leaderboard

@receiver(post_save, sender=UserChallengeParticipation)
def update_leaderboard(sender, instance, created, **kwargs):
    if instance.completed:
        leaderboard_entry, _ = Leaderboard.objects.get_or_create(user=instance.user)
        leaderboard_entry.points += instance.challenge.points_awarded
        leaderboard_entry.save()
