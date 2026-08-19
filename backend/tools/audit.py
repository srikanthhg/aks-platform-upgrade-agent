from __future__ import annotations
import json
from datetime import datetime, timezone
import psycopg
from psycopg.rows import dict_row
from config import get_settings
_initialized=False
def _init():
    global _initialized
    if _initialized:return
    with psycopg.connect(get_settings().database_url,autocommit=True) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS audit_events(id bigserial PRIMARY KEY,event_time timestamptz NOT NULL,event_type text NOT NULL,actor text NOT NULL,details jsonb NOT NULL)""");c.execute('CREATE INDEX IF NOT EXISTS ix_audit_events_time ON audit_events(event_time DESC)')
    _initialized=True
def write_audit(event_type:str,actor:str,details:dict):
    _init();now=datetime.now(timezone.utc);print(json.dumps({'time':now.isoformat(),'event_type':event_type,'actor':actor,'details':details},default=str),flush=True)
    with psycopg.connect(get_settings().database_url,autocommit=True) as c:c.execute('INSERT INTO audit_events(event_time,event_type,actor,details) VALUES (%s,%s,%s,%s::jsonb)',(now,event_type,actor,json.dumps(details,default=str)))
def read_audit(limit:int=50):
    _init()
    with psycopg.connect(get_settings().database_url,row_factory=dict_row) as c:return list(c.execute('SELECT id,event_time,event_type,actor,details FROM audit_events ORDER BY event_time DESC LIMIT %s',(limit,)).fetchall())
