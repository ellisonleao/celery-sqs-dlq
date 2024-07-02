Celery SQS + DLQ
================

This project shows how to use a django project with Celery using SQS as broker with a DLQ configured

## Prerequisites

- Docker compose


## Calling task

1. Run worker

```bash
$ celery -A celery_sqs_dlq worker -Q test-queue.fifo
```

2. Call any tasks from myapp.tasks
