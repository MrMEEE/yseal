"""
Core views for ySEal (Your Security Enhanced Architecture Library).
"""
import django
from django.shortcuts import render
from django.db import connection
from random import sample
from apps.policies.models import Policy, DownloadLog
from apps.contributors.models import Contributor
from apps.accounts.models import User


def home(request):
    """
    Home page view - similar to Ansible Galaxy landing page.
    Shows featured policies, statistics, and recommendations.
    """
    # Get statistics
    policy_count = Policy.objects.filter(is_active=True).count()
    contributor_count = Contributor.objects.filter(is_active=True).count()
    download_count = DownloadLog.objects.count()
    user_count = User.objects.filter(is_active=True).count()
    
    # Get recommendations (random featured contributor if available)
    recommendations = {}
    if contributor_count > 0:
        # Pick a random contributor to feature
        featured_contributor = sample(list(Contributor.objects.filter(is_active=True)), 1)[0]
        recommendations = {
            'recs': [{
                'id': 'yseal-partner',
                'icon': 'bulb',
                'action': {
                    'title': f"Check out {featured_contributor.company or featured_contributor.name}",
                    'href': f"/api/_ui/v1/contributors/{featured_contributor.name}/",
                },
                'description': 'Discover SELinux policies from our contributors.',
            }]
        }
    
    # Get featured policies (6 most recent, non-deprecated)
    featured_policies = Policy.objects.filter(
        is_active=True, 
        is_deprecated=False
    ).order_by('-created_at')[:6]
    
    # Database info
    database_engine = connection.settings_dict['ENGINE'].split('.')[-1].upper()
    if 'sqlite' in database_engine.lower():
        database_engine = 'SQLite'
    elif 'postgresql' in database_engine.lower():
        database_engine = 'PostgreSQL'
    
    context = {
        'policy_count': policy_count,
        'contributor_count': contributor_count,
        'download_count': download_count,
        'user_count': user_count,
        'recommendations': recommendations,
        'featured_policies': featured_policies,
        'django_version': django.get_version(),
        'database_engine': database_engine,
        # For backward compatibility
        'stats': {
            'policies': policy_count,
            'contributors': contributor_count,
            'downloads': download_count,
            'users': user_count,
        }
    }
    
    return render(request, 'home.html', context)


def browse(request):
    """Browse policies page with search and filters."""
    return render(request, 'browse.html')


def contributors(request):
    """Browse contributors page with search and filters."""
    return render(request, 'contributors.html')


def yoel_story(request):
    """The story of Yoel the ySEal."""
    return render(request, 'yoel_story.html')
