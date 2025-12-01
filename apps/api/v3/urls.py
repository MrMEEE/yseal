"""
API v3 URLs - Main API for CLI tool (similar to Ansible Galaxy api/v3/).
These endpoints will be consumed by the yseal-cli tool.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.policies.viewsets import (
    PolicyViewSet,
    ContributorViewSet,
    SearchViewSet,
    TagsViewSet,
)

app_name = 'api-v3'

router = DefaultRouter()

# Register viewsets
router.register(r'contributors', ContributorViewSet, basename='contributor')
router.register(r'policies', PolicyViewSet, basename='policy')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'tags', TagsViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]
