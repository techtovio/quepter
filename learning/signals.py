from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.signals import post_save
from .models import Ebook
from dashboard.models import Profile 

@receiver(m2m_changed, sender=Ebook)
def update_points_on_ebook_interaction(sender, instance, action, **kwargs):
    if action == 'post_add':
        user = instance.user  # Assume you have the user from the session or interaction
        profile = Profile.objects.get(user=user)

        if instance.is_free:
            # For free ebooks, 10 ebooks = 1 point
            profile.points += 0.1
        else:
            # For paid ebooks, 1 paid ebook = 5 point
            profile.points += 5
        
        profile.save()

@receiver(post_save, sender=Ebook)
def update_points_for_author(sender, instance, created, **kwargs):
    if created:
        author_profile = Profile.objects.get(user=instance.author)
        author_profile.points += 1  # Award 1 point for uploading an ebook
        author_profile.save()
