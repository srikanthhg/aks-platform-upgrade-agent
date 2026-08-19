from __future__ import annotations
from typing import Any
import requests
from config import get_settings
from tools.logger import logger
class TeamsNotifier:
    def send(self,title:str,message:str,facts:dict[str,Any])->dict[str,Any]:
        settings=get_settings()
        if not settings.teams_notifications_enabled:return {'sent':False,'skipped':True,'reason':'disabled'}
        if not settings.teams_webhook_url:return {'sent':False,'skipped':False,'error':'Webhook URL missing'}
        lines='\n'.join(f'- **{k}:** {v}' for k,v in facts.items())
        try:response=requests.post(settings.teams_webhook_url,json={'text':f'## {title}\n\n{message}\n\n{lines}'},timeout=20)
        except requests.RequestException as exc:logger.exception('Teams notification failed');return {'sent':False,'skipped':False,'error':str(exc)}
        if not 200<=response.status_code<300:return {'sent':False,'status_code':response.status_code,'error':response.text[:2000]}
        return {'sent':True,'status_code':response.status_code}
