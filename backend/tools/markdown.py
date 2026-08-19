from __future__ import annotations
import json,uuid
from datetime import datetime,timezone
from typing import Any
import psycopg
from psycopg.rows import dict_row
from config import get_settings
class MarkdownReportWriter:
    def __init__(self):
        self.database_url=get_settings().database_url
        with psycopg.connect(self.database_url,autocommit=True) as c:c.execute("""CREATE TABLE IF NOT EXISTS workflow_reports(id uuid PRIMARY KEY,thread_id text NOT NULL,stage text NOT NULL,filename text NOT NULL,content text NOT NULL,created_at timestamptz NOT NULL,UNIQUE(thread_id,stage))""")
    def create(self,state:dict[str,Any],stage:str)->dict[str,Any]:
        cluster=state.get('cluster',{});validation=state.get('validation',{});upgrade=state.get('upgrade',{});name=cluster.get('cluster_name','unknown');thread_id=state.get('workflow',{}).get('thread_id','unknown');now=datetime.now(timezone.utc);content='\n'.join([f'# AKS {stage} Report','',f'Generated: {now.isoformat()}',f'- Cluster: `{name}`',f'- Validation: **{validation.get("status","UNKNOWN")}**',f'- Upgrade: **{upgrade.get("status","NOT_STARTED")}**','```json',json.dumps(state,indent=2,default=str),'```']);report_id=str(uuid.uuid4());filename=f'{name}-{stage}.md'
        with psycopg.connect(self.database_url,autocommit=True) as c:row=c.execute("""INSERT INTO workflow_reports(id,thread_id,stage,filename,content,created_at) VALUES(%s,%s,%s,%s,%s,%s) ON CONFLICT(thread_id,stage) DO UPDATE SET filename=excluded.filename,content=excluded.content,created_at=excluded.created_at RETURNING id""",(report_id,thread_id,stage,filename,content,now)).fetchone()
        return {'id':str(row[0]),'stage':stage,'filename':filename,'created_at':now.isoformat()}
def get_report(thread_id:str,stage:str)->dict[str,Any]|None:
    with psycopg.connect(get_settings().database_url,row_factory=dict_row) as c:
        row=c.execute('SELECT id,thread_id,stage,filename,content,created_at FROM workflow_reports WHERE thread_id=%s AND stage=%s',(thread_id,stage)).fetchone();return dict(row) if row else None
