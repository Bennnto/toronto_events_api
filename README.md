![GitHub Created At](https://img.shields.io/github/created-at/bennnto/toronto_events_api?style=flat&logoColor=violet&logoSize=auto)
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
