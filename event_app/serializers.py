from rest_framework import serializers
from .models import Venue, Category, Event, Offer


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    offers = OfferSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "ext_id",
            "event_name",
            "description",
            "event_url",
            "sale_status",
            "sale_start_date",
            "sale_end_date",
            "event_start_date",
            "category",
            "venue",
            "offers",
        ]
        read_only_fields = ["ext_id", "id", "category", "venue", "offers"]
