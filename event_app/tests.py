from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal

from .models import Event, Venue, Category

# Disable throttling for all tests by using a cache backend that never stores.
NO_THROTTLE_CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

User = get_user_model()


# ─── Helpers ──────────────────────────────────────────────────────────────────


def make_venue(**kwargs):
    defaults = dict(
        venue_name="Scotiabank Arena",
        venue_type="venue",
        seat_map="",
        address="40 Bay St",
        city="Toronto",
        country="Canada",
        latitude=Decimal("43.643500"),
        longitude=Decimal("-79.379100"),
    )
    defaults.update(kwargs)
    return Venue.objects.create(**defaults)


def make_category(**kwargs):
    defaults = dict(segment="Music", genre="Rock", subgenre="Indie")
    defaults.update(kwargs)
    return Category.objects.create(**defaults)


def make_event(venue=None, category=None, **kwargs):
    venue = venue or make_venue()
    category = category or make_category()
    defaults = dict(
        ext_id="TK-TEST-001",
        event_name="Test Concert",
        description="A test event",
        event_url="https://example.com/event",
        sale_status="ON_SALE",
        venue=venue,
        category=category,
    )
    defaults.update(kwargs)
    return Event.objects.create(**defaults)


# ─── Health endpoints ──────────────────────────────────────────────────────────


@override_settings(CACHES=NO_THROTTLE_CACHE)
class HealthzTests(TestCase):
    """GET /api/v1/healthz/ — liveness probe, no auth required."""

    def setUp(self):
        self.client = APIClient()

    def test_healthz_returns_200(self):
        r = self.client.get("/api/v1/healthz/")
        self.assertEqual(r.status_code, 200)

    def test_healthz_body(self):
        r = self.client.get("/api/v1/healthz/")
        data = r.json()
        self.assertEqual(data["status"], "alive")
        self.assertIn("time", data)

    def test_healthz_no_auth_required(self):
        """Unauthenticated request must still return 200."""
        r = self.client.get("/api/v1/healthz/")
        self.assertNotEqual(r.status_code, 401)
        self.assertNotEqual(r.status_code, 403)


@override_settings(CACHES=NO_THROTTLE_CACHE)
class ReadyzTests(TestCase):
    """GET /api/v1/readyz/ — readiness probe, no auth required."""

    def setUp(self):
        self.client = APIClient()

    def test_readyz_returns_200_or_503(self):
        r = self.client.get("/api/v1/readyz/")
        self.assertIn(r.status_code, [200, 503])

    def test_readyz_body_has_checks(self):
        r = self.client.get("/api/v1/readyz/")
        data = r.json()
        self.assertIn("status", data)
        self.assertIn("checks", data)

    def test_readyz_database_check_present(self):
        r = self.client.get("/api/v1/readyz/")
        self.assertIn("database", r.json()["checks"])

    def test_readyz_cache_check_present(self):
        r = self.client.get("/api/v1/readyz/")
        self.assertIn("cache", r.json()["checks"])


# ─── Auth endpoints ────────────────────────────────────────────────────────────


@override_settings(CACHES=NO_THROTTLE_CACHE)
class TokenTests(TestCase):
    """POST /api/v1/token/ — JWT obtain/refresh/verify."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_obtain_token_valid_credentials(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.json())
        self.assertIn("refresh", r.json())

    def test_obtain_token_wrong_password(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "testuser", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(r.status_code, 401)

    def test_refresh_token(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        refresh = r.json()["refresh"]
        r2 = self.client.post(
            "/api/v1/token/refresh/", {"refresh": refresh}, format="json"
        )
        self.assertEqual(r2.status_code, 200)
        self.assertIn("access", r2.json())

    def test_verify_token_valid(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        access = r.json()["access"]
        r2 = self.client.post("/api/v1/token/verify/", {"token": access}, format="json")
        self.assertEqual(r2.status_code, 200)

    def test_verify_token_invalid(self):
        r = self.client.post(
            "/api/v1/token/verify/", {"token": "not.a.real.token"}, format="json"
        )
        self.assertEqual(r.status_code, 401)


# ─── Event list ────────────────────────────────────────────────────────────────


@override_settings(CACHES=NO_THROTTLE_CACHE)
class EventListTests(TestCase):
    """GET /api/v1/event/events_list/ — list all events."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="listuser", password="pass")
        self.event = make_event()

    def _auth(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "listuser", "password": "pass"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.json()['access']}")

    def test_list_unauthenticated_returns_200(self):
        """IsAuthenticatedOrReadOnly allows unauthenticated GET."""
        r = self.client.get("/api/v1/event/events_list/")
        self.assertEqual(r.status_code, 200)

    def test_list_authenticated_returns_200(self):
        self._auth()
        r = self.client.get("/api/v1/event/events_list/")
        self.assertEqual(r.status_code, 200)

    def test_list_returns_event_fields(self):
        self._auth()
        r = self.client.get("/api/v1/event/events_list/")
        results = r.json()
        self.assertGreater(len(results), 0)
        event = results[0]
        self.assertIn("event_name", event)
        self.assertIn("venue", event)
        self.assertIn("category", event)
        self.assertIn("offers", event)

    def test_list_filter_by_sale_status(self):
        self._auth()
        r = self.client.get("/api/v1/event/events_list/?sale_status=ON_SALE")
        self.assertEqual(r.status_code, 200)

    def test_list_pagination_limit(self):
        self._auth()
        # Create extra events
        for i in range(5):
            make_event(ext_id=f"TK-EXTRA-{i}", event_name=f"Extra Event {i}")
        r = self.client.get("/api/v1/event/events_list/?limit=2&offset=0")
        self.assertEqual(r.status_code, 200)
        self.assertLessEqual(len(r.json()), 2)


# ─── Event detail ──────────────────────────────────────────────────────────────


@override_settings(CACHES=NO_THROTTLE_CACHE)
class EventDetailTests(TestCase):
    """GET /api/v1/event/{pk}/events_detail/ — single event."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="detailuser", password="pass")
        self.event = make_event()

    def _auth(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "detailuser", "password": "pass"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.json()['access']}")

    def test_detail_unauthenticated_returns_200(self):
        """IsAuthenticatedOrReadOnly allows unauthenticated GET."""
        r = self.client.get(f"/api/v1/event/{self.event.pk}/events_detail/")
        self.assertEqual(r.status_code, 200)

    def test_detail_authenticated_returns_200(self):
        self._auth()
        r = self.client.get(f"/api/v1/event/{self.event.pk}/events_detail/")
        self.assertEqual(r.status_code, 200)

    def test_detail_correct_event_returned(self):
        self._auth()
        r = self.client.get(f"/api/v1/event/{self.event.pk}/events_detail/")
        self.assertEqual(r.json()["event_name"], "Test Concert")

    def test_detail_invalid_pk_returns_404(self):
        self._auth()
        r = self.client.get("/api/v1/event/99999/events_detail/")
        self.assertEqual(r.status_code, 404)

    def test_detail_has_nested_venue(self):
        self._auth()
        r = self.client.get(f"/api/v1/event/{self.event.pk}/events_detail/")
        self.assertIn("venue_name", r.json()["venue"])

    def test_detail_has_nested_category(self):
        self._auth()
        r = self.client.get(f"/api/v1/event/{self.event.pk}/events_detail/")
        self.assertIn("segment", r.json()["category"])


# ─── Event update ──────────────────────────────────────────────────────────────


@override_settings(CACHES=NO_THROTTLE_CACHE)
class EventUpdateTests(TestCase):
    """PATCH /api/v1/event/{pk}/par_update/ — partial update."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="updateuser", password="pass")
        self.event = make_event()

    def _auth(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "updateuser", "password": "pass"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.json()['access']}")

    def test_patch_unauthenticated_returns_403(self):
        r = self.client.patch(
            f"/api/v1/event/{self.event.pk}/par_update/", {"event_name": "New"}
        )
        self.assertIn(r.status_code, [401, 403])

    def test_patch_authenticated_updates_field(self):
        self._auth()
        r = self.client.patch(
            f"/api/v1/event/{self.event.pk}/par_update/",
            {"event_name": "Updated Concert"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["event_name"], "Updated Concert")

    def test_patch_invalid_pk_returns_404(self):
        self._auth()
        r = self.client.patch(
            "/api/v1/event/99999/par_update/", {"event_name": "X"}, format="json"
        )
        self.assertEqual(r.status_code, 404)


# ─── Event delete ──────────────────────────────────────────────────────────────


@override_settings(CACHES=NO_THROTTLE_CACHE)
class EventDeleteTests(TestCase):
    """DELETE /api/v1/event/{pk}/del_event/ — delete event."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="deleteuser", password="pass")
        self.event = make_event()

    def _auth(self):
        r = self.client.post(
            "/api/v1/token/",
            {"username": "deleteuser", "password": "pass"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.json()['access']}")

    def test_delete_unauthenticated_returns_403(self):
        r = self.client.delete(f"/api/v1/event/{self.event.pk}/del_event/")
        self.assertIn(r.status_code, [401, 403])

    def test_delete_authenticated_removes_event(self):
        self._auth()
        pk = self.event.pk
        r = self.client.delete(f"/api/v1/event/{pk}/del_event/")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Event.objects.filter(pk=pk).exists())

    def test_delete_invalid_pk_returns_404(self):
        self._auth()
        r = self.client.delete("/api/v1/event/99999/del_event/")
        self.assertEqual(r.status_code, 404)
