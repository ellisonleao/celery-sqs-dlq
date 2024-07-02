from celery import Task
from celery.exceptions import Reject

from celery_sqs_dlq.celery import app


def dlq_task(**kwargs):
    retry_kwargs = kwargs.get("retry_kwargs", {})
    exceptions = kwargs.get("exceptions", ())

    def wraps(f):
        class SendToDLQTask(Task):
            max_retries = retry_kwargs.get("max_retries", 3)
            default_retry_delay = retry_kwargs.get("countdown", 3)
            acks_late = True
            reject_on_worker_lost = True

            def on_retry(self, exc, task_id, args, kwargs, einfo):
                print(f"RETRY #{self.request.retries}")
                print(f"MAX RETRIES = {self.max_retries}")
                return super().on_retry(exc, task_id, args, kwargs, einfo)

            def on_failure(self, exc, task_id, args, kwargs, einfo):
                print(f"CALLED ON FAILURE WITH EXC={exc}. Rejecting task")
                exc = Reject(exc, requeue=False)
                return super().on_failure(exc, task_id, args, kwargs, einfo)

        return app.task(base=SendToDLQTask, autoretry_for=exceptions)(f)

    return wraps


@dlq_task(exceptions=(ZeroDivisionError,), retry_kwargs={"countdown": 1})
def should_retry():
    print("should raise zerodivision error, should retry until max retries")
    return 1 / 0


@dlq_task()
def should_not_retry():
    print("will raise unhandled exception, should not retry")
    raise Exception("unhandled exception")


@app.task(acks_late=True)
def send_to_dlq_task():
    try:
        return 1 / 0
    except Exception as exc:
        raise Reject(str(exc), requeue=False)
