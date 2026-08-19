from __future__ import annotations
import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from config import get_settings
_settings=get_settings()
_connection=psycopg.connect(_settings.database_url, autocommit=True, prepare_threshold=0)
checkpointer=PostgresSaver(_connection)
checkpointer.setup()
