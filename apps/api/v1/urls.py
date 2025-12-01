"""
API v1 URLs - UI specific endpoints (similar to Ansible Galaxy _ui/v1/).
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.policies.viewsets import (
    PolicyViewSet,
    ContributorViewSet,
    SearchViewSet,
    PolicyUploadViewSet,
    TagsViewSet,
    RatingViewSet,
)

app_name = 'api-ui-v1'

router = DefaultRouter()

# Register viewsets
router.register(r'contributors', ContributorViewSet, basename='contributor')
router.register(r'policies', PolicyViewSet, basename='policy')
router.register(r'search', SearchViewSet, basename='search')
router.register(r'tags', TagsViewSet, basename='tag')
router.register(r'ratings', RatingViewSet, basename='rating')

# Upload endpoint
upload_patterns = [
    path('', PolicyUploadViewSet.as_view({'post': 'create'}), name='policy-upload'),
]

urlpatterns = [
    path('', include(router.urls)),
    path('upload/', include(upload_patterns)),
]
