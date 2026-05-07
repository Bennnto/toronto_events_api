![Toronto](https://img.shields.io/badge/Toronto-Events_API-e8c547?style=flat&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCA0MCI+CiAgPHJlY3QgeD0iOSIgeT0iMCIgd2lkdGg9IjIiIGhlaWdodD0iNiIgZmlsbD0id2hpdGUiLz4KICA8ZWxsaXBzZSBjeD0iMTAiIGN5PSI3IiByeD0iNCIgcnk9IjEuNSIgZmlsbD0id2hpdGUiLz4KICA8cmVjdCB4PSI4LjUiIHk9IjciIHdpZHRoPSIzIiBoZWlnaHQ9IjgiIGZpbGw9IndoaXRlIi8+CiAgPHBvbHlnb24gcG9pbnRzPSI2LDE1IDE0LDE1IDEyLDI4IDgsMjgiIGZpbGw9IndoaXRlIi8+CiAgPHJlY3QgeD0iNCIgeT0iMjgiIHdpZHRoPSIxMiIgaGVpZ2h0PSIyLjUiIHJ4PSIxIiBmaWxsPSJ3aGl0ZSIvPgogIDxwb2x5Z29uIHBvaW50cz0iMiw0MCAxOCw0MCAxNCwzMCA2LDMwIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K&logoColor=white)
![GitHub Created At](https://img.shields.io/github/created-at/bennnto/toronto_events_api?style=flat&logoColor=violet&logoSize=auto)
![GitHub last commit](https://img.shields.io/github/last-commit/Bennnto/toronto_events_api)
![Static Badge](https://img.shields.io/badge/python3-blue?style=flat&logo=python&logoColor=yellow)
![Static Badge](https://img.shields.io/badge/django-6.0.4-darkgreen?style=flat&logo=django&logoColor=greeen&logoSize=auto)
![Static Badge](https://img.shields.io/badge/gunicorn-wsgi-teal?style=flat&logo=gunicorn)
![Static Badge](https://img.shields.io/badge/redis-gray?logo=redis)
![Static Badge](https://img.shields.io/badge/Sentry-magenta?logo=sentry)
![Static Badge](https://img.shields.io/badge/PostgreSQL-db-lightblue?style=flat&logo=postgresql&logoColor=lightblue)<br>
![Static Badge](https://img.shields.io/badge/License-MIT-lightblue?style=flat)

**This project : Contains information licensed under the Open Government Licence – Toronto.**


## Toronto Event API 

<details>
<summary>Table of Contents</summary>

  - [About The Project](#about-the-project)
    - [Tech Stack](#technology-stack)
  - [Features](#features)
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


   #### About The Project  <a id="about-the-project"></a>
  A Django REST API has been developed to aggregate Toronto events and festivals from the Ticketmaster Discovery API and JSON‑LD<br>
  event data scraped from third‑party websites—into a unified data model comprising Event, Venue, Category, and Offer entities which<br>
  are accessible through a public, read‑only HTTP interface designed for client applications, dashboards, and downstream services.<br>
  The project prioritizes reliable robust data normalization, along with explicit modelling of relationships between events, their locations,<br>
  and their commercial offers. Additionally it also incoporates production-oriented health checks for both liveness and readiness,<br>
  the database are responsive and the API is prepared to serve requests<br>

<details>  
<summary id=technology-stack>Tech Stack</summary> 

*   Language and Runtime
    *   Python 3.12* 
*   Web Framework
    *   Django (Core Web framework)
    *   Django Rest Framework (API layer)
    *   Rest Framework Simplejwt (Authentication)  
*   DataBase
    *   stgreSQLTask Queue and SchedulingT - Celery (Async task execution)
    *   Redis (Celery message broker and result backend)
    *   Django\_Celery\_beat (Periodic task scheduling)
    *   Django\_Celery\_result (Task result storage)
*   API Documentation
    *   Drf spectacular
    *   Scalar UI
*   Utilities
    *   django\_filter
    *   Django\_cors-headers
    *   Gunicorn (Wsgi)
    *   Python\_dotenv  
*   Monitoring
    *   Sentry SDK

</details>


#### Features <a id="features"></a>
  *    Ingest data from reliable source Ticketmaster, JSON-LD Toronto Event
  *    Normalized data model and relation
  *    Read only public rest API
  *    Endpoints health check for liveness and DB / cache readiness
  *    Schema / Documentation by "drf-spectacular" and UI "Scalar UI"
  *    Rate Limit for anonymouse user and authenticated clients


#### Data Model <a id="data-models"></a>

 ##### Event Model 

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
  ##### Venue Model

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
  ##### Offer Model

```Python
    event = models.ForeignKey('Event', related_name='offers', on_delete=models.CASCADE, null=True)
    offer_type = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)
    sale_url = models.URLField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
  ##### Category Model

```Python
    segment = models.CharField(max_length=255, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    subgenre = models.CharField(max_length=255, blank=True)
```

#### Base API and Public Endpoints <a id="api"></a>
  *    Base URL <a id="base-url"></a>
        - API Base URL : `api.yyz.codes/`
    
  *    Event Endpoints  <a id="event-check"></a>
        -   List all events : `GET /api/v1/event/`
        -  Event and Detail by given ID : `GET /api/v1/event/{id}/`
    
  <li id=health-check>Health Endpoints</li>
    - Health Endpoint (API live)<br>
      <ul>
        <li>
          <mark> GET /api/v1/healthz</mark>
        </li>
      </ul>
    - Ready Endpoint (cache and DB)<br>
      <ul>
        <li>
          <mark> GET /api/v1/readyz</mark>
        </li>
      </ul>
</ul>

<h4 id=syncing>Syncing Data</h4>
  Toronto Events API aggregrate Toronto events and festivals from reliable sources<br>
    - <mark>ticketmaster discovery API (city : Toronto)</mark><br>
    - <mark>Toronto Opendata Event and Festival from CivicTech under Open Government Licence – Toronto.</mark><br>
  * All incoming data will normalized to fit with our data models Event, Venue, Offer and Category<br>
    before expose to public API<br>
  * Data is refreshed on a daily schedule using Celery and system crontab<br>
    - Celery tasks handle the actual ingestion and normalization work.<br>
    - Crontab entries trigger the Celery beat scheduler to run these tasks at configured times.<br>

<h4 id=ratelimit>Rate Limit and Authentication</h4>
The Toronto Events API is designed as a read‑heavy public service with simple <br>
JWT‑based authenticationand defensive rate limiting to keep the platform stable <br>
for all consumers.<br>
  <br>
  <strong>Rate Limit</strong> <br>
  To prevent abuse and accidental overuse, each client is limited by user type <br>
    - Anonymous User 10 request / day per IP Address<br>
    - Authenticated User 500 request / day per User <br>
  <br>
  <strong>Authentication</strong> <br>
    1. Register an account <br>
    2. Obtain an access token and refresh token : send your credential username, password to token endpoints to obtain<br>
    - access token life-time 30 mins <br>
    - refresh token life-time 1 day <br>
    3. Call API to access data : Include the access token in the ‎`Authorization` <br>
    - header:Authorization: Bearer YOUR_ACCESS_TOKEN<br>

<h4 id=documentation>Documentation</h4>
Toronto events public api ship with human-friendly scalar UI and Open API autogenerated schema <br>
Scalar UI <br>
to access : <mark>/api/v1/docs/</mark> <br>
  - A browsable list of endpoints grouped by tags (e.g. Events, Health). <br>
  - Detailed request/response examples.<br>
  - Query parameter and filter descriptions (via ‎`EventFilter` + ‎`extend_schema`).<br>
  - Live “Try It” forms to execute requests against your running API. <br>

<h4 id=license>Licenses</h4> 
The application source code is licensed under the MIT License.
Copyright © 2026 <copyright Bennnto>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.<br>
<br>
Event data from Toronto Open Data / CivicTech is provided under the Open Government Licence – Toronto. <br>
Event data sourced from Ticketmaster is subject to Ticketmaster’s terms of use and is not licensed by this repository. <br>
