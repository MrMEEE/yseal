"""
Contributor models for organizing SELinux policies.
Contributors can have multiple owners, and users can own multiple contributors.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel

User = get_user_model()


class Contributor(TimeStampedModel):
    """
    Contributor model - represents a policy contributor/organization.
    Has a many-to-many relationship with User model (owners).
    Similar to Ansible Galaxy namespaces but called contributors.
    Normal users get their own personal contributor auto-created.
    Admins can create organization contributors with multiple owners.
    """
    name = models.SlugField(
        _('name'),
        max_length=100,
        unique=True,
        help_text=_('Unique contributor identifier (lowercase, alphanumeric, hyphens)')
    )
    display_name = models.CharField(_('display name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    avatar_url = models.URLField(_('avatar URL'), blank=True)
    company = models.CharField(_('company'), max_length=200, blank=True)
    website = models.URLField(_('website'), blank=True)
    email = models.EmailField(_('email'), blank=True)
    
    # Ownership - multiple users can own a contributor
    owners = models.ManyToManyField(
        User,
        related_name='owned_contributors',
        verbose_name=_('owners')
    )
    
    # Stats
    policy_count = models.IntegerField(_('policy count'), default=0)
    download_count = models.IntegerField(_('download count'), default=0)
    
    # Metadata
    is_verified = models.BooleanField(_('verified'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_personal = models.BooleanField(_('personal contributor'), default=False, 
                                      help_text=_('True if this is a personal contributor for a single user'))
    
    class Meta:
        db_table = 'contributors'
        verbose_name = _('contributor')
        verbose_name_plural = _('contributors')
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def add_owner(self, user):
        """Add a user as an owner of this contributor."""
        self.owners.add(user)

    def remove_owner(self, user):
        """Remove a user from contributor owners."""
        self.owners.remove(user)

    def is_owner(self, user):
        """Check if a user is an owner of this contributor."""
        return self.owners.filter(id=user.id).exists()


class ContributorLink(TimeStampedModel):
    """
    External links associated with a contributor (GitHub, Docs, etc.).
    """
    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name='links'
    )
    name = models.CharField(_('name'), max_length=100)
    url = models.URLField(_('URL'))
    
    class Meta:
        db_table = 'contributor_links'
        verbose_name = _('contributor link')
        verbose_name_plural = _('contributor links')
        ordering = ['name']

    def __str__(self):
        return f"{self.contributor.name} - {self.name}"
