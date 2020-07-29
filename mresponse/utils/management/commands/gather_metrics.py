from django.core.management.base import BaseCommand
from django.utils import timezone

from mresponse.reviews.models import Review
from mresponse.reviews.api.views import MAX_REVIEW_RATING
from mresponse.responses.models import Response
from mresponse.moderations.models import Moderation


class Command(BaseCommand):
    def fetched_reviews(self, period=timezone.timedelta(hours=24)):
        reviews = Review.objects.filter(
            application__is_archived=False, last_modified__gte=timezone.now() - period
        )
        return reviews.count()

    def responded_reviews(
        self, language="en", period=timezone.timedelta(hours=72), since=None
    ):
        reviews = Review.objects.filter(
            review_language=language,
            review_rating__lte=MAX_REVIEW_RATING,
            application__is_archived=False,
            last_modified__lte=timezone.now() - period,
        )
        if since:
            reviews = reviews.filter(last_modified__gte=since)

        review_count = 0
        responded_in_period_count = 0

        for review in reviews.iterator():
            review_count += 1
            if (
                hasattr(review, "response")
                and review.response.submitted_to_play_store
                and review.response.submitted_to_play_store_at - review.last_modified
                <= period
            ):
                responded_in_period_count += 1

        if review_count == 0:
            return 0

        return responded_in_period_count / review_count

    def active_contributors(
        self,
        required_responses=5,
        required_moderations=15,
        period=timezone.timedelta(days=7),
    ):
        users = {}
        contributor_count = 0

        since = timezone.now() - period
        responses = Response.objects.filter(submitted_at__gte=since)
        moderations = Moderation.objects.filter(submitted_at__gte=since)

        for response in responses.iterator():
            author = response.author_id
            if author in users:
                users[author]["responses"] += 1
            else:
                users[author] = {"responses": 1, "moderations": 0}

        for moderation in moderations.iterator():
            moderator = moderation.moderator_id
            if moderator in users:
                users[moderator]["moderations"] += 1
            else:
                users[moderator] = {"responses": 0, "moderations": 1}

        for user in users.values():
            if (
                user["responses"] >= required_responses
                and user["moderations"] >= required_moderations
            ):
                contributor_count += 1

        return contributor_count

    def add_arguments(self, parser):
        parser.add_argument(
            "--post-report", help="Post this report", action="store_true"
        )
        parser.add_argument(
            "--fetched-hours",
            help="Hours to report total fetched reviews for",
            type=int,
            default=24,
        )
        parser.add_argument(
            "--responded-hours",
            help="Hours reviews should be responded to within",
            type=int,
            default=72,
        )
        parser.add_argument(
            "--responded-languages",
            help="Languages to report on",
            action="append",
            default=["en", "de", "es"],
        )
        parser.add_argument(
            "--contribute-days",
            help="Days to report active contributors for",
            type=int,
            default=7,
        )
        parser.add_argument(
            "--contribute-responses",
            help="Responses needed to be deemed active",
            type=int,
            default=5,
        )
        parser.add_argument(
            "--contribute-moderations",
            help="Moderations needed to be deemed active",
            type=int,
            default=15,
        )

    def generate_report(self, options):
        report = "Report generated at {}:\n".format(timezone.now())
        report += "Responses fetched in the past {} hours: {}\n".format(
            options["fetched_hours"],
            self.fetched_reviews(
                period=timezone.timedelta(hours=options["fetched_hours"])
            ),
        )
        for language in options["responded_languages"]:
            report += "Responses in {} responded to within {} hours: {:.1%}\n".format(
                language,
                options["responded_hours"],
                self.responded_reviews(
                    language=language,
                    period=timezone.timedelta(hours=options["responded_hours"]),
                ),
            )
        report += "Active contributors (at least {} responses and {} moderations) in the past {} days: {}\n".format(
            options["contribute_responses"],
            options["contribute_moderations"],
            options["contribute_days"],
            self.active_contributors(
                required_responses=options["contribute_responses"],
                required_moderations=options["contribute_moderations"],
                period=timezone.timedelta(days=options["contribute_days"]),
            ),
        )
        return report

    def post_report(self, report):
        raise NotImplementedError

    def handle(self, *args, **kwargs):
        report = self.generate_report(kwargs)
        if kwargs["post_report"]:
            self.post_report(report)
        else:
            print(report)
