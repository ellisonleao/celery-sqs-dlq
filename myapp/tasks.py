from celery import Task
from celery.exceptions import Reject

from celery_sqs_dlq.celery import app


def dlq_task(**kwargs):
    retry_kwargs = kwargs.get("retry_kwargs", {})
    exceptions = kwargs.get("exceptions", ())

    def wraps(f):
        def zas(self, *args , **kwargs):
            try:
                print("self", self)
                return f(*args , **kwargs)
            except exceptions as exc:
                print("expected exceptions", exc)
                print("retries", self.request.retries)
                print("self.max_retries", self.max_retries)

                if self.request.retries >= self.max_retries:
                    print("rejecting due to max retries", exc)
                    raise Reject(str(exc), requeue=True)
                raise exc
            except Exception as exc:
                print("rejecting unexpected exception", exc)
                raise Reject(str(exc), requeue=False)

        return app.task(retry_kwargs=retry_kwargs, autoretry_for=exceptions, bind=True)(zas)

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
