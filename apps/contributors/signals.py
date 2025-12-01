"""
Signals for automatic personal contributor profile creation.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Contributor

User = get_user_model()


@receiver(post_save, sender=User)
def create_personal_contributor(sender, instance, created, **kwargs):
    """
    Automatically create a personal Contributor profile when a new User is created.
    Each user gets their own personal contributor with their username as the name.
    """
    if created:
        # Generate slug from username
        slug = instance.username.lower().replace('_', '-')
        
        # Check if a contributor with this name already exists
        if not Contributor.objects.filter(name=slug).exists():
            contributor = Contributor.objects.create(
                name=slug,
                display_name=instance.get_full_name() or instance.username,
                email=instance.email,
                is_personal=True
            )
            # Add the user as the owner
            contributor.owners.add(instance)
