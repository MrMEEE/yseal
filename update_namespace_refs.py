#!/usr/bin/env python3
"""
Quick script to update namespace references to contributor.
"""
import os

# Read and update viewsets.py
with open('apps/policies/viewsets.py', 'r') as f:
    content = f.read()

content = content.replace('from apps.namespaces.models import Namespace', 'from apps.contributors.models import Contributor')
content = content.replace('NamespaceSerializer', 'ContributorSerializer')
content = content.replace('NamespaceViewSet', 'ContributorViewSet')
content = content.replace('namespace__name', 'contributor__name')
content = content.replace('.namespace.', '.contributor.')
content = content.replace("'namespace'", "'contributor'")
content = content.replace('"namespace"', '"contributor"')
content = content.replace('namespace_count', 'contributor_count')
content = content.replace('Namespace.objects', 'Contributor.objects')
content = content.replace('queryset = Namespace', 'queryset = Contributor')
content = content.replace("serializer_class = NamespaceSerializer", "serializer_class = ContributorSerializer")
content = content.replace("basename='namespace'", "basename='contributor'")

with open('apps/policies/viewsets.py', 'w') as f:
    f.write(content)

print("✓ Updated apps/policies/viewsets.py")

# Update admin.py
with open('apps/policies/admin.py', 'r') as f:
    content = f.read()

content = content.replace('namespace__name', 'contributor__name')
content = content.replace('.namespace.', '.contributor.')
content = content.replace("'namespace'", "'contributor'")
content = content.replace('"namespace"', '"contributor"')

with open('apps/policies/admin.py', 'w') as f:
    f.write(content)

print("✓ Updated apps/policies/admin.py")

# Update core views
with open('apps/core/views.py', 'r') as f:
    content = f.read()

content = content.replace('from apps.namespaces.models import Namespace', 'from apps.contributors.models import Contributor')
content = content.replace('Namespace.objects', 'Contributor.objects')
content = content.replace('namespace_count', 'contributor_count')
content = content.replace('featured_namespace', 'featured_contributor')

with open('apps/core/views.py', 'w') as f:
    f.write(content)

print("✓ Updated apps/core/views.py")

# Update URL patterns
with open('apps/api/v1/urls.py', 'r') as f:
    content = f.read()

content = content.replace('NamespaceViewSet', 'ContributorViewSet')
content = content.replace("r'namespaces'", "r'contributors'")
content = content.replace("basename='namespace'", "basename='contributor'")

with open('apps/api/v1/urls.py', 'w') as f:
    f.write(content)

print("✓ Updated apps/api/v1/urls.py")

# Update accounts models
with open('apps/accounts/models.py', 'r') as f:
    content = f.read()

content = content.replace('can_create_namespace', 'can_create_contributor')

with open('apps/accounts/models.py', 'w') as f:
    f.write(content)

print("✓ Updated apps/accounts/models.py")

# Update accounts admin
with open('apps/accounts/admin.py', 'r') as f:
    content = f.read()

content = content.replace('can_create_namespace', 'can_create_contributor')

with open('apps/accounts/admin.py', 'w') as f:
    f.write(content)

print("✓ Updated apps/accounts/admin.py")

# Update voting admin
with open('apps/voting/admin.py', 'r') as f:
    content = f.read()

content = content.replace('namespace__name', 'contributor__name')

with open('apps/voting/admin.py', 'w') as f:
    f.write(content)

print("✓ Updated apps/voting/admin.py")

print("\n✅ All files updated successfully!")
