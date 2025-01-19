from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing
from django.utils.crypto import get_random_string
import random

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listings',
            type=int,
            default=10,
            help='Number of listings to create'
        )

    def handle(self, *args, **options):
        host_user, created = User.objects.get_or_create(
            username='ahmed_olawale',
            email='ayobamyahmed@gmail.com'
        )
        if created:
            host_user.set_password('password123#')
            host_user.save()
            self.stdout.write(
                self.style.SUCCESS('Created sample host user')
            )

        cities = ['New York', 'Oyo State', 'Paris', 'Cairo', 'Sydney']
        countries = ['USA', 'Nigeria', 'France', 'Egypt', 'Australia']
        listings_to_create = options['listings']
        created_count = 0

        for _ in range(listings_to_create):
            city_idx = random.randint(0, len(cities) - 1)
            listing = Listing.objects.create(
                title=f"Beautiful Properties in {cities[city_idx]}",
                description=f"A wonderful place to stay in {cities[city_idx]}. {get_random_string(100)}",
                address=f"{random.randint(1, 999)} {get_random_string(10)} Street",
                city=cities[city_idx],
                country=countries[city_idx],
                price_per_night=random.randint(50, 500),
                bedrooms=random.randint(1, 5),
                bathrooms=random.randint(1, 3),
                max_guests=random.randint(2, 10),
                host=host_user,
                is_available=True
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} listings')
        )
