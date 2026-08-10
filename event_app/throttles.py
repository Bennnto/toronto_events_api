from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BaseThrottle(AnonRateThrottle):
    scope = "base_anon"


class AuthThrottle(UserRateThrottle):
    scope = "base_auth"


class AdminThrottle(UserRateThrottle):
    scope = "base_admin"
