# API overview

Base path: `/api/v1`

- `GET /me` — authenticated identity and roles
- `POST /workflows` — queue a workflow
- `GET /workflows/{thread_id}` — workflow state
- `POST /workflows/{thread_id}/approve` — approve a paused warning
- `POST /workflows/{thread_id}/reject` — reject a paused warning
- `GET /workflows/{thread_id}/reports/{stage}` — Markdown report
- `GET /audit?limit=50` — recent audit events

Interactive OpenAPI documentation is available at `/docs`.
