from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserWallet
'''
@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'wallet'):
        UserWallet.create_wallet(user=instance)

# For existing users (run once during setup)
def assign_wallets_to_existing_users():
    for user in User.objects.all():
        if not hasattr(user, 'wallet'):
            UserWallet.create_wallet(user=user)
'''