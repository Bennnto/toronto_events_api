from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.decorators import action, api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.http import JsonResponse
from django.db import connections
from django.core.cache import caches
import time
from scalar.get_filter_parameters import get_filter_parameters


def _safe_filter_parameters(filter_cls):
    try:
        return get_filter_parameters(filter_cls)
    except Exception:
        return []
from .throttles import BaseThrottle, AuthThrottle
from .models import Event
from .serializers import EventSerializer
from .filters import EventFilter


class EventViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = EventSerializer
    filterset_class = EventFilter
    throttle_classes = [BaseThrottle, AuthThrottle]

    @extend_schema(
        description = 'Get All Event in DataBase',
        parameters = _safe_filter_parameters(EventFilter)
    )
    @action(detail=False, methods=['get'])
    def events_list(self, request):
        qs = Event.objects.all()
        filterset = self.filterset_class(request.GET, queryset=qs)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
        
        paginator = LimitOffsetPagination()
        page = paginator.paginate_queryset(filterset.qs, request, view=self)
        try :
            serializer = EventSerializer(page, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception :
            return Response({'error': 'Error Not Found Data'}, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        parameters=[OpenApiParameter("pk", int, description="Event id")],
        description='Get Event and Detail By Specified event_id'
        )
    @action(detail=True, methods=['get'])
    def events_detail(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
        parameters=[OpenApiParameter("pk", int, description="Event id")],
        description="Delete Specified Event by event_id"           
        )
    @action(detail=True, methods=['delete'])
    def del_event(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        if event :
            event.delete()
        return Response({'Meesage': f'Deleted Event id:{pk}'})
    
    @extend_schema(
        parameters=[OpenApiParameter("pk", int, description="Event id")],
        description="Partial updated event details by event_id"
        )
    @action(detail=True, methods=['put', 'patch'])
    def par_update(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

