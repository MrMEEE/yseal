"""
Management command to populate sample contributors and policies.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.contributors.models import Contributor
from apps.policies.models import Policy, PolicyVersion, Tag

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate database with sample contributors and policies'

    def handle(self, *args, **options):
        self.stdout.write('Populating sample data...')
        
        # Create sample users if they don't exist
        users = []
        for i, username in enumerate(['admin', 'selinux-team', 'redhat', 'fedora', 'community']):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            users.append(user)
        
        # Create sample contributors
        contributors_data = [
            {
                'name': 'selinux',
                'display_name': 'SELinux Project',
                'description': 'Official SELinux policy modules and tools',
                'company': 'SELinux Community',
                'website': 'https://selinuxproject.org',
                'is_verified': True,
            },
            {
                'name': 'redhat',
                'display_name': 'Red Hat',
                'description': 'Enterprise Linux security policies from Red Hat',
                'company': 'Red Hat, Inc.',
                'website': 'https://redhat.com',
                'is_verified': True,
            },
            {
                'name': 'fedora',
                'display_name': 'Fedora Project',
                'description': 'Community-driven SELinux policies for Fedora',
                'company': 'Fedora Project',
                'website': 'https://getfedora.org',
                'is_verified': True,
            },
            {
                'name': 'community',
                'display_name': 'Community Contributors',
                'description': 'Community-maintained SELinux policies',
                'company': '',
                'website': '',
                'is_verified': False,
            },
        ]
        
        contributors = []
        for contrib_data in contributors_data:
            contributor, created = Contributor.objects.get_or_create(
                name=contrib_data['name'],
                defaults=contrib_data
            )
            if created:
                # Add owner
                user = users[len(contributors) % len(users)]
                contributor.owners.add(user)
                self.stdout.write(self.style.SUCCESS(f'Created contributor: {contributor.name}'))
            contributors.append(contributor)
        
        # Create sample tags
        tag_names = ['docker', 'nginx', 'apache', 'database', 'web-server', 'container', 'security', 'networking']
        tags = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tag: {tag_name}'))
            tags.append(tag)
        
        # Create sample policies
        policies_data = [
            {
                'contributor': contributors[0],
                'name': 'docker-selinux',
                'description': 'SELinux policy module for Docker containers. Provides proper security context for container operations.',
                'tags': [tags[0], tags[5], tags[6]],
            },
            {
                'contributor': contributors[0],
                'name': 'nginx-selinux',
                'description': 'SELinux policy for Nginx web server. Allows Nginx to run with proper security contexts.',
                'tags': [tags[1], tags[4], tags[7]],
            },
            {
                'contributor': contributors[1],
                'name': 'httpd-custom',
                'description': 'Enhanced Apache HTTP Server SELinux policy with additional permissions for enterprise deployments.',
                'tags': [tags[2], tags[4]],
            },
            {
                'contributor': contributors[2],
                'name': 'postgresql-selinux',
                'description': 'SELinux policy for PostgreSQL database server with enhanced security features.',
                'tags': [tags[3], tags[6]],
            },
            {
                'contributor': contributors[3],
                'name': 'nodejs-selinux',
                'description': 'Community SELinux policy for Node.js applications.',
                'tags': [tags[4], tags[7]],
            },
        ]
        
        for policy_data in policies_data:
            policy_tags = policy_data.pop('tags')
            policy, created = Policy.objects.get_or_create(
                contributor=policy_data['contributor'],
                name=policy_data['name'],
                defaults=policy_data
            )
            
            if created:
                policy.tags.set(policy_tags)
                
                # Create initial version
                version = PolicyVersion.objects.create(
                    policy=policy,
                    version='1.0.0',
                    git_commit='a' * 40,  # Dummy commit hash
                    changelog='Initial release\n- Initial policy implementation\n- Basic security contexts\n- File permissions'
                )
                
                self.stdout.write(self.style.SUCCESS(f'Created policy: {policy.full_name} v{version.version}'))
                
                # Update policy count
                policy.contributor.policy_count = policy.contributor.policies.count()
                policy.contributor.save()
        
        self.stdout.write(self.style.SUCCESS('Sample data population complete!'))
        self.stdout.write(f'Created {Contributor.objects.count()} contributors')
        self.stdout.write(f'Created {Policy.objects.count()} policies')
        self.stdout.write(f'Created {Tag.objects.count()} tags')
