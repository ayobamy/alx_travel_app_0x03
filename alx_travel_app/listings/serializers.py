from rest_framework import serializers
from .models import Listing, Booking

class ListingSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.username', read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'description', 'address',
            'city', 'country', 'price_per_night', 'bedrooms',
            'max_guests', 'host_name', 'is_available', 'average_rating',
            'created_at', 'updated_at'
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / len(reviews)

class BookingSerializer(serializers.ModelSerializer):
    guest_name = serializers.CharField(source='guest.username', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'listing_title', 'guest_name',
            'check_in_date', 'check_out_date', 'number_of_guests',
            'total_price', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_price']

    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError(
                "Check-out date must be after check-in date"
            )
        if data['number_of_guests'] > data['listing'].max_guests:
            raise serializers.ValidationError(
                "Number of guests exceeds listing capacity"
            )
        return data
