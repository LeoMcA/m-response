from django.db import models
from django.utils import timezone

ASSIGNMENT_TIMEOUT = timezone.timedelta(minutes=20)


class ResponseQuerySet(models.QuerySet):
    def annotate_moderations_count(self):
        return self.annotate(moderations_count=models.Count('moderations'))

    def annotate_pass_criteria(self):
        return self.annotate(
            total_moderations_count=models.Count('moderations')
        ).annotate(
            positive_in_tone_count=models.Count('moderations', filter=models.Q(
                moderations__positive_in_tone=True))
        ).annotate(
            addressing_the_issue_count=models.Count('moderations', filter=models.Q(
                moderations__addressing_the_issue=True))
        ).annotate(
            personal_count=models.Count('moderations', filter=models.Q(
                moderations__personal=True))
        ).distinct()

    def pass_criteria(self):
        return self.annotate_pass_criteria().filter(
            total_moderations_count__gte=3,
            positive_in_tone_count__gte=3,
            addressing_the_issue_count__gte=2,
            personal_count__gte=1
        )

    def not_approved(self):
        return self.filter(approved=False)

    def moderator_queue(self):
        return self.not_approved().exclude(
            author__user_permissions__codename='can_bypass_community_moderation'
        )

    def no_moderations(self):
        return self.annotate_moderations_count().filter(moderations_count=0)

    def one_moderation(self):
        return self.annotate_moderations_count().filter(moderations_count=1)

    def two_or_more_moderations(self):
        return self.annotate_moderations_count().filter(moderations_count__gte=2)

    def two_or_less_moderations(self):
        return self.annotate_moderations_count().filter(moderations_count__lte=2)

    def not_moderated_by(self, user):
        return self.exclude(moderations__moderator_id=user.pk)

    def not_authored_by(self, user):
        return self.exclude(author=user.pk)


class ResponseAssignedToUserQuerySet(models.QuerySet):
    def expired(self):
        return self.filter(
            assigned_at__lt=timezone.now() - ASSIGNMENT_TIMEOUT
        )

    def not_expired(self):
        return self.filter(
            assigned_at__gte=timezone.now() - ASSIGNMENT_TIMEOUT
        )
