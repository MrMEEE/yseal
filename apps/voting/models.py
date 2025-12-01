"""
Voting and rating models for policies.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from apps.core.models import TimeStampedModel
from apps.policies.models import Policy

User = get_user_model()


class Vote(TimeStampedModel):
    """
    User votes on policies (upvote/downvote).
    """
    VOTE_CHOICES = [
        (1, 'Upvote'),
        (-1, 'Downvote'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    value = models.SmallIntegerField(
        _('vote value'),
        choices=VOTE_CHOICES,
        help_text=_('1 for upvote, -1 for downvote')
    )
    comment = models.TextField(_('comment'), blank=True)
    
    class Meta:
        db_table = 'votes'
        verbose_name = _('vote')
        verbose_name_plural = _('votes')
        unique_together = [['user', 'policy']]
        indexes = [
            models.Index(fields=['policy', 'value']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        vote_type = "upvoted" if self.value > 0 else "downvoted"
        return f"{self.user.username} {vote_type} {self.policy.full_name}"


class Rating(TimeStampedModel):
    """
    User ratings for policies (1-5 stars).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    policy = models.ForeignKey(
        Policy,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    score = models.SmallIntegerField(
        _('rating score'),
        choices=[(i, f"{i} stars") for i in range(1, 6)],
        help_text=_('Rating from 1 to 5 stars')
    )
    review = models.TextField(_('review'), blank=True)
    
    # Helpfulness tracking
    helpful_count = models.IntegerField(_('helpful count'), default=0)
    
    class Meta:
        db_table = 'ratings'
        verbose_name = _('rating')
        verbose_name_plural = _('ratings')
        unique_together = [['user', 'policy']]
        indexes = [
            models.Index(fields=['policy', 'score']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.policy.full_name} - {self.score} stars"


class RatingHelpfulness(TimeStampedModel):
    """
    Track which users found a rating helpful.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rating_helpfulness'
    )
    rating = models.ForeignKey(
        Rating,
        on_delete=models.CASCADE,
        related_name='helpfulness'
    )
    is_helpful = models.BooleanField(_('is helpful'), default=True)
    
    class Meta:
        db_table = 'rating_helpfulness'
        verbose_name = _('rating helpfulness')
        verbose_name_plural = _('rating helpfulness')
        unique_together = [['user', 'rating']]

    def __str__(self):
        return f"{self.user.username} found rating {self.rating.id} {'helpful' if self.is_helpful else 'not helpful'}"
