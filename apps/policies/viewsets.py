"""
ViewSets for the policies app, based on Ansible Galaxy architecture.
"""
from django.db.models import Q, Count, Avg, OuterRef, Exists, Subquery
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination

from .models import (
    Policy, PolicyVersion, PolicyFile, Tag, DownloadLog
)
from apps.contributors.models import Contributor
from apps.voting.models import Vote, Rating
from .serializers import (
    PolicyListSerializer, PolicyDetailSerializer,
    PolicyVersionDetailSerializer, PolicyVersionListSerializer,
    ContributorSerializer, TagSerializer, RatingSerializer,
    PolicyUploadSerializer, DownloadLogSerializer,
    SearchResultsSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination similar to galaxy_ng"""
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100


class PolicyFilter(filters.FilterSet):
    """Filter class for policies (similar to galaxy_ng CollectionFilter)"""
    contributor = filters.CharFilter(field_name='contributor__name')
    name = filters.CharFilter(lookup_expr='icontains')
    is_deprecated = filters.BooleanFilter()
    tags = filters.CharFilter(method='filter_tags')
    
    class Meta:
        model = Policy
        fields = ['contributor', 'name', 'is_deprecated']
    
    def filter_tags(self, queryset, name, value):
        """Filter by tag names"""
        tags = value.split(',')
        for tag in tags:
            queryset = queryset.filter(tags__name__iexact=tag.strip())
        return queryset


class PolicyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing and retrieving policies.
    Similar to galaxy_ng CollectionViewSet.
    
    Endpoints:
    - GET /api/v1/policies/ - List all policies
    - GET /api/v1/policies/{id}/ - Get policy details
    - GET /api/v1/policies/{contributor}/{name}/ - Get policy by contributor and name
    - GET /api/v1/policies/{contributor}/{name}/versions/ - List policy versions
    - GET /api/v1/policies/{contributor}/{name}/versions/{version}/ - Get specific version
    """
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filterset_class = PolicyFilter
    lookup_field = 'id'
    
    def get_queryset(self):
        """Get queryset with annotations for downloads and tags"""
        queryset = Policy.objects.select_related('contributor').prefetch_related('tags', 'versions')
        
        # Annotate with download count
        download_count = DownloadLog.objects.filter(
            policy_version__policy=OuterRef('pk')
        ).values('policy_version__policy').annotate(
            count=Count('id')
        ).values('count')
        
        queryset = queryset.annotate(
            download_count=Subquery(download_count)
        )
        
        return queryset.order_by('-updated_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return PolicyDetailSerializer
        return PolicyListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a policy by ID or by contributor/name.
        Supports: /api/v1/policies/123/ or /api/v1/policies/contributor/policyname/
        """
        # Check if we're looking up by contributor/name
        if 'contributor' in kwargs and 'name' in kwargs:
            try:
                policy = Policy.objects.get(
                    contributor__name=kwargs['contributor'],
                    name=kwargs['name']
                )
                serializer = self.get_serializer(policy)
                return Response(serializer.data)
            except Policy.DoesNotExist:
                return Response(
                    {'detail': f"Policy {kwargs['contributor']}/{kwargs['name']} not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path=r'(?P<contributor>[^/]+)/(?P<name>[^/]+)/versions')
    def versions(self, request, contributor=None, name=None):
        """
        List all versions for a specific policy.
        GET /api/v1/policies/{contributor}/{name}/versions/
        """
        try:
            policy = Policy.objects.get(contributor__name=contributor, name=name)
            versions = policy.versions.all().order_by('-created_at')
            serializer = PolicyVersionListSerializer(versions, many=True)
            return Response({
                'meta': {'count': versions.count()},
                'data': serializer.data
            })
        except Policy.DoesNotExist:
            return Response(
                {'detail': f"Policy {contributor}/{name} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(
        detail=False, 
        methods=['get'], 
        url_path=r'(?P<contributor>[^/]+)/(?P<name>[^/]+)/versions/(?P<version>[^/]+)'
    )
    def version_detail(self, request, contributor=None, name=None, version=None):
        """
        Get details for a specific policy version.
        GET /api/v1/policies/{contributor}/{name}/versions/{version}/
        """
        try:
            policy = Policy.objects.get(contributor__name=contributor, name=name)
            policy_version = policy.versions.get(version=version)
            serializer = PolicyVersionDetailSerializer(policy_version)
            return Response(serializer.data)
        except Policy.DoesNotExist:
            return Response(
                {'detail': f"Policy {contributor}/{name} not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PolicyVersion.DoesNotExist:
            return Response(
                {'detail': f"Version {version} not found for {contributor}/{name}"},
                status=status.HTTP_404_NOT_FOUND
            )


class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing contributors.
    Similar to galaxy_ng ContributorViewSet.
    """
    queryset = Contributor.objects.all().order_by('name')
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'name'
    
    def get_queryset(self):
        """Return contributors ordered by name"""
        return Contributor.objects.all().order_by('name')
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete contributor only if no policies depend on it.
        Similar to galaxy_ng contributor deletion checking.
        """
        contributor = self.get_object()
        
        if contributor.policies.exists():
            return Response(
                {
                    'detail': f"Cannot delete contributor '{contributor.name}'. "
                             f"It has {contributor.policies.count()} associated policies."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)


class SearchViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    Search policies by keywords and filters.
    Similar to galaxy_ng SearchListView.
    
    Supports:
    - keywords: text search
    - contributor: filter by contributor
    - tags: filter by tags (comma-separated)
    - is_deprecated: filter deprecated policies
    - order_by: sort results (-relevance, -download_count, -updated_at, name)
    """
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    serializer_class = SearchResultsSerializer
    
    def get_queryset(self):
        """Build search queryset with filters"""
        keywords = self.request.query_params.get('keywords', '')
        contributor = self.request.query_params.get('contributor')
        tags = self.request.query_params.get('tags')
        is_deprecated = self.request.query_params.get('is_deprecated')
        order_by = self.request.query_params.get('order_by', '-updated_at')
        
        # Start with all policies
        queryset = Policy.objects.select_related('contributor').prefetch_related('tags')
        
        # Apply keyword search
        if keywords:
            queryset = queryset.filter(
                Q(name__icontains=keywords) |
                Q(description__icontains=keywords) |
                Q(contributor__name__icontains=keywords) |
                Q(tags__name__icontains=keywords)
            ).distinct()
        
        # Apply contributor filter
        if contributor:
            queryset = queryset.filter(contributor__name=contributor)
        
        # Apply tags filter
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            for tag in tag_list:
                queryset = queryset.filter(tags__name__iexact=tag)
        
        # Apply is_deprecated filter
        if is_deprecated is not None:
            queryset = queryset.filter(is_deprecated=is_deprecated.lower() == 'true')
        
        # Annotate with download count
        download_count = DownloadLog.objects.filter(
            policy_version__policy=OuterRef('pk')
        ).values('policy_version__policy').annotate(
            count=Count('id')
        ).values('count')
        
        queryset = queryset.annotate(
            download_count=Subquery(download_count, output_field=Count('id'))
        )
        
        # Apply ordering
        if order_by == '-relevance':
            # For now, relevance is same as -updated_at
            # TODO: Implement proper full-text search with ranking
            queryset = queryset.order_by('-updated_at')
        elif order_by == '-download_count':
            queryset = queryset.order_by('-download_count', '-updated_at')
        elif order_by == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Return search results with metadata"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        # Format results
        results = []
        for policy in page:
            latest_version = policy.versions.order_by('-created_at').first()
            results.append({
                'id': policy.id,
                'contributor': policy.contributor.name,
                'name': policy.name,
                'description': policy.description,
                'latest_version': latest_version.version if latest_version else None,
                'tags': [tag.name for tag in policy.tags.all()],
                'download_count': policy.download_count or 0,
                'is_deprecated': policy.is_deprecated,
                'created_at': policy.created_at,
                'updated_at': policy.updated_at,
                'content_type': 'policy',
                'relevance': 0.0  # TODO: Implement proper relevance scoring
            })
        
        return self.get_paginated_response(results)


class PolicyUploadViewSet(viewsets.GenericViewSet):
    """
    ViewSet for uploading policy packages.
    Similar to galaxy_ng CollectionUploadViewSet.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PolicyUploadSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Upload a policy package.
        POST /api/v1/policies/upload/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # TODO: Implement actual package parsing and import
        # For now, just return success
        return Response({
            'detail': 'Policy upload initiated',
            'contributor': serializer.validated_data['contributor'],
            'name': serializer.validated_data['name'],
            'version': serializer.validated_data['version'],
        }, status=status.HTTP_202_ACCEPTED)


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for browsing tags.
    Similar to galaxy_ng TagsViewSet.
    """
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Annotate with policy count"""
        return Tag.objects.annotate(
            policy_count=Count('policies')
        ).order_by('name')


class RatingViewSet(viewsets.ModelViewSet):
    """ViewSet for policy ratings"""
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter ratings by policy if specified"""
        queryset = Rating.objects.select_related('user', 'policy').order_by('-created_at')
        policy_id = self.request.query_params.get('policy')
        if policy_id:
            queryset = queryset.filter(policy_id=policy_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set user to current user"""
        serializer.save(user=self.request.user)
