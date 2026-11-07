from __future__ import annotations

import argparse
import json

from config import get_settings
from graph.checkpointer import create_checkpointer
from graph.workflow import build_workflow
from services.job_queue import JobQueue
from services.locks import ClusterLockStore
from services.workflow_service import WorkflowService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resource-group')
    parser.add_argument('--cluster-name')
    parser.add_argument('--target-version')
    parser.add_argument('--thread-id')
    parser.add_argument('--approve', action='store_true')
    parser.add_argument('--reject', action='store_true')
    parser.add_argument('--operator', default='cli-user')
    args = parser.parse_args()

    settings = get_settings()
    queue = JobQueue(settings.database_url)
    locks = ClusterLockStore(settings.database_url)
    connection = None
    try:
        queue.initialize()
        locks.initialize()
        connection, checkpointer = create_checkpointer(settings.database_url)
        service = WorkflowService(
            graph=build_workflow(checkpointer), lock_store=locks, queue=queue
        )
        if args.approve or args.reject:
            result = service.resume(args.thread_id, args.approve, args.operator, None)
        elif args.thread_id:
            result = service.get(args.thread_id)
        else:
            result = service.start(
                {
                    'resource_group': args.resource_group,
                    'cluster_name': args.cluster_name,
                    'target_version': args.target_version,
                    'dry_run': True,
                    'max_surge': '33%',
                },
                args.operator,
            )
        print(json.dumps(result, indent=2, default=str))
    finally:
        if connection is not None:
            connection.close()


if __name__ == '__main__':
    main()
