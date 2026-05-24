from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db import connections
from django.core.cache import caches
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
import time
import os
from dotenv import load_dotenv
from scalar.get_filter_parameters import get_filter_parameters

load_dotenv()

def _safe_filter_parameters(filter_cls):
    try:
        return get_filter_parameters(filter_cls)
    except Exception:
        return []
from .throttles import BaseThrottle, AuthThrottle, AdminThrottle
from .models import Event, Venue
from .serializers import EventSerializer, VenueSerializer
from .filters import EventFilter, VenueFilter
from .forms import Registry_Form, Login_Form
from dotenv import load_dotenv
import os

load_dotenv()

@extend_schema_view(
    list=extend_schema(
        tags=['Events'],
        description='List all events with optional filters.',
        parameters=_safe_filter_parameters(EventFilter)
    ),
    retrieve=extend_schema(
        tags=['Events'],
        parameters=[OpenApiParameter("pk", int, description="Event id")],
        description='Retrieve event by id.',
    ),
)
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = EventSerializer
    filterset_class = EventFilter
    throttle_classes = [BaseThrottle, AuthThrottle]
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['event_name', 'category__category__name', 'venue__venue_name']

    def list(self, request, *args, **kwargs):
        queryset = self.filterset_class(request.GET, queryset=self.get_queryset())
        if not queryset.is_valid():
            return Response({"Error": "Couldn't retrieve information from DB"})
        page = self.paginate_queryset(queryset.qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    

@extend_schema_view(
    list=extend_schema(
        tags=['Admin Events'],
        description='List all events with optional filters.',
    ),
    retrieve=extend_schema(
        tags=['Admin Events'],
        description='Retrieve event by id.',
    ),
    create=extend_schema(
        tags=['Admin Events'],
        description='Create a new event.'
    ),
    update=extend_schema(
        tags=['Admin Events'],
        description='Update exisiting events.'
    ),
    partial_update=extend_schema(
        tags=['Admin Events'],
        description='Partials update existing events.'
    ),
    destroy=extend_schema(
        tags=['Admin Events'],
        description='Delete events from database'
    ),
)
class AdminEventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsAdminUser]
    filterset_class = EventFilter
    serializer_class = EventSerializer
    pagination_class = LimitOffsetPagination
    throttle_classes = [AdminThrottle]
    filter_backends= [DjangoFilterBackend, SearchFilter]
    search_fields = ['event_name', 'category__category__name', 'venue__venue_name']

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VenueSerializer
    filterset_class = VenueFilter
    throttle_classes = [BaseThrottle, AuthThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['venue_name', 'address']
    pagination_class = LimitOffsetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filterset_class(request.GET, queryset=self.get_queryset())
        if not queryset.is_valid():
            return Response({"Error": "Couldn't retrieve information from DB"})
        page = self.paginate_queryset(queryset.qs) 
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)    

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([BaseThrottle, AuthThrottle])
@extend_schema(
    tags=['Health'],
    description = 'Liveness Probe - application process is alive',
    responses ={200: {'example': {"status": "alive", "time": 1714775400.123}}}
)
def healthz(request):
    return JsonResponse({"status": "alive", "time": time.time()})

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([BaseThrottle, AuthThrottle])
@extend_schema(
    tags=['Health'],
    description = 'Readiness probe - check DB and Cache Return 503 if unavailable',
    responses={
        200: {'example': {"status": "ready", "checks": {"database": {"status": "ok", "latency_ms": 2.5}}}},
        503: {'example': {"status": "not_ready", "checks": {"database": {"status": "error", "error": "connection failed"}}}}
    }
)
def readyz(request):
    checks = {}
    ok = True
    try:
        start = time.time()
        with connections['default'].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks['database'] = {"status": "ok", "latency_ms": round((time.time() - start) * 1000, 1)}
    except Exception as e:
        checks['database'] = {"status": "error", "error": str(e)}
        ok = False
    
    try:
        start = time.time()
        cache = caches['default']
        cache.set("_hc", "1", timeout=10)
        if cache.get("_hc") == "1":
            checks['cache'] = {"status": "ok", "latency_ms": round((time.time() - start) * 1000, 1)}
        else:
            checks['cache'] = {"status": "error", "error": "cache read/write failed"}
            ok = False
    except Exception as e:
        checks['cache'] = {"status": "error", "error": str(e)}
        ok = False
    
    status_code = 200 if ok else 503
    return JsonResponse({"status": "ready" if ok else "not_ready", "checks": checks}, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([BaseThrottle, AuthThrottle])
def event_count(request):
    from .models import Event

    try:
        total = Event.objects.count()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"total_events": total})

def user_register(request):
    if request.method == "POST":
        form = Registry_Form(request.POST)
        if form.is_valid():
            user = form.save()
            email_message = f"""Your Toronto Event APIs Account Created Successfully\n\nTo Obtain Access Token and Refresh Token Please Send\nYour Credential username={user.username} and your password to Token Endpoint.\n\n(Please do not reply to this Email)"""
            send_mail(
                subject="Toronto Event APIs Account Created Successfully",
                message=email_message,
                from_email=os.getenv("EMAIL_HOST_USER"),
                recipient_list=[user.email],
            )
            messages.success(request, "Check your email for account confirmation")
            return redirect('login')
    else:
        form = Registry_Form()
    context = {
        'form': form
    }
    return render(request, 'register.html', context)

def user_login(request):
    if request.method == "POST":
        form = Login_Form(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Form validation failed")
    else:
        form = Login_Form()
    context = {
        'form': form
    }
    return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('login')


@login_required(login_url='login')
def home(request):
    from django.conf import settings
    rate = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]
    if request.user.is_staff:
        rate_limit = rate["base_admin"]
    elif request.user.is_authenticated:
        rate_limit = rate["base_auth"]
    else:
        rate_limit = rate["base_anon"]
    total_events = Event.objects.count()
    #Key DRF Use for UserRateThrottle
    if request.user.is_staff :
        key = f"throttle_base_admin_{request.user.pk}"
    else:
        key = f"throttle_base_auth_{request.user.pk}"
    
    from django.core.cache import cache
    history = cache.get(key, [])
    requests_today = len(history)
    if request.user.is_staff :
        remaining_limit = 1500 - len(history)
    elif request.user.is_authenticated:
        remaining_limit = 500 - len(history)
    else:
        remaining_limit = 10 - len(history)

    start = time.time()
    with connections['default'].cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    db_latency_ms = round((time.time() - start) * 1000, 1)

    context = {
        'user': request.user,
        'rate_limit': rate_limit,
        'total_events': total_events,
        'remaining_limit': remaining_limit,
        'requests_today': requests_today,
        'db_latency_ms': db_latency_ms,
    }
    return render(request, 'home.html', context)

def reset_password(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request,
            from_email = os.getenv('EMAIL_HOST_USER'),
            subject_template_name = 'password_reset_subject.txt',
            email_template_name = 'password_reset_email.html',
            )
        messages.success(request, "Check your email for password reset confirmation")
        return redirect('password_reset_done')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})
