import django_filters
from .models import Event, Venue


class EventFilter(django_filters.FilterSet):
    class Meta:
        model = Event
        fields = ["event_start_date", "category"]

class VenueFilter(django_filters.FilterSet):
    class Meta:
        model = Venue
        fields = ["venue_name", "address", "venue_type"]