from mimesis.schema import Field, Schema

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from mresponse.reviews.models import Review
from mresponse.responses.models import Response
from mresponse.applications.models import Application
from mresponse.users.models import UserProfile
from mresponse.utils.queryset import get_random_entry

class Command(BaseCommand):
    help = "Fill the database with dummy data"

    def add_arguments(self, parser):
        parser.add_argument('--applications', type=int, default=5, help="Number of applications to generate")
        parser.add_argument('--reviews', type=int, default=100, help="Number of reviews to generate")
        parser.add_argument('--users', type=int, default=20, help="Number of users to generate")
        parser.add_argument('--responses', type=int, default=50, help="Number of responses to generate")

    def handle(self, *args, **options):
        _ = Field('en')
        
        def generate_applications():
            description = (
                lambda: {
                    "name": _('os'),
                    "package": _('identifier', mask='@@@.@@@@@.@@@@@')
                }
            )
            schema = Schema(schema=description)
            for fields in schema.create(iterations=options['applications']):
                application = Application(**fields)
                application.save()

        def generate_reviews():
            description = (
                lambda: {
                    "play_store_review_id": _('uuid'),
                    "android_sdk_version": _('integer_number', start=1),
                    "author_name": _('full_name'),
                    "review_text": _('text'),
                    "review_language": 'en',
                    "review_rating": _('integer_number', start=1, end=2),
                    "last_modified": _('datetime')
                }
            )
            schema = Schema(schema=description)
            for fields in schema.create(iterations=options['reviews']):
                review = Review(**fields)
                review.application = get_random_entry(Application.objects.all())
                review.save()

        def generate_users():
            description = (
                lambda: {
                    "username": _('username'),
                    "languages": '["en"]',
                    "name": _('full_name')
                }
            )
            schema = Schema(schema=description)
            for fields in schema.create(iterations=options['users']):
                user = get_user_model()(username=fields['username'])
                user.save()
                user.profile.languages = fields['languages']
                user.profile.name = fields['name']
                user.profile.save()

        def generate_responses():
            description = (
                lambda: {
                   "text": _('text')
                }
            )
            schema = Schema(schema=description)
            for fields in schema.create(iterations=options['responses']):
                response = Response(**fields)
                response.review = get_random_entry(Review.objects.filter(response__isnull=True))
                response.author = get_random_entry(get_user_model().objects.all())
                response.save()

        generate_applications()
        generate_reviews()
        generate_users()
        generate_responses()
