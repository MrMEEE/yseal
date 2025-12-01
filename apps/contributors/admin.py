from django.contrib import admin
from .models import Contributor, ContributorLink


class ContributorLinkInline(admin.TabularInline):
    model = ContributorLink
    extra = 1


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'get_owners', 'is_personal', 'policy_count', 'download_count', 'is_verified', 'is_active', 'created_at')
    list_filter = ('is_verified', 'is_active', 'is_personal', 'created_at')
    search_fields = ('name', 'display_name', 'company', 'owners__username', 'owners__email')
    readonly_fields = ('created_at', 'updated_at', 'policy_count', 'download_count')
    filter_horizontal = ('owners',)
    inlines = [ContributorLinkInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'description', 'is_personal')
        }),
        ('Contact Information', {
            'fields': ('company', 'website', 'email', 'avatar_url')
        }),
        ('Ownership', {
            'fields': ('owners',)
        }),
        ('Statistics', {
            'fields': ('policy_count', 'download_count')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('owners')
    
    def get_owners(self, obj):
        """Display the list of owners"""
        return ", ".join([owner.username for owner in obj.owners.all()])
    get_owners.short_description = 'Owners'


@admin.register(ContributorLink)
class ContributorLinkAdmin(admin.ModelAdmin):
    list_display = ('contributor', 'name', 'url', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('contributor__name', 'name', 'url')
