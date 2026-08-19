from __future__ import annotations
from datetime import datetime, timedelta, timezone
import psycopg
from config import get_settings
class ClusterLockConflict(RuntimeError): pass
class ClusterLockStore:
    def __init__(self,database_url: str|None=None): self.database_url=database_url or get_settings().database_url; self._init()
    def _connect(self): return psycopg.connect(self.database_url, autocommit=True)
    def _init(self):
        with self._connect() as c:c.execute("""CREATE TABLE IF NOT EXISTS cluster_locks(cluster_key text PRIMARY KEY, thread_id text UNIQUE NOT NULL, acquired_at timestamptz NOT NULL, expires_at timestamptz NOT NULL)""")
    def acquire(self,cluster_key,thread_id):
        now=datetime.now(timezone.utc); exp=now+timedelta(minutes=get_settings().cluster_lock_ttl_minutes)
        with self._connect() as c:
            with c.transaction():
                c.execute('DELETE FROM cluster_locks WHERE expires_at <= %s',(now,))
                try:c.execute('INSERT INTO cluster_locks VALUES (%s,%s,%s,%s)',(cluster_key,thread_id,now,exp))
                except psycopg.errors.UniqueViolation as exc:raise ClusterLockConflict(f'Cluster already has an active workflow: {cluster_key}') from exc
    def refresh(self,thread_id):
        exp=datetime.now(timezone.utc)+timedelta(minutes=get_settings().cluster_lock_ttl_minutes)
        with self._connect() as c:c.execute('UPDATE cluster_locks SET expires_at=%s WHERE thread_id=%s',(exp,thread_id))
    def release(self,thread_id):
        with self._connect() as c:c.execute('DELETE FROM cluster_locks WHERE thread_id=%s',(thread_id,))
    def get_cluster_key(self,thread_id):
        with self._connect() as c:
            row=c.execute('SELECT cluster_key FROM cluster_locks WHERE thread_id=%s',(thread_id,)).fetchone(); return row[0] if row else None
