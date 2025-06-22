from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Account

# This signal ensures that a bank account is created for a user upon approval
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account_on_approval(sender, instance, **kwargs):
    # Check if the user is approved and is a customer (not a staff/manager)
    if instance.is_approved and not instance.is_staff:
        # Check if an account does not already exist to prevent duplicates
        if not hasattr(instance, 'account'):
            Account.objects.create(user=instance)