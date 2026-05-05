from django.http import HttpResponse
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from rest_framework.permissions import AllowAny


def scalar_viewer(request):
    openapi_url = "/api/v1/schema/"
    title = "Toronto Event Public API"
    scalar_js_url = "https://cdn.jsdelivr.net/npm/@scalar/api-reference"
    scalar_proxy_url = ""
    scalar_favicon_url = "/static/favicon.ico"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" href="{scalar_favicon_url}">
        <link rel="stylesheet" href="/static/scalar.css">
        <style>
        body {{
            margin: 0;
            padding: 0;
        }}
        </style>
    </head>
    <body>
        <noscript>
            Scalar requires Javascript to function. Please enable it to browse the documentation.
        </noscript>
        <script
            id="api-reference"
            data-url="{openapi_url}"
            data-proxy-url="{scalar_proxy_url}"
            >
        </script>
        <script src="{scalar_js_url}"></script>
    </body>
    </html>
    """
    return HttpResponse(html)


urlpatterns_scalar = [
    path("api/v1/schema/", SpectacularAPIView.as_view(permission_classes=[AllowAny]), name="schema"),
    path("api/v1/docs/", scalar_viewer, name="docs"),
]