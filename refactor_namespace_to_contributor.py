#!/usr/bin/env python3
"""
Script to rename namespace to contributor throughout the codebase.
This handles all Python files that reference namespace/Namespace.
"""
import os
import re
from pathlib import Path

# Define the base directory
BASE_DIR = Path(__file__).parent

# Files to update (relative to BASE_DIR)
FILES_TO_UPDATE = [
    'apps/policies/viewsets.py',
    'apps/policies/admin.py',
    'apps/api/v1/urls.py',
    'apps/core/views.py',
    'apps/accounts/models.py',
    'apps/accounts/admin.py',
]

# Replacement patterns
REPLACEMENTS = [
    # Class names
    (r'\bNamespaceViewSet\b', 'ContributorViewSet'),
    (r'\bNamespaceSerializer\b', 'ContributorSerializer'),
    (r'\bNamespaceLinkInline\b', 'ContributorLinkInline'),
    (r'\bNamespaceAdmin\b', 'ContributorAdmin'),
    (r'\bNamespaceLink\b', 'ContributorLink'),
    (r'\bNamespace\b', 'Contributor'),
    
    # Import statements
    (r'from apps\.namespaces\.models import', 'from apps.contributors.models import'),
    (r'apps\.namespaces', 'apps.contributors'),
    
    # URL patterns
    (r"r'namespaces'", "r'contributors'"),
    (r'basename=[\'"]namespace[\'"]', 'basename="contributor"'),
    
    # Variable names and field names
    (r'\bnamespace__name\b', 'contributor__name'),
    (r'\bnamespace__(\w+)', r'contributor__\1'),
    (r'\.namespace\.', '.contributor.'),
    (r'\bnamespace\b(?!s)', 'contributor'),  # namespace but not namespaces
    (r'\bnamespace_count\b', 'contributor_count'),
    (r'\bfeatured_namespace\b', 'featured_contributor'),
    (r'\bowned_namespaces\b', 'owned_contributors'),
    (r'\bcan_create_namespace\b', 'can_create_contributor'),
    
    # String literals
    (r'"namespace"', '"contributor"'),
    (r"'namespace'", "'contributor'"),
    (r'"namespaces"', '"contributors"'),
    (r"'namespaces'", "'contributors'"),
    
    # Comments and docstrings
    (r'namespace', 'contributor'),
    (r'Namespace', 'Contributor'),
]

def update_file(filepath):
    """Update a single file with all replacements."""
    full_path = BASE_DIR / filepath
    
    if not full_path.exists():
        print(f"Skipping {filepath} (not found)")
        return
    
    print(f"Updating {filepath}...")
    
    with open(full_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Apply all replacements
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"  ✓ Updated {filepath}")
    else:
        print(f"  - No changes needed for {filepath}")

def main():
    print("Starting namespace → contributor refactoring...")
    print("=" * 60)
    
    for filepath in FILES_TO_UPDATE:
        update_file(filepath)
    
    print("=" * 60)
    print("Refactoring complete!")
    print("\nNext steps:")
    print("1. Run: python manage.py makemigrations")
    print("2. Run: python manage.py migrate")
    print("3. Test the application")

if __name__ == '__main__':
    main()
