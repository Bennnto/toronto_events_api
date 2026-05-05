## Toronto Event API 
<summmary>Table of Contents</summmary>
  <ul>
    <li><a href=#About-the-project>About The project</li>
      <ul>
        <li><a href=#Technology-stack>Tech Stack</a></li>
      </ul>
    <li><a href=#Feature>Features</a></li>
    <li><a href=#Data-model>Data Models</a></li>
    <li><a href=#API>API</a></li>
      <ul>
        <li><a href=#Base-url>Base URL</a></li>
        <li><a href=#Events-check>Event Endpoints</li>
        <li><a href=#Health-check>Health Endpoints</li>
      </ul>
    <li><a href=#Syncing>Syncing Data</li>
      <ul>
        <li><a href=#Tkmaster>Ticket Master</a></li>
        <li><a href=#Jsonld>Jsonld</a></li>
      </ul>
    <li><a href=#ratelimit>Rate Limit and Authentication</a></li>
    <li><a href=#Documentation>Documentations</a></li>
    <li><a href=#license>Licenses</a></li>
  </ul>

  <h4 id=About-the-project>About the project</h4>
      A Django REST API has been developed to aggregate Toronto events and festivals from the Ticketmaster Discovery API and JSON‑LD<br>
      event data scraped from third‑party websites—into a unified data model comprising Event, Venue, Category, and Offer entities which<br>
      are accessible through a public, read‑only HTTP interface designed for client applications, dashboards, and downstream services.<br>
      The project prioritizes reliable robust data normalization, along with explicit modelling of relationships between events, their locations,<br>
      and their commercial offers. Additionally it also incoporates production-oriented health checks for both livenessand readiness,<br>
      the database are responsive and the API is prepared to serve requests<br>
