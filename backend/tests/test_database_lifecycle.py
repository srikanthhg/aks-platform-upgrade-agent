from __future__ import annotations

import psycopg

from services.job_queue import JobQueue
from services.locks import ClusterLockStore


def test_database_service_constructors_do_not_connect(monkeypatch):
    """Importing/constructing services must not require a reachable database."""
    def unexpected_connect(*args, **kwargs):
        raise AssertionError("Database connection attempted during construction")

    monkeypatch.setattr(psycopg, "connect", unexpected_connect)

    queue = JobQueue("postgresql://user:pass@localhost:5432/test")
    locks = ClusterLockStore("postgresql://user:pass@localhost:5432/test")

    assert queue.database_url.endswith("/test")
    assert locks.database_url.endswith("/test")
