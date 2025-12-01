"""
Serializers for the policies app, based on Ansible Galaxy patterns.
"""
from django.db.models import Avg
from rest_framework import serializers
from .models import Policy, PolicyVersion, PolicyFile, Tag, DownloadLog
from apps.contributors.models import Contributor
from apps.voting.models import Rating


class ContributorSerializer(serializers.ModelSerializer):
    """Serializer for Contributor model"""
    owners = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Contributor
        fields = ['name', 'display_name', 'company', 'description', 'email', 'avatar_url', 'is_verified', 'is_personal', 'owners', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'is_verified']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    class Meta:
        model = Tag
        fields = ['name']


class PolicyVersionListSerializer(serializers.ModelSerializer):
    """Serializer for listing policy versions"""
    class Meta:
        model = PolicyVersion
        fields = ['version', 'created_at']


class PolicyListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing policies (similar to CollectionListSerializer).
    Used in browse/search views.
    """
    contributor = serializers.CharField(source='contributor.name')
    tags = TagSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()
    download_count = serializers.IntegerField(read_only=True, default=0)
    is_deprecated = serializers.BooleanField(read_only=True, default=False)
    
    class Meta:
        model = Policy
        fields = [
            'id',
            'contributor',
            'name',
            'description',
            'latest_version',
            'tags',
            'download_count',
            'is_deprecated',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_version(self, obj):
        """Get the latest version for this policy"""
        latest = obj.versions.order_by('-created_at').first()
        if latest:
            return {
                'version': latest.version,
                'created_at': latest.created_at.isoformat()
            }
        return None


class PolicyFileSerializer(serializers.ModelSerializer):
    """Serializer for policy files"""
    class Meta:
        model = PolicyFile
        fields = ['name', 'content', 'created_at']
        read_only_fields = ['created_at']


class PolicyVersionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a specific policy version.
    """
    policy = serializers.CharField(source='policy.name', read_only=True)
    contributor = serializers.CharField(source='policy.contributor.name', read_only=True)
    files = PolicyFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = PolicyVersion
        fields = [
            'id',
            'policy',
            'contributor',
            'version',
            'changelog',
            'requires_reboot',
            'selinux_contexts',
            'files',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PolicyDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for a policy (similar to CollectionDetailSerializer).
    Shows all versions and metadata.
    """
    contributor = ContributorSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    versions = PolicyVersionListSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()
    download_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Policy
        fields = [
            'id',
            'contributor',
            'name',
            'description',
            'latest_version',
            'versions',
            'tags',
            'download_count',
            'average_rating',
            'is_deprecated',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_version(self, obj):
        """Get the latest version for this policy"""
        latest = obj.versions.order_by('-created_at').first()
        if latest:
            return PolicyVersionDetailSerializer(latest).data
        return None
    
    def get_download_count(self, obj):
        """Calculate total download count"""
        return DownloadLog.objects.filter(
            policy_version__policy=obj
        ).count()
    
    def get_average_rating(self, obj):
        """Calculate average rating"""
        ratings = Rating.objects.filter(policy=obj)
        if ratings.exists():
            return ratings.aggregate(avg=Avg('score'))['avg']
        return None


class SearchResultsSerializer(serializers.Serializer):
    """
    Serializer for search results (similar to galaxy_ng SearchResultsSerializer).
    Combines policy metadata with search relevance.
    """
    id = serializers.IntegerField()
    contributor = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    latest_version = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField())
    download_count = serializers.IntegerField()
    is_deprecated = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    relevance = serializers.FloatField(required=False)
    content_type = serializers.CharField(default='policy')


class PolicyUploadSerializer(serializers.Serializer):
    """
    Serializer for policy package uploads.
    """
    file = serializers.FileField()
    contributor = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=100)
    version = serializers.CharField(max_length=50)
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Check file extension
        if not value.name.endswith(('.tar.gz', '.zip')):
            raise serializers.ValidationError("File must be .tar.gz or .zip")
        
        return value
    
    def validate_contributor(self, value):
        """Validate contributor exists"""
        if not Contributor.objects.filter(name=value).exists():
            raise serializers.ValidationError(f"Contributor '{value}' does not exist")
        return value


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for policy ratings"""
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'user', 'policy', 'score', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class DownloadLogSerializer(serializers.ModelSerializer):
    """Serializer for download logs"""
    policy = serializers.CharField(source='policy_version.policy.name', read_only=True)
    version = serializers.CharField(source='policy_version.version', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = DownloadLog
        fields = ['id', 'policy', 'version', 'user', 'downloaded_at']
        read_only_fields = ['id', 'downloaded_at']
