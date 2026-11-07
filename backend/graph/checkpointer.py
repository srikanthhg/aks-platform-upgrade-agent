from __future__ import annotations

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver


def create_checkpointer(database_url: str) -> tuple[psycopg.Connection, PostgresSaver]:
    """Create and initialize a PostgreSQL checkpointer.

    Call this from the API lifespan or worker startup, never at module import.
    The returned connection must remain open for the checkpointer's lifetime.
    """
    connection = psycopg.connect(
        database_url,
        autocommit=True,
        prepare_threshold=0,
        connect_timeout=10,
    )
    try:
        checkpointer = PostgresSaver(connection)
        checkpointer.setup()
        return connection, checkpointer
    except Exception:
        connection.close()
        raise
