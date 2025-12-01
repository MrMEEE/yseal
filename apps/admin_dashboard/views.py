"""
Admin dashboard views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from apps.policies.models import Policy, PolicyVersion, Tag
from apps.contributors.models import Contributor
from apps.accounts.models import User
from apps.voting.models import Rating


def is_staff(user):
    """Check if user is staff."""
    return user.is_staff


def login_view(request):
    """
    Custom login view with site theme.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            auth_login(request, user)
            next_url = request.GET.get('next', 'admin_dashboard:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Please enter the correct username and password for a staff account.')
    
    return render(request, 'admin_dashboard/login.html')


def logout_view(request):
    """
    Logout view that redirects to home page.
    """
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('/')


@login_required
@user_passes_test(is_staff)
def dashboard(request):
    """
    Admin dashboard home page with statistics.
    """
    context = {
        'total_policies': Policy.objects.count(),
        'total_contributors': Contributor.objects.count(),
        'total_users': User.objects.count(),
        'total_tags': Tag.objects.count(),
        'total_ratings': Rating.objects.count(),
        'recent_policies': Policy.objects.select_related('contributor').order_by('-created_at')[:10],
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'pending_policies': Policy.objects.filter(is_deprecated=False).count(),
    }
    return render(request, 'admin_dashboard/dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def policies_list(request):
    """
    List all policies with search and filters.
    """
    policies = Policy.objects.select_related('contributor').annotate(
        version_count=Count('versions')
    ).order_by('-created_at')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        policies = policies.filter(
            Q(name__icontains=search_query) |
            Q(contributor__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by contributor
    contributor_filter = request.GET.get('contributor', '')
    if contributor_filter:
        policies = policies.filter(contributor__name=contributor_filter)
    
    # Filter by deprecated
    deprecated_filter = request.GET.get('deprecated', '')
    if deprecated_filter == 'true':
        policies = policies.filter(is_deprecated=True)
    elif deprecated_filter == 'false':
        policies = policies.filter(is_deprecated=False)
    
    # Pagination
    paginator = Paginator(policies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'contributor_filter': contributor_filter,
        'deprecated_filter': deprecated_filter,
        'contributors': Contributor.objects.all().order_by('name'),
    }
    return render(request, 'admin_dashboard/policies_list.html', context)


@login_required
@user_passes_test(is_staff)
def contributors_list(request):
    """
    List all contributors with search and filters.
    """
    contributors = Contributor.objects.annotate(
        owner_count=Count('owners')
    ).order_by('name')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        contributors = contributors.filter(
            Q(name__icontains=search_query) |
            Q(display_name__icontains=search_query) |
            Q(company__icontains=search_query)
        )
    
    # Filter by verified
    verified_filter = request.GET.get('verified', '')
    if verified_filter == 'true':
        contributors = contributors.filter(is_verified=True)
    elif verified_filter == 'false':
        contributors = contributors.filter(is_verified=False)
    
    # Pagination
    paginator = Paginator(contributors, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'verified_filter': verified_filter,
    }
    return render(request, 'admin_dashboard/contributors_list.html', context)


@login_required
@user_passes_test(is_staff)
def users_list(request):
    """
    List all users with search and filters.
    """
    users = User.objects.annotate(
        contributor_count=Count('owned_contributors')
    ).order_by('-date_joined')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Filter by staff
    staff_filter = request.GET.get('staff', '')
    if staff_filter == 'true':
        users = users.filter(is_staff=True)
    elif staff_filter == 'false':
        users = users.filter(is_staff=False)
    
    # Filter by verified
    verified_filter = request.GET.get('verified', '')
    if verified_filter == 'true':
        users = users.filter(is_verified=True)
    elif verified_filter == 'false':
        users = users.filter(is_verified=False)
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'staff_filter': staff_filter,
        'verified_filter': verified_filter,
    }
    return render(request, 'admin_dashboard/users_list.html', context)


@login_required
@user_passes_test(is_staff)
def tags_list(request):
    """
    List all tags.
    """
    tags = Tag.objects.annotate(
        policy_count=Count('policies')
    ).order_by('-policy_count')
    
    context = {
        'tags': tags,
    }
    return render(request, 'admin_dashboard/tags_list.html', context)


@login_required
@user_passes_test(is_staff)
def ratings_list(request):
    """
    List all ratings.
    """
    ratings = Rating.objects.select_related('user', 'policy').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(ratings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'admin_dashboard/ratings_list.html', context)
