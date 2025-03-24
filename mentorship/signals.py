from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import MentorshipMessage, GroupMentorship, MentorshipTransaction, Profile

# Deduct points when messaging a mentor in one-on-one mentorship
@receiver(post_save, sender=MentorshipMessage)
def deduct_points_for_message(sender, instance, **kwargs):
    if instance.mentorship:
        profile = instance.sender.profile
        points_to_deduct = 1.0  # Deduct 1 point for messaging
        if profile.points >= points_to_deduct:
            profile.points -= points_to_deduct
            profile.save()

            # Log the deduction
            MentorshipTransaction.objects.create(
                user=instance.sender,
                mentorship_type='one-on-one',
                points_deducted=points_to_deduct
            )

# Deduct points when joining group mentorship
@receiver(m2m_changed, sender=GroupMentorship.members.through)
def deduct_points_on_join_group(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            user = User.objects.get(pk=pk)
            profile = user.profile
            points_to_deduct = instance.points_required
            if profile.points >= points_to_deduct:
                profile.points -= points_to_deduct
                profile.save()

                # Log the deduction
                MentorshipTransaction.objects.create(
                    user=user,
                    mentorship_type='group',
                    points_deducted=points_to_deduct
                )
