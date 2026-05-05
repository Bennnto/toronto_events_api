![Toronto](https://img.shields.io/badge/Toronto-Events_API-e8c547?style=for-the-badge&logo=data:image/svg%2Bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCI+CiAgPCEtLSBTa3kgYmFja2dyb3VuZCAtLT4KICA8cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iIzFhMWEyZSIvPgoKICA8IS0tIENOIFRvd2VyIHNpbGhvdWV0dGUgLS0+CiAgPCEtLSBCYXNlIHBsYXRmb3JtIC0tPgogIDxyZWN0IHg9IjMwIiB5PSI3MiIgd2lkdGg9IjQwIiBoZWlnaHQ9IjYiIHJ4PSIyIiBmaWxsPSIjZThjNTQ3Ii8+CiAgPCEtLSBMb3dlciB0b3dlciBib2R5IC0tPgogIDxwb2x5Z29uIHBvaW50cz0iMzgsNzIgNjIsNzIgNTYsMzggNDQsMzgiIGZpbGw9IiNlOGM1NDciLz4KICA8IS0tIFVwcGVyIHNoYWZ0IC0tPgogIDxyZWN0IHg9IjQ2IiB5PSIxOCIgd2lkdGg9IjgiIGhlaWdodD0iMjAiIHJ4PSIxIiBmaWxsPSIjZThjNTQ3Ii8+CiAgPCEtLSBQb2Qvb2JzZXJ2YXRpb24gZGVjayAtLT4KICA8ZWxsaXBzZSBjeD0iNTAiIGN5PSIzOCIgcng9IjEwIiByeT0iNCIgZmlsbD0iI2Yw
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
