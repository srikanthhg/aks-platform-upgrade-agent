# ADR 0001: PostgreSQL for durable workflow state

**Status:** Accepted

SQLite and local files do not support resilient multi-replica Container Apps deployments. PostgreSQL is used for LangGraph checkpoints, queueing, locks, audit events, and report storage. This centralizes durable state and permits API replicas to remain stateless.
