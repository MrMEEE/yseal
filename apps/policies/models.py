"""
SELinux Policy models for ySEal.
"""
import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel
from apps.contributors.models import Contributor

# PostgreSQL-specific imports (conditional)
USE_POSTGRES = os.getenv('USE_POSTGRES', 'False') == 'True'

if USE_POSTGRES:
    from django.contrib.postgres.fields import ArrayField
    from django.contrib.postgres.search import SearchVectorField
    from django.contrib.postgres.indexes import GinIndex
else:
    # SQLite fallbacks
    ArrayField = None
    SearchVectorField = None
    GinIndex = None


class Tag(TimeStampedModel):
    """
    Tags for categorizing policies.
    """
    name = models.SlugField(_('name'), max_length=50, unique=True)
    
    class Meta:
        db_table = 'tags'
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name']

    def __str__(self):
        return self.name


class Policy(TimeStampedModel):
    """
    Main Policy model representing a SELinux policy collection.
    """
    contributor = models.ForeignKey(
        Contributor,
        on_delete=models.CASCADE,
        related_name='policies'
    )
    name = models.SlugField(
        _('name'),
        max_length=100,
        help_text=_('Policy name (lowercase, alphanumeric, hyphens)')
    )
    display_name = models.CharField(_('display name'), max_length=200)
    description = models.TextField(_('description'))
    
    # Repository info
    repository_url = models.URLField(_('repository URL'))
    repository_branch = models.CharField(_('repository branch'), max_length=100, default='main')
    
    # Documentation
    readme = models.TextField(_('README'), blank=True)
    documentation_url = models.URLField(_('documentation URL'), blank=True)
    
    # Metadata
    tags = models.ManyToManyField(Tag, related_name='policies', blank=True)
    license = models.CharField(_('license'), max_length=100, blank=True)
    
    # Statistics
    download_count = models.IntegerField(_('download count'), default=0)
    star_count = models.IntegerField(_('star count'), default=0)
    
    # Status
    is_deprecated = models.BooleanField(_('deprecated'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Search (PostgreSQL only)
    if USE_POSTGRES and SearchVectorField:
        search_vector = SearchVectorField(null=True, blank=True)
    
    class Meta:
        db_table = 'policies'
        verbose_name = _('policy')
        verbose_name_plural = _('policies')
        unique_together = [['contributor', 'name']]
        ordering = ['-download_count', '-created_at']
        
        # Build indexes conditionally
        indexes = [
            models.Index(fields=['contributor', 'name']),
            models.Index(fields=['is_deprecated', 'is_active']),
        ]
        if USE_POSTGRES and GinIndex and SearchVectorField:
            indexes.insert(0, GinIndex(fields=['search_vector']))

    def __str__(self):
        return f"{self.contributor.name}.{self.name}"

    @property
    def full_name(self):
        """Returns the full policy name (contributor.name)."""
        return f"{self.contributor.name}.{self.name}"


class PolicyVersion(TimeStampedModel):
    """
    Specific version of a policy.
    """
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version = models.CharField(
        _('version'),
        max_length=50,
        help_text=_('Semantic version (e.g., 1.0.0)')
    )
    
    # Git information
    git_commit = models.CharField(_('git commit SHA'), max_length=40)
    git_tag = models.CharField(_('git tag'), max_length=100, blank=True)
    
    # Metadata
    changelog = models.TextField(_('changelog'), blank=True)
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    # Files
    archive_url = models.URLField(_('archive URL'), blank=True)
    archive_size = models.IntegerField(_('archive size (bytes)'), default=0)
    checksum = models.CharField(_('SHA256 checksum'), max_length=64, blank=True)
    
    # Dependencies
    dependencies = models.JSONField(_('dependencies'), default=list, blank=True)
    
    # SELinux specific
    selinux_version = models.CharField(_('SELinux version'), max_length=50, blank=True)
    
    # Supported systems - PostgreSQL uses ArrayField, SQLite uses JSONField
    if USE_POSTGRES and ArrayField:
        supported_systems = ArrayField(
            models.CharField(max_length=100),
            blank=True,
            default=list,
            verbose_name=_('supported systems'),
            help_text=_('e.g., ["RHEL 8", "RHEL 9", "Fedora 38"]')
        )
    else:
        supported_systems = models.JSONField(
            _('supported systems'),
            default=list,
            blank=True,
            help_text=_('e.g., ["RHEL 8", "RHEL 9", "Fedora 38"]')
        )
    
    # Status
    is_latest = models.BooleanField(_('is latest'), default=False)
    download_count = models.IntegerField(_('download count'), default=0)
    
    class Meta:
        db_table = 'policy_versions'
        verbose_name = _('policy version')
        verbose_name_plural = _('policy versions')
        unique_together = [['policy', 'version']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['policy', 'version']),
            models.Index(fields=['is_latest']),
        ]

    def __str__(self):
        return f"{self.policy.full_name} v{self.version}"

    def save(self, *args, **kwargs):
        """Override save to update is_latest flag."""
        if self.is_latest:
            # Set all other versions of this policy to not latest
            PolicyVersion.objects.filter(
                policy=self.policy,
                is_latest=True
            ).exclude(id=self.id).update(is_latest=False)
        super().save(*args, **kwargs)


class PolicyFile(TimeStampedModel):
    """
    Individual files within a policy version.
    """
    version = models.ForeignKey(
        PolicyVersion,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file_path = models.CharField(_('file path'), max_length=500)
    file_type = models.CharField(
        _('file type'),
        max_length=10,
        choices=[
            ('te', 'Type Enforcement (.te)'),
            ('fc', 'File Contexts (.fc)'),
            ('if', 'Interface (.if)'),
            ('pp', 'Policy Package (.pp)'),
            ('cil', 'Common Intermediate Language (.cil)'),
            ('other', 'Other'),
        ],
        default='other'
    )
    content = models.TextField(_('content'), blank=True)
    size = models.IntegerField(_('size (bytes)'), default=0)
    
    class Meta:
        db_table = 'policy_files'
        verbose_name = _('policy file')
        verbose_name_plural = _('policy files')
        ordering = ['file_path']

    def __str__(self):
        return f"{self.version} - {self.file_path}"


class DownloadLog(TimeStampedModel):
    """
    Track policy downloads for analytics.
    """
    policy = models.ForeignKey(Policy, on_delete=models.CASCADE, related_name='downloads')
    version = models.ForeignKey(PolicyVersion, on_delete=models.CASCADE, related_name='downloads')
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'), blank=True)
    
    class Meta:
        db_table = 'download_logs'
        verbose_name = _('download log')
        verbose_name_plural = _('download logs')
        indexes = [
            models.Index(fields=['policy', 'created_at']),
            models.Index(fields=['version', 'created_at']),
        ]

    def __str__(self):
        return f"{self.policy.full_name} v{self.version.version} - {self.created_at}"
