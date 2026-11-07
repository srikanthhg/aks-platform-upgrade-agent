from __future__ import annotations

import signal
import time
import traceback

from config import get_settings
from graph.checkpointer import create_checkpointer
from graph.workflow import build_workflow
from services.job_queue import JobQueue
from services.locks import ClusterLockStore
from services.workflow_service import WorkflowService
from tools.logger import logger

running = True


def stop(*_):
    global running
    running = False


def main():
    global running
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    settings = get_settings()
    queue = JobQueue(settings.database_url)
    lock_store = ClusterLockStore(settings.database_url)
    connection = None
    try:
        queue.initialize()
        lock_store.initialize()
        connection, checkpointer = create_checkpointer(settings.database_url)
        graph = build_workflow(checkpointer)
        service = WorkflowService(graph=graph, lock_store=lock_store, queue=queue)
        logger.info('Workflow worker started; PostgreSQL dependencies initialized')

        while running:
            job = queue.claim(
                lease_minutes=max(30, settings.upgrade_timeout_seconds // 60 + 30)
            )
            if not job:
                time.sleep(2)
                continue
            try:
                service.execute_job(job)
                queue.complete(job['id'])
            except Exception as exc:
                logger.error(
                    'Workflow job %s failed: %s\\n%s',
                    job['id'], exc, traceback.format_exc(),
                )
                service.fail_job(job, str(exc))
                queue.fail(job['id'], str(exc), retry=False)
    finally:
        if connection is not None:
            connection.close()
        logger.info('Workflow worker stopped')


if __name__ == '__main__':
    main()
