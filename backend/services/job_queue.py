from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from typing import Any
import psycopg
from psycopg.rows import dict_row
from config import get_settings

class JobQueue:
    def __init__(self): self.database_url=get_settings().database_url; self._init()
    def _init(self):
        with psycopg.connect(self.database_url,autocommit=True) as c:
            c.execute("""CREATE TABLE IF NOT EXISTS workflow_jobs(id bigserial PRIMARY KEY, thread_id text NOT NULL, job_type text NOT NULL,payload jsonb NOT NULL, status text NOT NULL DEFAULT 'queued', attempts int NOT NULL DEFAULT 0,lease_until timestamptz, error text, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now())""")
            c.execute("CREATE INDEX IF NOT EXISTS ix_workflow_jobs_claim ON workflow_jobs(status,lease_until,created_at)")
            c.execute("CREATE INDEX IF NOT EXISTS ix_workflow_jobs_thread ON workflow_jobs(thread_id,created_at DESC)")
    def enqueue(self,thread_id:str,job_type:str,payload:dict[str,Any])->int:
        with psycopg.connect(self.database_url) as c:
            row=c.execute("INSERT INTO workflow_jobs(thread_id,job_type,payload) VALUES (%s,%s,%s::jsonb) RETURNING id",(thread_id,job_type,json.dumps(payload,default=str))).fetchone(); c.commit(); return int(row[0])
    def claim(self,lease_minutes:int=180)->dict[str,Any]|None:
        now=datetime.now(timezone.utc); lease=now+timedelta(minutes=lease_minutes)
        with psycopg.connect(self.database_url,row_factory=dict_row) as c:
            row=c.execute("""SELECT * FROM workflow_jobs WHERE status='queued' OR (status='running' AND lease_until < %s) ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 1""",(now,)).fetchone()
            if not row: c.commit(); return None
            updated=c.execute("UPDATE workflow_jobs SET status='running',attempts=attempts+1,lease_until=%s,updated_at=%s WHERE id=%s RETURNING *",(lease,now,row['id'])).fetchone(); c.commit(); return dict(updated)
    def complete(self,job_id:int):
        with psycopg.connect(self.database_url,autocommit=True) as c:c.execute("UPDATE workflow_jobs SET status='completed',lease_until=NULL,updated_at=now() WHERE id=%s",(job_id,))
    def fail(self,job_id:int,error:str,retry:bool=False):
        status='queued' if retry else 'failed'
        with psycopg.connect(self.database_url,autocommit=True) as c:c.execute("UPDATE workflow_jobs SET status=%s,error=%s,lease_until=NULL,updated_at=now() WHERE id=%s",(status,error[:4000],job_id))
    def latest(self,thread_id:str)->dict[str,Any]|None:
        with psycopg.connect(self.database_url,row_factory=dict_row) as c:
            row=c.execute("SELECT * FROM workflow_jobs WHERE thread_id=%s ORDER BY created_at DESC LIMIT 1",(thread_id,)).fetchone(); return dict(row) if row else None
