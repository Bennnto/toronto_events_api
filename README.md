![Toronto](https://img.shields.io/badge/Toronto-Events_API-e8c547?style=flat&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMCA0MCI+CiAgPHJlY3QgeD0iOSIgeT0iMCIgd2lkdGg9IjIiIGhlaWdodD0iNiIgZmlsbD0id2hpdGUiLz4KICA8ZWxsaXBzZSBjeD0iMTAiIGN5PSI3IiByeD0iNCIgcnk9IjEuNSIgZmlsbD0id2hpdGUiLz4KICA8cmVjdCB4PSI4LjUiIHk9IjciIHdpZHRoPSIzIiBoZWlnaHQ9IjgiIGZpbGw9IndoaXRlIi8+CiAgPHBvbHlnb24gcG9pbnRzPSI2LDE1IDE0LDE1IDEyLDI4IDgsMjgiIGZpbGw9IndoaXRlIi8+CiAgPHJlY3QgeD0iNCIgeT0iMjgiIHdpZHRoPSIxMiIgaGVpZ2h0PSIyLjUiIHJ4PSIxIiBmaWxsPSJ3aGl0ZSIvPgogIDxwb2x5Z29uIHBvaW50cz0iMiw0MCAxOCw0MCAxNCwzMCA2LDMwIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K&logoColor=white)
![GitHub Created At](https://img.shields.io/github/created-at/bennnto/toronto_events_api?style=flat&logoColor=violet&logoSize=auto)
![GitHub last commit](https://img.shields.io/github/last-commit/Bennnto/toronto_events_api)
![Static Badge](https://img.shields.io/badge/python3-blue?style=flat&logo=python&logoColor=yellow)
![Static Badge](https://img.shields.io/badge/django-6.0.4-darkgreen?style=flat&logo=django&logoColor=greeen&logoSize=auto)
![Static Badge](https://img.shields.io/badge/gunicorn-wsgi-teal?style=flat&logo=gunicorn)
![Static Badge](https://img.shields.io/badge/PostgreSQL-db-lightblue?style=flat&logo=postgresql&logoColor=lightblue)



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
      and their commercial offers. Additionally it also incoporates production-oriented health checks for both livenessand readiness,<br>
      the database are responsive and the API is prepared to serve requests<br>

  <h5 id=Technology-stack>Tech Stack</h5>
