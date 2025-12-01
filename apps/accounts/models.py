"""
User models for ySEal.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel


class User(AbstractUser):
    """
    Custom User model for ySEal.
    Extends Django's AbstractUser with additional fields.
    """
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(_('biography'), max_length=500, blank=True)
    avatar_url = models.URLField(_('avatar URL'), blank=True)
    github_id = models.CharField(_('GitHub ID'), max_length=100, blank=True, unique=True, null=True)
    company = models.CharField(_('company'), max_length=200, blank=True)
    location = models.CharField(_('location'), max_length=100, blank=True)
    website = models.URLField(_('website'), blank=True)
    
    # Permissions
    is_verified = models.BooleanField(_('verified'), default=False)
    can_create_contributor = models.BooleanField(_('can create contributor'), default=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UserProfile(TimeStampedModel):
    """
    Extended profile information for users.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    notification_preferences = models.JSONField(default=dict, blank=True)
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return f"Profile for {self.user.username}"
