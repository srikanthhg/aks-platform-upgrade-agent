# ADR 0002: Separate API and worker

**Status:** Accepted

AKS upgrades are long-running and must not depend on an HTTP request remaining open. The API validates and queues requests; a dedicated worker executes workflows. This isolates user traffic from disruptive operations and enables restart recovery.
