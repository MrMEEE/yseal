from django.contrib import admin
from .models import Tag, Policy, PolicyVersion, PolicyFile, DownloadLog


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


class PolicyVersionInline(admin.TabularInline):
    model = PolicyVersion
    extra = 0
    readonly_fields = ('created_at', 'download_count')
    fields = ('version', 'git_commit', 'is_latest', 'download_count', 'created_at')


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'contributor', 'download_count', 'star_count', 'is_deprecated', 'is_active', 'created_at')
    list_filter = ('is_deprecated', 'is_active', 'contributor', 'created_at')
    search_fields = ('name', 'contributor__name', 'description')
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at', 'download_count', 'star_count')
    inlines = [PolicyVersionInline]
    
    fieldsets = (
        (None, {
            'fields': ('contributor', 'name', 'display_name', 'description')
        }),
        ('Repository', {
            'fields': ('repository_url', 'repository_branch')
        }),
        ('Documentation', {
            'fields': ('readme', 'documentation_url')
        }),
        ('Metadata', {
            'fields': ('tags', 'license')
        }),
        ('Statistics', {
            'fields': ('download_count', 'star_count')
        }),
        ('Status', {
            'fields': ('is_deprecated', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class PolicyFileInline(admin.TabularInline):
    model = PolicyFile
    extra = 0
    readonly_fields = ('size',)


@admin.register(PolicyVersion)
class PolicyVersionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'version', 'is_latest', 'download_count', 'created_at')
    list_filter = ('is_latest', 'created_at', 'policy__contributor')
    search_fields = ('policy__name', 'policy__contributor__name', 'version')
    readonly_fields = ('created_at', 'updated_at', 'download_count')
    inlines = [PolicyFileInline]
    
    fieldsets = (
        (None, {
            'fields': ('policy', 'version', 'changelog')
        }),
        ('Git Information', {
            'fields': ('git_commit', 'git_tag')
        }),
        ('Archive', {
            'fields': ('archive_url', 'archive_size', 'checksum')
        }),
        ('Dependencies', {
            'fields': ('dependencies',)
        }),
        ('SELinux Specific', {
            'fields': ('selinux_version', 'supported_systems')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Status', {
            'fields': ('is_latest', 'download_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PolicyFile)
class PolicyFileAdmin(admin.ModelAdmin):
    list_display = ('version', 'file_path', 'file_type', 'size', 'created_at')
    list_filter = ('file_type', 'created_at')
    search_fields = ('version__policy__name', 'file_path')


@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ('policy', 'version', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('policy__name', 'ip_address')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
