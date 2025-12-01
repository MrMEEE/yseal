from django.contrib import admin
from .models import Vote, Rating, RatingHelpfulness


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'policy', 'value', 'created_at')
    list_filter = ('value', 'created_at')
    search_fields = ('user__username', 'policy__name', 'policy__contributor__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'policy', 'value', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'policy', 'score', 'helpful_count', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'policy__name', 'policy__contributor__name', 'review')
    readonly_fields = ('created_at', 'updated_at', 'helpful_count')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'policy', 'score', 'review')
        }),
        ('Engagement', {
            'fields': ('helpful_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RatingHelpfulness)
class RatingHelpfulnessAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('user__username', 'rating__policy__name')
    readonly_fields = ('created_at',)
