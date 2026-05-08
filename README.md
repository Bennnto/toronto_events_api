![Toronto](https://img.shields.io/badge/Toronto-Events_API-e8c547?style=flat&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCA0MCI+CiAgPHJlY3QgeD0iOSIgeT0iMCIgd2lkdGg9IjIiIGhlaWdodD0iNiIgZmlsbD0id2hpdGUiLz4KICA8ZWxsaXBzZSBjeD0iMTAiIGN5PSI3IiByeD0iNCIgcnk9IjEuNSIgZmlsbD0id2hpdGUiLz4KICA8cmVjdCB4PSI4LjUiIHk9IjciIHdpZHRoPSIzIiBoZWlnaHQ9IjgiIGZpbGw9IndoaXRlIi8+CiAgPHBvbHlnb24gcG9pbnRzPSI2LDE1IDE0LDE1IDEyLDI4IDgsMjgiIGZpbGw9IndoaXRlIi8+CiAgPHJlY3QgeD0iNCIgeT0iMjgiIHdpZHRoPSIxMiIgaGVpZ2h0PSIyLjUiIHJ4PSIxIiBmaWxsPSJ3aGl0ZSIvPgogIDxwb2x5Z29uIHBvaW50cz0iMiw0MCAxOCw0MCAxNCwzMCA2LDMwIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K&logoColor=white)
![GitHub Created At](https://img.shields.io/github/created-at/bennnto/toronto_events_api?style=flat&logoColor=violet&logoSize=auto)
![GitHub last commit](https://img.shields.io/github/last-commit/Bennnto/toronto_events_api)
![Static Badge](https://img.shields.io/badge/python-3.12-blue?style=flat&logo=python&logoColor=yellow)
![Static Badge](https://img.shields.io/badge/django-6.0.4-darkgreen?style=flat&logo=django&logoColor=green&logoSize=auto)
![Static Badge](https://img.shields.io/badge/gunicorn-wsgi-teal?style=flat&logo=gunicorn)
![Static Badge](https://img.shields.io/badge/redis-gray?logo=redis)
![Static Badge](https://img.shields.io/badge/Sentry-magenta?logo=sentry)
![Static Badge](https://img.shields.io/badge/PostgreSQL-db-lightblue?style=flat&logo=postgresql&logoColor=lightblue)
![Static Badge](https://img.shields.io/badge/License-MIT-lightblue?style=flat)

> **This project contains information licensed under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/).**

---

# Toronto Event API

A Django REST API that aggregates Toronto events and festivals from the **Ticketmaster Discovery API** and **JSON‑LD event data** published by Toronto Open Data — unified into a normalized data model of **Event**, **Venue**, **Category**, and **Offer** entities, and served through a public, read‑only HTTP interface designed for client applications, dashboards, and downstream services.

The project prioritizes robust data normalization, explicit modelling of relationships between events, their locations, and their commercial offers, and incorporates production-oriented health checks for both liveness and readiness — ensuring the database is responsive and the API is prepared to serve traffic.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [Data Syncing](#data-syncing)
- [Rate Limits & Authentication](#rate-limits--authentication)
- [Documentation](#documentation)
- [License](#license)

## Features

- 🔄 **Multi-source ingestion** — Ticketmaster Discovery API and Toronto Open Data JSON‑LD
- 🗃️ **Normalized data model** — Events, Venues, Categories, and Offers with explicit relationships
- 🔒 **Read-only public API** — Safe, predictable GET endpoints for all consumers
- 🩺 **Health checks** — Liveness (`/healthz`) and readiness (`/readyz`) endpoints for monitoring
- 📖 **Interactive documentation** — Auto-generated OpenAPI schema with Scalar UI
- 🚦 **Rate limiting** — Tiered limits for anonymous and authenticated clients
- 🔑 **JWT authentication** — Token-based access for higher rate limits
- 📍 **Geolocation data** — Latitude and longitude on every venue for map-based applications

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.12 |
| **Web Framework** | Django 6.0 · Django REST Framework |
| **Database** | PostgreSQL |
| **Cache / Broker** | Redis |
| **Task Queue** | Celery · django-celery-beat · django-celery-results |
| **Authentication** | Simple JWT |
| **API Docs** | drf-spectacular · Scalar UI |
| **WSGI Server** | Gunicorn |
| **Static Files** | WhiteNoise |
| **Monitoring** | Sentry SDK |
| **Utilities** | django-filter · django-cors-headers · python-dotenv |

## Architecture

```
┌─────────────────────┐     ┌──────────────────┐
│  Ticketmaster API   │     │  Toronto Open     │
│  (Discovery v2)     │     │  Data (JSON‑LD)   │
└────────┬────────────┘     └────────┬─────────┘
         │                           │
         ▼                           ▼
┌──────────────────────────────────────────────┐
│          Celery Workers (sync tasks)         │
│     normalize → deduplicate → upsert         │
└────────────────────┬─────────────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │ PostgreSQL   │
              │ (Event, Venue│
              │  Category,   │
              │  Offer)      │
              └──────┬──────┘
                     │
                     ▼
┌──────────────────────────────────────────────┐
│       Django REST Framework (Gunicorn)       │
│   GET /api/v1/events/  ·  GET /healthz/      │
└──────────────────────────────────────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │   Client Apps /     │
          │   Dashboards /      │
          │   Map Interfaces    │
          └─────────────────────┘
```

## Data Models

### Entity Relationship

```
Category ──< Event >── Venue
                │
                └──< Offer
```

*One Category has many Events. One Venue hosts many Events. One Event has many Offers.*

### Event

| Field | Type | Description |
|---|---|---|
| `ext_id` | CharField | External ID from source |
| `event_name` | CharField | Name of the event |
| `description` | TextField | Event description |
| `event_url` | URLField | Link to event page |
| `sale_status` | CharField | Ticket sale status |
| `category` | ForeignKey → Category | Event classification |
| `venue` | ForeignKey → Venue | Event location |
| `sale_start_date` | DateTimeField | When tickets go on sale |
| `sale_end_date` | DateTimeField | When ticket sales end |
| `event_start_date` | DateTimeField | Event date and time |
| `created_at` | DateTimeField | Record creation timestamp |

### Venue

| Field | Type | Description |
|---|---|---|
| `venue_name` | CharField | Name of the venue |
| `venue_type` | CharField | Type of venue |
| `seat_map` | URLField | Seat map image URL |
| `address` | CharField | Street address |
| `city` | CharField | City |
| `country` | CharField | Country |
| `latitude` | DecimalField | GPS latitude (6 decimal places) |
| `longitude` | DecimalField | GPS longitude (6 decimal places) |

### Offer

| Field | Type | Description |
|---|---|---|
| `event` | ForeignKey → Event | Associated event |
| `offer_type` | CharField | Type of offer |
| `price` | DecimalField | Ticket price |
| `currency` | CharField | Currency code (e.g. CAD) |
| `sale_url` | URLField | Direct purchase link |
| `created_at` | DateTimeField | Record creation timestamp |

### Category

| Field | Type | Description |
|---|---|---|
| `segment` | CharField | Top-level classification (e.g. Music, Sports) |
| `genre` | CharField | Genre within segment |
| `subgenre` | CharField | Sub-genre |

## API Endpoints

**Base URL**

```
https://api.yyz.codes
```

### Events (Public, Read-Only)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/events/` | List all events (paginated, filterable) |
| `GET` | `/api/v1/events/{id}/` | Retrieve a single event by ID |

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/healthz/` | Liveness check — is the API running? |
| `GET` | `/api/v1/readyz/` | Readiness check — are the database and cache connected? |

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/token/` | Obtain access + refresh tokens |
| `POST` | `/api/v1/token/refresh/` | Refresh an expired access token |
| `POST` | `/api/v1/token/verify/` | Verify a token's validity |

### Documentation

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/docs/` | Scalar UI — interactive API explorer |
| `GET` | `/api/v1/schema/` | OpenAPI 3.0 schema (JSON) |

## Data Syncing

The API aggregates events from two reliable sources:

| Source | Method | Scope |
|---|---|---|
| **Ticketmaster Discovery API** | REST API | Events in the Toronto market |
| **Toronto Open Data (CivicTech)** | JSON‑LD file import | Festivals and civic events |

### Sync Pipeline

1. **Fetch** — Raw data is retrieved from each source
2. **Normalize** — Fields are mapped to the unified data model (Event, Venue, Offer, Category)
3. **Deduplicate** — Events are matched by external ID to avoid duplicates
4. **Upsert** — New events are created; existing events are updated

### Schedule

Data is refreshed on a **daily schedule** using Celery Beat:

- **Celery workers** handle the ingestion and normalization tasks
- **Celery Beat** triggers the workers at configured times via crontab

## Rate Limits & Authentication

The API is designed as a read-heavy public service with JWT-based authentication and defensive rate limiting.

### Rate Limits

| Client Type | Limit |
|---|---|
| Anonymous | **10 requests / day** (per IP) |
| Authenticated | **500 requests / day** (per user) |

### Getting Authenticated Access

1. **Register** an account at `/register/`
2. **Obtain tokens** — `POST /api/v1/token/` with your username and password
   - Access token lifetime: **30 minutes**
   - Refresh token lifetime: **1 day**
3. **Call the API** — include the token in the `Authorization` header:
   ```
   Authorization: Bearer YOUR_ACCESS_TOKEN
   ```

## Documentation

The API ships with interactive documentation powered by **Scalar UI** and an auto-generated **OpenAPI 3.0** schema via drf-spectacular.

**Access at:** [`/api/v1/docs/`](https://api.yyz.codes/api/v1/docs/)

- Browsable endpoint list grouped by tags (Events, Admin Events, Health)
- Detailed request/response examples
- Query parameter and filter descriptions
- Live **"Try It"** forms to execute requests directly

## License

### Source Code

The application source code is licensed under the **MIT License**.

Copyright © 2026 Bennnto

> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

### Data

- Event data from **Toronto Open Data / CivicTech** is provided under the [Open Government Licence – Toronto](https://open.toronto.ca/open-data-licence/).
- Event data sourced from **Ticketmaster** is subject to [Ticketmaster's terms of use](https://developer.ticketmaster.com/support/terms-of-use/) and is not licensed by this repository.
