from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class BaseThrottle(AnonRateThrottle):
    scope = "base_anon"

class AuthThrottle(UserRateThrottle):
    scope = "base_auth"

