from django.db import models


class Venue(models.Model):
    venue_name = models.CharField(max_length=255)
    venue_type = models.CharField(max_length=255)
    seat_map = models.URLField(max_length=1000, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)

    def __str__(self):
        return f"{self.venue_name} - {self.city}"


class Category(models.Model):
    segment = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    subgenre = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.segment or self.genre or self.subgenre or "Uncategorized"


class Offer(models.Model):
    event = models.ForeignKey(
        "Event", related_name="offers", on_delete=models.CASCADE, null=True
    )
    offer_type = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    sale_url = models.URLField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event}-{self.offer_type} : {self.price}"


class Event(models.Model):
    ext_id = models.CharField(max_length=255)
    event_name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    event_url = models.URLField(max_length=1000, null=True, blank=True)
    sale_status = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    sale_start_date = models.DateTimeField(blank=True, null=True)
    sale_end_date = models.DateTimeField(blank=True, null=True)
    event_start_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_name} - {self.event_start_date}"
