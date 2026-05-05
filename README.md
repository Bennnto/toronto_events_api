![Toronto](https://img.shields.io/badge/Toronto-Events_API-e8c547?style=flat&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCA0MCI+CiAgPHJlY3QgeD0iOSIgeT0iMCIgd2lkdGg9IjIiIGhlaWdodD0iNiIgZmlsbD0id2hpdGUiLz4KICA8ZWxsaXBzZSBjeD0iMTAiIGN5PSI3IiByeD0iNCIgcnk9IjEuNSIgZmlsbD0id2hpdGUiLz4KICA8cmVjdCB4PSI4LjUiIHk9IjciIHdpZHRoPSIzIiBoZWlnaHQ9IjgiIGZpbGw9IndoaXRlIi8+CiAgPHBvbHlnb24gcG9pbnRzPSI2LDE1IDE0LDE1IDEyLDI4IDgsMjgiIGZpbGw9IndoaXRlIi8+CiAgPHJlY3QgeD0iNCIgeT0iMjgiIHdpZHRoPSIxMiIgaGVpZ2h0PSIyLjUiIHJ4PSIxIiBmaWxsPSJ3aGl0ZSIvPgogIDxwb2x5Z29uIHBvaW50cz0iMiw0MCAxOCw0MCAxNCwzMCA2LDMwIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K&logoColor=white)
![GitHub Created At](https://img.shields.io/github/created-at/bennnto/toronto_events_api?style=flat&logoColor=violet&logoSize=auto)
![GitHub last commit](https://img.shields.io/github/last-commit/Bennnto/toronto_events_api)
![Static Badge](https://img.shields.io/badge/python3-blue?style=flat&logo=python&logoColor=yellow)
![Static Badge](https://img.shields.io/badge/django-6.0.4-darkgreen?style=flat&logo=django&logoColor=greeen&logoSize=auto)
![Static Badge](https://img.shields.io/badge/gunicorn-wsgi-teal?style=flat&logo=gunicorn)
![Static Badge](https://img.shields.io/badge/redis-gray?logo=redis)
![Static Badge](https://img.shields.io/badge/Sentry-magenta?logo=sentry)
![Static Badge](https://img.shields.io/badge/PostgreSQL-db-lightblue?style=flat&logo=postgresql&logoColor=lightblue)<br>
**This project : Contains information licensed under the Open Government Licence – Toronto.**


## Toronto Event API 

<details>
<summary>Table of Contents</summary>

  - [About The Project](#about-the-project)
    - [Tech Stack](#technology-stack)
  - [Features](#feature)
  - [Data Models](#data-model)
  - [API](#api)
    - [Base URL](#base-url)
    - [Event Endpoints](#events-check)
    - [Health Endpoints](#health-check)
  - [Syncing Data](#syncing)
    - [Ticket Master](#tkmaster)
    - [Jsonld](#jsonld)
  - [Rate Limit and Authentication](#ratelimit)
  - [Documentation](#documentation)
  - [Licenses](#license)

</details>


  <h4 id=About-the-project>About the project</h4>
        A Django REST API has been developed to aggregate Toronto events and festivals from the Ticketmaster Discovery API and JSON‑LD<br>
      event data scraped from third‑party websites—into a unified data model comprising Event, Venue, Category, and Offer entities which<br>
      are accessible through a public, read‑only HTTP interface designed for client applications, dashboards, and downstream services.<br>
      The project prioritizes reliable robust data normalization, along with explicit modelling of relationships between events, their locations,<br>
      and their commercial offers. Additionally it also incoporates production-oriented health checks for both liveness and readiness,<br>
      the database are responsive and the API is prepared to serve requests<br>

<details>
  <summary id=Technology-stack>Tech Stack</summary>
    <ul>
    <li>Language and Runtime</li>
      - Python 3.12 
    <li>Web Framework</li>
      - Django (Core Web framework)<br>
      - Django Rest Framework (API layer)<br>
      - Rest Framework Simplejwt (Authentication)<br>
    <li>DataBase</li>
      - PostgreSQL<br<
    <li>Task Queue and Scheduling</li>T
      - Celery (Async task execution)<br>
      - Redis (Celery message broker and result backend)<br>
      - Django_Celery_beat (Periodic task scheduling)<br>
      - Django_Celery_result (Task result storage)<br>
    <li<>API Documentation</li>
      - Drf spectacular<br>
      - Scalar<br>
    <li>Utilities</li>
      - Django_filter<br>
      - Django_cors-headers<br>
      - Gunicorn (Wsgi)<br>
      - Python_dotenv<br>
    <li>Monitoring</li>
      - Sentry SDK<br>
    </ul>
  
</details>

<h4 id=feature>Features</h4>
<ul>
  <li>Ingest data from reliable source Ticketmaster, JSON-LD Toronto Event</li>
  <li>Normalized data model and relation</li>
  <li>Read only public rest API</li>
  <li>Endpoints health check for liveness and DB / cache readiness</li>
  <li>Schema / Documentation by "drf-spectacular" and UI "Scalar UI"</li>
  <li>Rate limit for anonymouse user and authenticated clients</li>
</ul>

<h4 id=data-model>Data Model</h4>
  <h5>Event Model</h5>

```Python
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
```
  <h5>Venue Model</h5>

```Python
    venue_name = models.CharField(max_length=255)
    venue_type = models.CharField(max_length=255)
    seat_map = models.URLField(max_length=1000, blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
```
  <h5>Offer Model</h5>

```Python
    event = models.ForeignKey('Event', related_name='offers', on_delete=models.CASCADE, null=True)
    offer_type = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    sale_url = models.URLField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
  <h5>Category Model</h5>

```Python
    segment = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    subgenre = models.CharField(max_length=255, blank=True)
```

<h4 id=api>API Base URL and Endpoints</h4>
<ul>
  <li>Base URL</li>
    - API Base URL
      <ul>
        <li>
          <mark>api.yyz.codes/</mark>
        </li>
      </ul> 
  <li id=events-check>Event Endpoints</li>
    - List all events<br>
      <ul>
        <li>
          <mark>api.yyz.codes/api/v1/event/events_list/</mark>
        </li>
      </ul>
    - Event and Detail by given ID<br>
      <ul>
        <li>
          <mark>api.yyz.codes/api/v1/event/{id}/events_detail/</mark>
        </li>
      </ul>
  <li id=health-check>Health Endpoints</li>
    - Health Endpoint (API live)<br>
      <ul>
        <li>
          <mark>api.yyz.codes/api/v1/healthz</mark>
        </li>
      </ul>
    - Ready Endpoint (cache and DB)<br>
      <ul>
        <li>
          <mark>api.yyz.codes/api/v1/readyz</mark>
        </li>
      </ul>
</ul>

<h4 id=syncing>Syncing Data</h4>
<
    
