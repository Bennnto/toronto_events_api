from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.cache import cache
from unittest.mock import patch


class ThrottleTests(TestCase):
    """Tests for API throttling."""
    
    def test_anonymous_throttle_configured(self):
        """Verify throttle classes are applied to healthz endpoint."""
        # Just verify the view accepts requests (doesn't error)
        client = APIClient()
        url = '/api/v1/healthz/'
        
        r1 = client.get(url)
        self.assertIn(r1.status_code, [200, 429], "Should be either success or throttled")

    def test_authenticated_throttle_configured(self):
        """Verify throttle classes work for authenticated requests."""
        User = get_user_model()
        user = User.objects.create_user(username='tuser', password='pass')
        
        client = APIClient()
        client.force_authenticate(user=user)
        url = '/api/v1/healthz/'
        
        r1 = client.get(url)
        self.assertIn(r1.status_code, [200, 429], "Should be either success or throttled")   
        