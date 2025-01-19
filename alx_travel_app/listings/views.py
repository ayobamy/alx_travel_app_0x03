from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Listings.
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @swagger_auto_schema(
        method='get',
        operation_description="Filter listings by city",
        manual_parameters=[
            openapi.Parameter(
                'city',
                openapi.IN_QUERY,
                description="City name to filter by",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_city(self, request):
        """
        Filter listings by city.
        """
        city = request.query_params.get('city', '')
        listings = self.queryset.filter(city__icontains=city)
        serializer = self.serializer_class(listings, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='get',
        operation_description="Get listings by availability status",
        manual_parameters=[
            openapi.Parameter(
                'available',
                openapi.IN_QUERY,
                description="Availability status (true/false)",
                type=openapi.TYPE_BOOLEAN
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get listings filtered by availability."""
        is_available = request.query_params.get('available', 'true').lower() == 'true'
        listings = self.queryset.filter(is_available=is_available)
        serializer = self.serializer_class(listings, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Bookings.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        listing = get_object_or_404(Listing, listing_id=self.request.data.get('listing'))
        # Cal total price based on number of nights
        check_in = serializer.validated_data['check_in_date']
        check_out = serializer.validated_data['check_out_date']
        nights = (check_out - check_in).days
        total_price = listing.price_per_night * nights
        
        serializer.save(
            guest=self.request.user,
            total_price=total_price
        )

    def get_queryset(self):
        """
        Filter bookings based on user role.
        """
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(guest=user)

    @swagger_auto_schema(
        method='post',
        operation_description="Cancel a booking",
        responses={200: "Booking cancelled successfully"}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a booking.
        """
        booking = self.get_object()
        if booking.guest != request.user and not request.user.is_staff:
            return Response(
                {"error": "You don't have permission to cancel this booking"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        booking.status = 'cancelled'
        booking.save()
        return Response({"message": "Booking cancelled successfully"})

    @swagger_auto_schema(
        method='get',
        operation_description="Get bookings by status",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Booking status (pending/confirmed/cancelled/completed)",
                type=openapi.TYPE_STRING
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """
        Get bookings filtered by status.
        """
        status = request.query_params.get('status', '')
        bookings = self.get_queryset().filter(status=status)
        serializer = self.serializer_class(bookings, many=True)
        return Response(serializer.data)
