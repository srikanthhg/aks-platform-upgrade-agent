from __future__ import annotations
import signal,time,traceback
from config import get_settings
from services.job_queue import JobQueue
from services.workflow_service import WorkflowService
from tools.logger import logger
running=True
def stop(*_):
    global running;running=False
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
settings=get_settings();queue=JobQueue();service=WorkflowService(queue=queue);logger.info('Workflow worker started')
while running:
    job=queue.claim(lease_minutes=max(30,settings.upgrade_timeout_seconds//60+30))
    if not job:time.sleep(2);continue
    try:service.execute_job(job);queue.complete(job['id'])
    except Exception as exc:logger.error('Workflow job %s failed: %s\n%s',job['id'],exc,traceback.format_exc());service.fail_job(job,str(exc));queue.fail(job['id'],str(exc),retry=False)
logger.info('Workflow worker stopped')
