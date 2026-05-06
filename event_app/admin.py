from django.contrib import admin
from .models import Event, Venue, Category, Offer


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "event_url", "category", "venue")
    list_filter = ["category", "event_start_date"]


@admin.register(Venue)
class VenueEvent(admin.ModelAdmin):
    list_display = ("venue_name", "venue_type", "address", "city")
    list_filter = ["venue_type"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("segment", "genre", "subgenre")


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("offer_type", "price", "currency")
